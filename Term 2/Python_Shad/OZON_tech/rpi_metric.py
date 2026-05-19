import importlib
import importlib.util
import subprocess
import sys
import numpy as np
import polars as pl
if importlib.util.find_spec('polars') is None:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'polars'])


from pathlib import Path
# Устанавливаем зависимости
for pkg in ['polars', 'sentence-transformers']:
    if importlib.util.find_spec(pkg.replace('-', '_')) is None:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

# Устанавливаем все зависимости
for pkg, import_name in [
    ('polars',               'polars'),
    ('sentence-transformers', 'sentence_transformers'),
    ('numpy',                'numpy'),
    ('torch',                'torch'),  # sentence-transformers требует torch
]:
    if importlib.util.find_spec(import_name) is None:
        print(f"Устанавливаем {pkg}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
    else:
        print(f"{pkg} уже установлен")

from sentence_transformers import SentenceTransformer
day = '2024-03-01'
base_path = Path('.')
day_path = base_path / 'user_actions_3_months' / f'date={day}'

print(day_path)
parts = []
for parquet_file in day_path.glob('action_type=*/*.parquet'):
    part = pl.read_parquet(parquet_file).with_columns(
        pl.lit(parquet_file.parent.name.replace('action_type=', '')).alias('action_type_folder')
    )
    parts.append(part)

df = pl.concat(parts)


# ============================================================
# КОНСТАНТЫ
# ============================================================

CONVERSION_ACTIONS    = {"to_cart", "to_favorite"}
SESSION_TIMEOUT_MIN   = 15
MIN_REFORMULATIONS    = 3    # минимум переформулировок для надёжной оценки RPI
EMBEDDING_MODEL       = 'intfloat/multilingual-e5-small'  # хорошо работает с русским


# ============================================================
# ШАГ 1: Выделяем все поисковые события, сортируем по времени
# ============================================================

def get_search_events(df: pl.DataFrame) -> pl.DataFrame:
    """
    Берём все события search с непустым запросом.
    Каждая строка = один поисковый запрос пользователя.
    """
    return (
        df
        .filter(
            (pl.col("action_type") == "search") &
            pl.col("search_query").is_not_null()
        )
        .select(["user_id", "search_query", "timestamp"])
        .sort(["user_id", "timestamp"])
    )


# ============================================================
# ШАГ 2: Выделяем конверсионные события
# ============================================================

def get_conversions(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .filter(pl.col("action_type").is_in(CONVERSION_ACTIONS))
        .select([
            "user_id",
            pl.col("timestamp").alias("conv_ts"),
        ])
    )


# ============================================================
# ШАГ 3: Находим переформулировки
#
# Переформулировка — это когда:
#   1. Пользователь ввёл запрос q
#   2. НЕ было конверсии до следующего запроса
#   3. Следующий запрос q' был введён в пределах SESSION_TIMEOUT_MIN
#
# Результат: таблица пар (q, q') — исходный и новый запрос
# ============================================================

def find_reformulations(
    search_events: pl.DataFrame,
    conversions: pl.DataFrame,
    session_timeout_min: int = SESSION_TIMEOUT_MIN,
) -> pl.DataFrame:
    """
    Для каждого поискового события смотрим:
    - какой следующий запрос сделал тот же пользователь
    - был ли он в пределах таймаута (= та же сессия)
    - не было ли конверсии между двумя запросами
    """

    # Добавляем следующий запрос и его timestamp для того же пользователя
    with_next = (
        search_events
        .with_columns([
            pl.col("search_query")
              .shift(-1)
              .over("user_id")
              .alias("next_query"),
            pl.col("timestamp")
              .shift(-1)
              .over("user_id")
              .alias("next_ts"),
        ])
        # Убираем последний запрос пользователя (нет следующего)
        .filter(pl.col("next_query").is_not_null())
        # Убираем пары где следующий запрос за пределами таймаута
        .filter(
            (pl.col("next_ts") - pl.col("timestamp"))
            .dt.total_minutes() <= session_timeout_min
        )
        # Убираем пары где запрос не изменился (пользователь повторил тот же запрос)
        .filter(pl.col("search_query") != pl.col("next_query"))
        .rename({"timestamp": "query_ts"})
    )

    # Проверяем: была ли конверсия между query_ts и next_ts?
    # Джойним конверсии по user_id и смотрим попадает ли conv_ts в окно
    with_conv_check = (
        with_next
        .join(conversions, on="user_id", how="left")
        .with_columns(
            # Конверсия валидна если произошла между двумя запросами
            pl.when(
                pl.col("conv_ts").is_not_null() &
                (pl.col("conv_ts") > pl.col("query_ts")) &
                (pl.col("conv_ts") < pl.col("next_ts"))
            )
            .then(True)
            .otherwise(False)
            .alias("has_conversion_between")
        )
        .group_by(["user_id", "search_query", "query_ts", "next_query", "next_ts"])
        .agg(
            pl.col("has_conversion_between").any().alias("had_conversion")
        )
        # Оставляем только переформулировки БЕЗ конверсии между ними
        .filter(pl.col("had_conversion") == False)
        .select(["search_query", "next_query"])
    )

    return with_conv_check


# ============================================================
# ШАГ 4: Считаем косинусное сходство через эмбеддинги
# ============================================================

def cosine_similarity_matrix(
    vecs_a: np.ndarray,
    vecs_b: np.ndarray,
) -> np.ndarray:
    """
    Побатчевое косинусное сходство между парами векторов.
    vecs_a[i] сравнивается с vecs_b[i].
    normalize_embeddings=True в encode() уже нормирует длины →
    косинусное сходство = скалярное произведение.
    """
    return np.sum(vecs_a * vecs_b, axis=1)


def compute_similarities(
    reformulations: pl.DataFrame,
    model: SentenceTransformer,
) -> pl.DataFrame:
    """
    Для каждой пары (search_query, next_query) считаем
    косинусное сходство эмбеддингов.
    """
    queries_orig = reformulations["search_query"].to_list()
    queries_new  = reformulations["next_query"].to_list()

    # Уникальные запросы для экономии вычислений
    all_unique_queries = list(set(queries_orig + queries_new))

    print(f"Считаем эмбеддинги для {len(all_unique_queries)} уникальных запросов...")
    embeddings_map = {
        q: emb for q, emb in zip(
            all_unique_queries,
            model.encode(all_unique_queries, normalize_embeddings=True, show_progress_bar=True)
        )
    }

    # Считаем сходство для каждой пары
    sims = []
    for q_orig, q_new in zip(queries_orig, queries_new):
        vec_a = embeddings_map[q_orig]
        vec_b = embeddings_map[q_new]
        sim   = float(np.dot(vec_a, vec_b))  # = косинус т.к. векторы нормированы
        sims.append(sim)

    return reformulations.with_columns(
        pl.Series("similarity", sims)
    )


# ============================================================
# ШАГ 5: Агрегируем RPI по каждому запросу
# ============================================================

def compute_rpi(
    reformulations_with_sim: pl.DataFrame,
    min_reformulations: int = MIN_REFORMULATIONS,
) -> pl.DataFrame:
    """
    RPI(q) = 1 - mean(sim(q, q'_r) for r in R_q)

    Чем выше RPI — тем сильнее пользователи "убегают" от запроса q,
    тем хуже качество выдачи.
    """
    return (
        reformulations_with_sim
        .group_by("search_query")
        .agg([
            pl.col("similarity").mean().alias("avg_similarity"),
            pl.col("similarity").std().alias("std_similarity"),
            pl.len().alias("n_reformulations"),

            # Топ-3 самые частые переформулировки (для интерпретации)
            pl.col("next_query").alias("reformulation_examples"),
        ])
        .with_columns(
            # Сама метрика RPI
            (1 - pl.col("avg_similarity")).alias("rpi"),
        )
        .filter(pl.col("n_reformulations") >= min_reformulations)
        .sort("rpi", descending=True)
        .select([
            "search_query",
            "rpi",
            "avg_similarity",
            "std_similarity",
            "n_reformulations",
            "reformulation_examples",
        ])
    )


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ — полный пайплайн
# ============================================================

def calculate_rpi_pipeline(
    df: pl.DataFrame,
    session_timeout_min: int = SESSION_TIMEOUT_MIN,
    min_reformulations: int = MIN_REFORMULATIONS,
    embedding_model_name: str = EMBEDDING_MODEL,
) -> pl.DataFrame:

    print("Шаг 1: Извлекаем поисковые события...")
    search_events = get_search_events(df)
    print(f"  → {len(search_events)} поисковых событий")

    print("Шаг 2: Извлекаем конверсии...")
    conversions = get_conversions(df)
    print(f"  → {len(conversions)} конверсий")

    print("Шаг 3: Находим переформулировки...")
    reformulations = find_reformulations(search_events, conversions, session_timeout_min)
    print(f"  → {len(reformulations)} переформулировок")

    print("Шаг 4: Загружаем модель эмбеддингов...")
    model = SentenceTransformer(embedding_model_name)

    print("Шаг 5: Считаем косинусные сходства...")
    reformulations_with_sim = compute_similarities(reformulations, model)

    print("Шаг 6: Агрегируем RPI по запросам...")
    result = compute_rpi(reformulations_with_sim, min_reformulations)

    return result


# ============================================================
# ЗАПУСК + ИНТЕРПРЕТАЦИЯ
# ============================================================

result = calculate_rpi_pipeline(df)

print("\n=== Запросы с ВЫСОКИМ RPI (плохая выдача, пользователи убегают) ===")
print(result.head(10))

print("\n=== Запросы с НИЗКИМ RPI (хорошая выдача, пользователи остаются) ===")
print(result.sort("rpi", descending=False).head(10))

# Распределение RPI
print("\n=== Распределение RPI ===")
print(result.select([
    pl.col("rpi").mean().alias("mean_rpi"),
    pl.col("rpi").median().alias("median_rpi"),
    pl.col("rpi").quantile(0.25).alias("p25_rpi"),
    pl.col("rpi").quantile(0.75).alias("p75_rpi"),
]))
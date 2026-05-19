import importlib.util
import subprocess
import sys

if importlib.util.find_spec('polars') is None:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'polars'])

import polars as pl
from pathlib import Path
day = '2024-03-01'
base_path = Path('.')
day_path = base_path / 'user_actions' / 'user_actions_3_months' / f'date={day}'

print(day_path)
parts = []
for parquet_file in day_path.glob('action_type=*/*.parquet'):
    part = pl.read_parquet(parquet_file).with_columns(
        pl.lit(parquet_file.parent.name.replace('action_type=', '')).alias('action_type_folder')
    )
    parts.append(part)

df = pl.concat(parts)




#------------------------------Таблица (время от поиска до конверсиии) - значение LAMBDA----------------
'''
2-5 минут - 0.14-0.35
5-15 минут - 0.05-0.14
15-40 минут - 0.02-0.05
60-180 минут - 0.004 - 0.02
'''
#----------------------------------------------

# ============================================================
# КОНСТАНТЫ
# ============================================================

# За конверсионные действия мы считаем (to_cart, favourite)
LAMBDA = 0.02            # среднее время от момента поиска до конверсии - 14 минут
SESSION_TIMEOUT_MINUTES = 30 # сессия закрывается если после search нет активности
CONVERSION_ACTIONS = {"to_cart", "to_favorite"}
MIN_SESSIONS = 5             # минимум сессий для включения запроса в результат


# ============================================================
# ШАГ 1: Старт сессии — событие search
# ============================================================

def get_search_starts(df: pl.DataFrame) -> pl.DataFrame:
    """
    Старт сессии = момент когда пользователь ввёл поисковый запрос.
    Одна строка = одна поисковая сессия.
    Если пользователь ввёл один и тот же запрос несколько раз —
    каждый раз считается отдельной сессией.
    """
    return (
        df
        .filter(
            (pl.col("action_type") == "search") &
            pl.col("search_query").is_not_null()
        )
        .select([
            "user_id",
            "search_query",
            pl.col("timestamp").alias("search_ts"),
        ])
        .sort(["user_id", "search_ts"])
    )


# ============================================================
# ШАГ 2: Конверсионные события
# ============================================================

def get_conversions(df: pl.DataFrame) -> pl.DataFrame:
    """
    Конверсия = add_to_cart или add_to_favorite.
    item_id сохраняем для диагностики, на логику не влияет.
    """
    return (
        df
        .filter(pl.col("action_type").is_in(CONVERSION_ACTIONS))
        .select([
            "user_id",
            "item_id",
            pl.col("timestamp").alias("conv_ts"),
            pl.col("action_type").alias("conv_action"),
        ])
    )


# ============================================================
# ШАГ 3: Определяем границы каждой сессии и джойним конверсии
# ============================================================

def build_sessions(
    search_starts: pl.DataFrame,
    conversions: pl.DataFrame,
    session_timeout_minutes: int = SESSION_TIMEOUT_MINUTES,
) -> pl.DataFrame:
    """
    Границы сессии:
    - начало: search_ts
    - конец:  следующий search_ts того же пользователя
              ИЛИ search_ts + session_timeout если следующего нет

    Конверсия засчитывается если попала в окно (search_ts, session_end_ts].
    Берём первую конверсию в окне — она даёт минимальный delta_t.
    """

    # --- Определяем конец каждой сессии ---
    sessions_with_bounds = (
        search_starts
        .with_columns(
            # Следующий поиск того же пользователя
            pl.col("search_ts")
              .shift(-1)
              .over("user_id")
              .alias("next_search_ts")
        )
        .with_columns(
            # Конец сессии = следующий поиск если он в пределах таймаута,
            # иначе search_ts + таймаут
            pl.when(
                pl.col("next_search_ts").is_not_null() &
                (
                    (pl.col("next_search_ts") - pl.col("search_ts"))
                    .dt.total_minutes()
                    <= session_timeout_minutes
                )
            )
            .then(pl.col("next_search_ts"))
            .otherwise(
                pl.col("search_ts") +
                pl.duration(minutes=session_timeout_minutes)
            )
            .alias("session_end_ts")
        )
    )

    # --- Джойним конверсии по user_id и фильтруем по временному окну ---
    sessions_with_convs = (
        sessions_with_bounds
        .join(conversions, on="user_id", how="left")
        .with_columns(
            # Конверсия валидна только если попала внутрь окна сессии
            pl.when(
                pl.col("conv_ts").is_not_null() &
                (pl.col("conv_ts") > pl.col("search_ts")) &
                (pl.col("conv_ts") <= pl.col("session_end_ts"))
            )
            .then(pl.col("conv_ts"))
            .otherwise(None)
            .alias("conv_ts_valid")
        )
        # Для каждой сессии берём самую раннюю конверсию
        .group_by(["user_id", "search_query", "search_ts", "session_end_ts"])
        .agg(
            pl.col("conv_ts_valid").min().alias("first_conv_ts"),
        )
    )

    return sessions_with_convs


# ============================================================
# ШАГ 4: Считаем delta_t и дискаунтированный вес
# ============================================================

def compute_discounted_weight(
    sessions: pl.DataFrame,
    lambda_: float = LAMBDA,
) -> pl.DataFrame:
    """
    Добавляем колонки:
    - converted:   bool, была ли конверсия в сессии
    - delta_t_min: минуты от search_ts до первой конверсии
    - weight:      e^(-lambda * delta_t) если конверсия есть, иначе 0

    Сессии без конверсии получают weight=0 и остаются в данных —
    они важны для знаменателя TDCR.
    """
    return (
        sessions
        .with_columns(
            pl.col("first_conv_ts").is_not_null().alias("converted"),
        )
        .with_columns(
            pl.when(pl.col("converted"))
              .then(
                  (pl.col("first_conv_ts") - pl.col("search_ts"))
                  .dt.total_seconds() / 60.0
              )
              .otherwise(None)
              .alias("delta_t_min")
        )
        .with_columns(
            pl.when(pl.col("converted"))
              .then((-lambda_ * pl.col("delta_t_min")).exp())
              .otherwise(pl.lit(0.0))
              .alias("weight")
        )
    )


# ============================================================
# ШАГ 5: Агрегируем TDCR по каждому запросу
# ============================================================

def compute_tdcr(
    weighted_sessions: pl.DataFrame,
    min_sessions: int = MIN_SESSIONS,
) -> pl.DataFrame:
    """
    TDCR(q) = sum(weight_s for s in S_q) / |S_q|

    Дополнительно считаем ACR для сравнения — он показывает
    насколько TDCR штрафует запросы за медленные конверсии.

    min_sessions — фильтр надёжности: запросы с малым числом
    сессий дают нестабильную оценку.
    """
    return (
        weighted_sessions
        .group_by("search_query")
        .agg([
            pl.col("weight").sum().alias("sum_weights"),
            pl.len().alias("n_sessions"),
            pl.col("converted").sum().alias("n_converted"),
            pl.col("delta_t_min").mean().alias("avg_delta_t_min"),
        ])
        .with_columns([
            # Основная метрика
            (pl.col("sum_weights") / pl.col("n_sessions"))
              .alias("tdcr"),
            # Обычный ACR для сравнения
            (pl.col("n_converted") / pl.col("n_sessions"))
              .alias("acr"),
        ])
        .with_columns(
            # Разница ACR - TDCR: насколько конверсии были "медленными"
            (pl.col("acr") - pl.col("tdcr")).alias("slowness_penalty")
        )
        .filter(pl.col("n_sessions") >= min_sessions)
        .sort("tdcr", descending=True)
        .select([
            "search_query",
            "tdcr",
            "acr",
            "slowness_penalty",
            "n_sessions",
            "n_converted",
            "avg_delta_t_min",
        ])
    )


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ — полный пайплайн
# ============================================================

def calculate_tdcr_pipeline(
    df: pl.DataFrame,
    lambda_: float = LAMBDA,
    session_timeout_minutes: int = SESSION_TIMEOUT_MINUTES,
    min_sessions: int = MIN_SESSIONS,
) -> pl.DataFrame:
    """
    Полный пайплайн: сырой датафрейм → TDCR по каждому запросу.

    Параметры:
        lambda_                 — скорость дискаунтирования (чем больше,
                                  тем сильнее штраф за медленную конверсию)
        session_timeout_minutes — максимальная длина сессии в минутах
        min_sessions            — минимум сессий для включения запроса
    """
    search_starts = get_search_starts(df)
    conversions   = get_conversions(df)
    sessions      = build_sessions(search_starts, conversions, session_timeout_minutes)
    weighted      = compute_discounted_weight(sessions, lambda_=lambda_)
    result        = compute_tdcr(weighted, min_sessions=min_sessions)
    return result


# ============================================================
# ДИАГНОСТИКА — полезно запустить перед основным пайплайном
# ============================================================

def diagnose(df: pl.DataFrame) -> None:
    print("=== Типы действий ===")
    print(df["action_type"].value_counts().sort("count", descending=True))
    print("\n=== action_type_folder ===")
    print(df["action_type_folder"].value_counts().sort("count", descending=True))
    print(f"\n=== Всего строк: {len(df)} ===")
    print(f"=== Уникальных пользователей: {df['user_id'].n_unique()} ===")
    print(f"=== Уникальных запросов: {df['search_query'].n_unique()} ===")


# ============================================================
# ЗАПУСК
# ============================================================

#diagnose(df)

result = calculate_tdcr_pipeline(
    df,
    lambda_=0.05,
    session_timeout_minutes=30,
    min_sessions=5,
)

print("\n=== Топ-50 запросов по TDCR ===")
print(result.head(50))

print("\n=== 50 запросов из середины списка ===")
mid = len(result) // 10
df_mid = result[mid - 25 : mid + 25]
print(df_mid)
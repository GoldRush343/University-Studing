"""
=============================================================================
SEARCH QUALITY INDEX (SQI) ANALYZER
=============================================================================
Проект для автоматической оценки качества поискового движка на основе 
поведенческих факторов (Reverse Engineering of User Behavior).

Алгоритм оценивает каждый поисковый запрос по 5-ти математическим гипотезам,
используя Байесовское сглаживание и нелинейные функции (логарифмы, экспоненты),
чтобы сформировать итоговый балл (от 0 до 100).

5 ГИПОТЕЗ КАЧЕСТВА:
1. Текст (score_text): Доля пользователей, не бросивших выдачу (Penetration Rate).
2. Ранжирование (score_rank): Конверсия из просмотра карточки в корзину.
3. Интент/NER (score_ner): Усталость юзера (просмотры на 1 пользователя).
4. Спам (score_spam): Расфокус выдачи (покупки на уникальный товар).
5. Разнообразие (score_div): Иллюзия выбора (купленные товары / просмотренные товары).
=============================================================================
"""

import importlib.util
import subprocess
import sys
import os

# --- 0. АВТО-УСТАНОВКА ЗАВИСИМОСТЕЙ ---
required_packages = ['seaborn', 'matplotlib', 'polars', 'pyarrow']
for package in required_packages:
    if importlib.util.find_spec(package) is None:
        print(f"📦 Установка недостающей библиотеки: {package}...")
        subprocess.call([sys.executable, '-m', 'pip', 'install', package])

import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Создаем директорию для артефактов
os.makedirs('images', exist_ok=True)

def load_and_clean_data(base_path_str: str, day: str) -> pl.DataFrame:
    """
    [ШАГ 1] Загрузка логов, удаление ботов и нормализация текста.
    """
    print(f"\n[1/3] Загрузка и очистка данных за {day}...")
    base_path = Path(base_path_str)
    day_path = base_path / 'user_actions' / 'user_actions_3_months' / f'date={day}'
    
    if not day_path.exists():
        raise FileNotFoundError(f"Критическая ошибка: Путь {day_path} не найден!")
        
    parts = []
    for parquet_file in day_path.glob('action_type=*/*.parquet'):
        part = pl.read_parquet(parquet_file)
        parts.append(part)
        
    df = pl.concat(parts)
    
    # Очистка данных
    df = df.filter(pl.col('user_id') != 6195822) # Фильтр системного бота
    df = df.filter(pl.col('search_query').is_not_null())
    
    # Текстовая нормализация
    df = df.with_columns([
        pl.col('search_query').str.to_lowercase().str.strip_chars().alias('search_query'),
        (pl.col('search_query').str.count_matches(' ') + 1).alias('word_count')
    ])
    return df

def calculate_quality_scores(df: pl.DataFrame) -> pl.DataFrame:
    """
    [ШАГ 2] Математический движок. Расчет 5 гипотез с использованием
    сглаживания Лапласа и экспоненциального/логарифмического затухания.
    """
    print("[2/3] Расчет матрицы качества (Bayesian Smoothing + Non-linear decay)...")
    
    # 2.1 Агрегация базовых метрик
    stats = df.group_by('search_query').agg([
        pl.col('word_count').first().alias('word_count'),
        (pl.col('action_type') == 'search').sum().alias('n_searches'),
        pl.col('action_type').filter(pl.col('action_type').is_in(['view', 'click'])).count().alias('n_views'),
        (pl.col('action_type') == 'to_cart').sum().alias('n_carts'),
        
        pl.col('user_id').filter(pl.col('action_type') == 'search').n_unique().alias('u_searchers'),
        pl.col('user_id').filter(pl.col('action_type').is_in(['view', 'click'])).n_unique().alias('u_viewers'),
        
        pl.col('item_id').filter(pl.col('action_type').is_in(['view', 'click'])).n_unique().alias('i_unique_viewed'),
        pl.col('item_id').filter(pl.col('action_type') == 'to_cart').n_unique().alias('i_unique_carts')
    ]).filter(pl.col('n_searches') >= 30) # Отсекаем редкие запросы для стат. значимости

    # 2.2 Сглаживание Лапласа (Добавление априорных псевдо-наблюдений)
    stats = stats.with_columns([
        ((pl.col('u_viewers') + 1) / (pl.col('u_searchers') + 2)).alias('smooth_penetration'),
        ((pl.col('n_carts') + 1) / (pl.col('n_views') + 10)).alias('smooth_cart_per_view'),
        ((pl.col('n_views') + 3) / (pl.col('u_viewers') + 1)).alias('smooth_views_per_user'),
        ((pl.col('n_carts') + 1) / (pl.col('i_unique_viewed') + 5)).alias('smooth_cart_per_item'),
        ((pl.col('i_unique_carts') + 1) / (pl.col('i_unique_viewed') + 2)).alias('smooth_diversity')
    ])

    # 2.3 Вычисление суб-индексов (все от 0.0 до 1.0)
    scores = stats.with_columns([
        # ТЕКСТ: Идеально, если > 80% юзеров кликают после поиска (нет пустых экранов)
        pl.when(pl.col('smooth_penetration') >= 0.8).then(1.0)
          .otherwise(pl.col('smooth_penetration') / 0.8).alias('score_text'),
        
        # РАНЖИРОВАНИЕ: Экспоненциальный рост от конверсии корзины
        (1.0 - (-20.0 * pl.col('smooth_cart_per_view')).exp()).alias('score_rank'),
        
        # ИНТЕНТ (NER): Логарифмический штраф за долгое листание
        (1.0 / (pl.col('smooth_views_per_user') + 1).log(2)).alias('score_ner'),
          
        # СПАМ: Штраф за расфокусировку (мало покупок на множество уникальных товаров)
        (1.0 - (-10.0 * pl.col('smooth_cart_per_item')).exp()).alias('score_spam'),

        # РАЗНООБРАЗИЕ: Штраф за "иллюзию выбора" (люди смотрят сотни товаров, но берут один и тот же)
        pl.when((pl.col('smooth_diversity') * 10) > 1.0).then(1.0)
          .otherwise(pl.col('smooth_diversity') * 10).alias('score_div')
    ])

    # 2.4 ИТОГОВЫЙ ИНДЕКС (Веса по 20% на каждую гипотезу, масштаб 100)
    scores = scores.with_columns([
        (
            (pl.col('score_text') * 0.2 + 
             pl.col('score_rank') * 0.2 + 
             pl.col('score_ner') * 0.2 + 
             pl.col('score_spam') * 0.2 + 
             pl.col('score_div') * 0.2) * 100
        ).round(1).alias('TOTAL_QUALITY_SCORE')
    ]).sort('TOTAL_QUALITY_SCORE', descending=True)

    return scores

def generate_report_and_plots(scores_df: pl.DataFrame):
    """
    [ШАГ 3] Визуализация и генерация отчетов.
    """
    print("[3/3] Генерация отчетов и графиков...")
    
    # Экспорт в CSV для менеджеров
    scores_df.write_csv('search_quality_report.csv')
    
    pandas_df = scores_df.to_pandas()

    # --- График 1: Би-модальное распределение качества ---
    plt.figure(figsize=(10, 5))
    sns.histplot(data=pandas_df, x='TOTAL_QUALITY_SCORE', bins=40, color='purple', kde=True)
    plt.axvline(x=50, color='red', linestyle='--', label='Зона провала (<50)')
    plt.title('Индекс Качества Поиска: Глобальное Распределение')
    plt.xlabel('Итоговый балл (0 - Ужасно, 100 - Идеально)')
    plt.ylabel('Количество поисковых запросов')
    plt.legend()
    plt.savefig('images/quality_score_distribution.png')
    plt.close()

    # --- График 2: Деградация по длине запроса ---
    length_quality = scores_df.group_by('word_count').agg(
        pl.col('TOTAL_QUALITY_SCORE').mean().alias('avg_score')
    ).filter(pl.col('word_count') <= 7).sort('word_count')
    
    plt.figure(figsize=(10, 5))
    sns.barplot(data=length_quality.to_pandas(), x='word_count', y='avg_score', color='goldenrod')
    plt.ylim(0, 100)
    plt.title('Деградация качества поиска при усложнении запроса')
    plt.xlabel('Длина поискового запроса (кол-во слов)')
    plt.ylabel('Средний балл качества (TQS)')
    plt.savefig('images/quality_degradation_by_length.png')
    plt.close()

    # --- CLI ВЫВОД (Интерфейс пользователя) ---
    
    print("\n" + "="*85)
    print(" РЕЙТИНГ: ТОП-10 ЛУЧШИХ ЗАПРОСОВ (Идеальная работа поисковика)")
    print("="*85)
    # Сортировка по убыванию (descending=True)
    best = scores_df.filter(pl.col('n_searches') > 100).sort('TOTAL_QUALITY_SCORE', descending=True).head(10)
    print(best.select([
        'search_query', 'word_count', 'TOTAL_QUALITY_SCORE', 
        'score_text', 'score_rank', 'score_ner', 'score_div'
    ]))

    print("\n" + "="*85)
    print(" АНТИ-РЕЙТИНГ: ТОП-10 ХУДШИХ ЗАПРОСОВ (Требуют исправления ранжирования)")
    print("="*85)
    # Сортировка по возрастанию (descending=False)
    worst = scores_df.filter(pl.col('n_searches') > 100).sort('TOTAL_QUALITY_SCORE').head(10)
    print(worst.select([
        'search_query', 'word_count', 'TOTAL_QUALITY_SCORE', 
        'score_text', 'score_rank', 'score_ner', 'score_div'
    ]))
    
    print("\n" + "="*85)
    print(" МАТРИЦА ПРОБЛЕМ (Как интерпретировать нули в колонках):")
    print(" • score_text -> Поисковик выдал пустой экран / не понял язык.")
    print(" • score_rank -> В топе кликбейт. Люди заходят в карточки, но не покупают.")
    print(" • score_ner  -> Усталость. Люди листают слишком много (поиск не понял интент).")
    print(" • score_spam -> SEO-мусор. Корзины размазаны по куче нерелевантных товаров.")
    print(" • score_div  -> Иллюзия выбора. Смотрят сотни товаров, но берут одни и те же.")
    print("="*85)
    print(" Файл 'search_quality_report.csv' и графики (в папке images/) успешно созданы.\n")

# ==========================================
# ТОЧКА ВХОДА (MAIN)
# ==========================================
if __name__ == "__main__":
    # Настройки директорий
    BASE_PATH = "." 
    TARGET_DAY = "2024-03-01" 

    try:
        # Pipeline исполнения
        raw_df = load_and_clean_data(BASE_PATH, TARGET_DAY)
        scored_df = calculate_quality_scores(raw_df)
        generate_report_and_plots(scored_df)
        
    except Exception as e:
        print(f"\n Произошла ошибка при выполнении: {e}")
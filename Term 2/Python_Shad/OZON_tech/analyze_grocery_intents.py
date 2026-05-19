import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Создаем папку для отчетов
os.makedirs('images', exist_ok=True)

def get_sqi_metrics(df: pl.DataFrame) -> pl.DataFrame:
    """Расчет Технического Качества (5 гипотез)"""
    stats = df.group_by('search_query').agg([
        pl.col('word_count').first(),
        (pl.col('action_type') == 'search').sum().alias('n_searches'),
        pl.col('action_type').filter(pl.col('action_type').is_in(['view', 'click'])).count().alias('n_views'),
        (pl.col('action_type') == 'to_cart').sum().alias('n_carts'),
        pl.col('user_id').filter(pl.col('action_type') == 'search').n_unique().alias('u_searchers'),
        pl.col('user_id').filter(pl.col('action_type').is_in(['view', 'click'])).n_unique().alias('u_viewers'),
        pl.col('item_id').filter(pl.col('action_type').is_in(['view', 'click'])).n_unique().alias('i_unique_viewed'),
        pl.col('item_id').filter(pl.col('action_type') == 'to_cart').n_unique().alias('i_unique_carts')
    ]).filter(pl.col('n_searches') >= 30)

    # Математика затухания
    res = stats.with_columns([
        ((pl.col('u_viewers') + 1) / (pl.col('u_searchers') + 2)).alias('p_pen'),
        ((pl.col('n_carts') + 1) / (pl.col('n_views') + 10)).alias('p_conv'),
        ((pl.col('n_views') + 3) / (pl.col('u_viewers') + 1)).alias('p_fatigue'),
        ((pl.col('n_carts') + 1) / (pl.col('i_unique_viewed') + 5)).alias('p_focus'),
        ((pl.col('i_unique_carts') + 1) / (pl.col('i_unique_viewed') + 2)).alias('p_div')
    ]).with_columns([
        pl.when(pl.col('p_pen') >= 0.8).then(1.0).otherwise(pl.col('p_pen') / 0.8).alias('s_text'),
        (1.0 - (-20.0 * pl.col('p_conv')).exp()).alias('s_rank'),
        (1.0 / (pl.col('p_fatigue') + 1).log(2)).alias('s_ner'),
        (1.0 - (-10.0 * pl.col('p_focus')).exp()).alias('s_spam'),
        pl.when((pl.col('p_div') * 10) > 1.0).then(1.0).otherwise(pl.col('p_div') * 10).alias('s_div')
    ])

    return res.with_columns([
        ((pl.col('s_text') + pl.col('s_rank') + pl.col('s_ner') + pl.col('s_spam') + pl.col('s_div')) / 5 * 100).alias('TECHNICAL_SCORE')
    ]).select(['search_query', 'n_searches', 'n_carts', 'TECHNICAL_SCORE'])
    
def get_grocery_fit_metrics(df: pl.DataFrame) -> pl.DataFrame:
    """Улучшенная верификация классов через концентрацию покупок и длину запроса"""
    
    feat = df.group_by('search_query').agg([
        pl.col('user_id').n_unique().alias('u_users'),
        pl.col('word_count').first().alias('word_count'),
        (pl.col('action_type') == 'view').sum().alias('n_views'),
        (pl.col('action_type') == 'to_cart').sum().alias('n_carts'),
        # Сколько УНИКАЛЬНЫХ товаров было добавлено в корзину всеми юзерами
        pl.col('item_id').filter(pl.col('action_type') == 'to_cart').n_unique().alias('u_cart_items'),
    ]).filter(pl.col('u_users') > 20)

    feat = feat.with_columns([
        (pl.col('n_views') / pl.col('u_users')).alias('vpu'),
        (pl.col('n_carts') / pl.col('u_users')).alias('cpu'),
        # ИНДЕКС ЛОЯЛЬНОСТИ: чем выше, тем больше люди согласны в выборе конкретного товара
        (pl.col('n_carts') / (pl.col('u_cart_items') + 0.1)).alias('loyalty_index')
    ])

    # --- УМНАЯ КЛАССИФИКАЦИЯ ---
    res = feat.with_columns(
        pl.when(pl.col('word_count') >= 3).then(pl.lit("3. Специфичный (Атрибуты)"))
        
        # Если многие покупают одно и то же (высокая концентрация), это рутина
        .when(pl.col('loyalty_index') > 4.5).then(pl.lit("1. Рутина (База)"))
        
        # Если много товаров в корзину на одного юзера - это весовая закупка
        .when(pl.col('cpu') > 1.3).then(pl.lit("4. Закупка (Вес)"))
        
        # Все остальное, где люди смотрят разное и покупают разное - выбор вкуса
        .otherwise(pl.lit("2. Выбор вкуса (Бренды)"))
        .alias('intent_class')
    )

    # --- ПЕРЕСЧЕТ СКОРА ПОД НОВУЮ ЛОГИКУ ---
    res = res.with_columns([
        pl.when(pl.col('intent_class') == "1. Рутина (База)")
        .then(100 - (pl.col('vpu') * 10)) # Штраф за каждый лишний просмотр в базе
        
        .when(pl.col('intent_class') == "3. Специфичный (Атрибуты)")
        .then(100 - (pl.col('vpu') * 5))
        
        .when(pl.col('intent_class') == "4. Закупка (Вес)")
        .then((1 / (pl.col('vpu') / pl.col('cpu') + 1)) * 200) # Отношение просмотров к объему покупки
        
        .otherwise(pl.col('cpu') * 50 + (20 - pl.col('vpu')) * 2) 
        .alias('INTENT_SCORE')
    ])

    return res.with_columns(pl.col('INTENT_SCORE').clip(0, 100)).select(['search_query', 'intent_class', 'INTENT_SCORE', 'loyalty_index'])

def main_analysis():
    # 1. Загрузка
    print("Запуск объединенного анализа...")
    day = '2024-03-01'
    base_path = Path('.')
    day_path = base_path / 'user_actions' / 'user_actions_3_months' / f'date={day}'
    parts = [pl.read_parquet(f) for f in day_path.glob('action_type=*/*.parquet')]
    s = pl.concat(parts).filter(pl.col('user_id') != 6195822).filter(pl.col('search_query').is_not_null())
    s = s.with_columns([
        pl.col('search_query').str.to_lowercase().str.strip_chars().alias('search_query'),
        (pl.col('search_query').str.count_matches(' ') + 1).alias('word_count')
    ])

    # 2. Получение двух скоров
    sqi_df = get_sqi_metrics(s)
    grocery_df = get_grocery_fit_metrics(s)

    # 3. МЕРДЖ И ФИНАЛЬНЫЙ РАСЧЕТ
    final_df = sqi_df.join(grocery_df, on='search_query', how='inner')

    final_df = final_df.with_columns([
        # Средневзвешенный балл
        ((pl.col('TECHNICAL_SCORE') + pl.col('INTENT_SCORE')) / 2).round(1).alias('FINAL_SCORE'),
        # Индекс упущенной выгоды (насколько плох запрос * как часто его ищут)
        ((100 - (pl.col('TECHNICAL_SCORE') + pl.col('INTENT_SCORE')) / 2) * pl.col('n_searches') / 1000).round(2).alias('PRIORITY_LOSS_INDEX')
    ]).sort('PRIORITY_LOSS_INDEX', descending=True)

    # 4. Визуализация: Квадрант Приоритетов
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=final_df.to_pandas(), x='TECHNICAL_SCORE', y='INTENT_SCORE', 
                    size='n_searches', hue='intent_class', alpha=0.5, sizes=(20, 500))
    plt.axvline(60, color='red', linestyle='--')
    plt.axhline(60, color='red', linestyle='--')
    plt.title('Квадрант Качества: Техника vs Продукт (Размер = Частота поиска)')
    plt.xlabel('Техническое качество (SQI)')
    plt.ylabel('Продуктовый интент (Grocery Score)')
    plt.savefig('images/final_priority_quadrant.png')

    # ВЫВОД ТОП-FIX LIST
    print("\n" + "!"*40)
    print("TOP FIX LIST: Эти запросы нужно чинить ПЕРВЫМИ")
    print("!"*40)
    print(final_df.head(15).select(['search_query', 'intent_class', 'FINAL_SCORE', 'PRIORITY_LOSS_INDEX', 'n_searches']))

    final_df.write_csv('final_priority_fix_list.csv')
    print("\nГотово. Ищи 'final_priority_fix_list.csv' и новый график в images/")

if __name__ == "__main__":
    main_analysis()
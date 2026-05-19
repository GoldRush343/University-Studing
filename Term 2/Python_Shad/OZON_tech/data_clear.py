import polars as pl
from pathlib import Path

def process_search_data(date_str: str):
    # 1. ЗАГРУЗКА
    base_path = Path('.')
    day_path = base_path / 'user_actions' / 'user_actions_3_months' / f'date={date_str}'
    
    parts = []
    for parquet_file in day_path.glob('action_type=*/*.parquet'):
        part = pl.read_parquet(parquet_file).with_columns(
            pl.lit(parquet_file.parent.name.replace('action_type=', '')).alias('action_type_folder')
        )
        parts.append(part)
    
    df = pl.concat(parts)
    
    # 2. ОЧИСТКА (Data Cleaning)
    # Удаляем ботов (здесь можно добавить фильтр по количеству действий в секунду, если нужно)
    # Удаляем строки без поискового запроса, если тип действия - search
    df = df.filter(pl.col('user_id') != 6195822)
    
    # 3. ПОДГОТОВКА ВОРОНКИ
    # Выделяем целевые действия
    payment_actions = ['favorite', 'to_cart']
    
    # Приводим к единому таймлайну
    events = df.group_by(['user_id', 'timestamp']).agg(
        pl.col('search_query').drop_nulls().first().alias('search_query'),
        (pl.col('action_type') == 'search').sum().cast(pl.UInt32).alias('is_search'),
        (pl.col('action_type') == 'view').sum().cast(pl.UInt32).alias('is_view'),
        (pl.col('action_type').is_in(payment_actions)).any().alias('is_conversion')
    )
    
    # 4. РАСЧЕТ МЕТРИК ПО ЗАПРОСАМ (Агрегация)
    # Считаем для каждого запроса: сколько раз искали, сколько просмотрели, сколько купили
    metrics_df = (
        events.filter(pl.col('search_query').is_not_null())
        .group_by('search_query')
        .agg(
            pl.len().alias('total_shows'),
            pl.col('is_view').sum().alias('total_views'),
            pl.col('is_conversion').sum().alias('total_conversions')
        )
        .with_columns(
            (pl.col('total_conversions') / pl.col('total_shows')).alias('conversion_rate'),
            (pl.col('total_views') / pl.col('total_shows')).alias('view_rate')
        )
        .sort('conversion_rate', descending=True)
    )
    
    return metrics_df

# --- ЗАПУСК ---
day = '2024-03-01'
final_table = process_search_data(day)

# Сохраняем во временную таблицу (parquet файл)
final_table.write_parquet('quality_score_report.parquet')

print("Пайплайн завершен. Итоговая таблица:")
print(final_table.head(10))
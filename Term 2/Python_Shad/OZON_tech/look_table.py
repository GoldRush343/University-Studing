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

s = pl.concat(parts)
print(s.shape)

# 1. Посмотрим общую информацию: типы данных и количество пропусков
print("--- Схема данных (типы колонок) ---")
print(s.schema)

print("\n--- Количество пропусков (null) в каждой колонке ---")
print(s.null_count())

# 2. Исследование категориальных колонок
# action_type, widget_name, action_type_folder — это ключевые поля для логики
cat_cols = ['action_type', 'widget_name', 'action_type_folder']

for col in cat_cols:
    print(f"\n--- Уникальные значения в колонке: {col} ---")
    # Берем уникальные значения и сортируем их по популярности
    unique_vals = s.select(col).unique().sort(col)
    print(unique_vals.to_series().to_list())

# 3. Посмотрим примеры запросов (чтобы понять их вид)
print("\n--- Примеры 10 случайных поисковых запросов ---")
print(s.filter(pl.col('search_query').is_not_null())
      .select('search_query')
      .sample(10)
      .to_series().to_list())

# 4. Анализ связи между колонками (например, какие виджеты есть для каких типов действий)
print("\n--- Группировка: какие виджеты используются для каких action_type ---")
widget_dist = s.group_by(['action_type', 'widget_name']).len().sort('len', descending=True)
print(widget_dist)
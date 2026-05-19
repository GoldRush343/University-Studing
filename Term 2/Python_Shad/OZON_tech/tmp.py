import polars as pl

# 1. Загружаем сохраненный ранее отчет
try:
    df = pl.read_parquet('quality_score_report.parquet')
    print("Отчет успешно загружен!")
    print(f"Всего уникальных запросов: {len(df)}\n")
except FileNotFoundError:
    print("Ошибка: файл quality_score_report.parquet не найден. Сначала запустите основной пайплайн.")
    exit()

# 2. Находим медиану, чтобы выделить "средние" запросы
# Мы исключаем редкие запросы (шум) и слишком популярные
median_shows = df.select(pl.col('total_shows').median()).item()

# Определяем "средний" диапазон (например, от 0.5 до 2 медиан)
# Можно настроить под себя
avg_df = df.filter(
    (pl.col('total_shows') >= median_shows * 0.5) & 
    (pl.col('total_shows') <= median_shows * 2.0)
)

print(f"Медианное число показов: {median_shows}")
print(f"Количество запросов в 'среднем' диапазоне: {len(avg_df)}")

# 3. Показываем результат
# Сортируем так, чтобы сверху были самые эффективные, снизу — самые проблемные
result = avg_df.sort('conversion_rate', descending=True)

print("\n--- Топ 20 эффективных 'средних' запросов ---")
print(result.head(20))

print("\n--- Топ 20 проблемных 'средних' запросов (Conversion Rate = 0) ---")
print(result.filter(pl.col('conversion_rate') == 0).head(20))
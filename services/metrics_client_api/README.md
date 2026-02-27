# Чтоб проверить
> 1. хуярим по направлению MaRiTs/services/metrics_client_api
> 2. Качаем все что в томлах есть ```pip install -e .```
> 3. На всякий проверяем установку модуля ```python -c "import metrics_client_api; print(metrics_client_api)"```
> 3.5 Можно еще так проверить ```uvicorn metrics_client_api.main:app --reload```
> 4. Собираем ```docker build -t metrics-client-api .```
> 5. Запускаем ```docker run --rm -p 8000:8000 metrics-client-api```
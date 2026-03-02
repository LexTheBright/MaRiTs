# Чтоб проверить
> 1. хуярим по направлению MaRiTs/services/metrics_server
> 2. Качаем все что в томлах есть ``pip install -e .``
> 3. Проверяемс ``python -m server.main``
> 4. Собираем ``docker build -t metrics-server .``
> 5. Запускаем ``docker run --rm -p 8888:8888 --name metrics-server metrics-server``


## Можно попробовать обратиться:
```python
from metrics_client import Client

c = Client("127.0.0.1", 8888)
c.put("test.metric", 42.0)
print(c.get("test.metric"))
```
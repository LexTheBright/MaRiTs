# --- ЭТАП 1: Сборка (Builder) ---
FROM python:3.14-alpine as builder

# Устанавливаем инструменты сборки
RUN apk add --no-cache \
    build-base \
    libffi-dev 

WORKDIR /app

# Улучшаем кеширование: сначала только файлы сборки
COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip setuptools wheel build && \
pip install --no-cache-dir --prefix=/install influxdb-client

COPY server ./server
# Собираем проект в wheel-пакет
RUN python -m build && \
pip install --no-cache-dir --prefix=/install --no-deps ./dist/*.whl 
    # Устанавливаем во временную папку /install

# --- ЭТАП 2: Финальный образ ---
FROM python:3.14-alpine

# Метаданные (полезно для администрирования)
LABEL project.name="Metrics TCP server" \
      project.owner="Lex Huan Ryu" \
      version="0.1.0"

# Настройки Python (не генерим pyc и выводим сразу в консоль)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Добавляем путь к установленным пакетам в PATH
    PATH="/usr/local/bin:$PATH"

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY --from=builder /install /usr/local

RUN chown -R appuser:appgroup /app

USER appuser
# FastAPI порт
EXPOSE 8888

# Healthcheck через TCP-сокет (nc) или Python
# Вариант 1: через netcat (легковесный)
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
#   CMD echo "ping" | timeout 2 nc -w 1 localhost 8888 >/dev/null 2>&1 || exit 1

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c 'import urllib.request; urllib.request.urlopen("http://localhost:8888/")' || exit 1

# Запуск сервера (соответствует коду с asyncio.run(main()))
# Запуск через модуль. 
CMD ["python", "-m", "server.main"] 
# ли пакет:
# CMD ["python", "-c", "from server.main import run_server; run_server('0.0.0.0', 8888)"]
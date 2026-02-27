# --- ЭТАП 1: Сборка (Builder) ---
FROM python:3.12-alpine as builder

# Устанавливаем инструменты сборки. 
# Pandas и NumPy часто требуют компиляции, если нет готовых wheel-файлов для Alpine.
RUN apk add --no-cache \
    build-base \
    libffi-dev

WORKDIR /app

# Улучшаем кеширование: сначала только файлы сборки
COPY pyproject.toml README.md ./
COPY src ./src

# Собираем проект в wheel-пакет
RUN pip install --no-cache-dir --upgrade pip setuptools wheel build && \
    python -m build && \
    # Устанавливаем во временную папку /install
    pip install --no-cache-dir --prefix=/install ./dist/*.whl 

# --- ЭТАП 2: Финальный образ ---
FROM python:3.12-alpine

# Метаданные (полезно для администрирования)
LABEL project.name="Metrics Client API" \
      project.owner="Lex Huan Ryu" \
      version="0.1.0"

# Настройки Python (не генерим pyc и выводим сразу в консоль)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Добавляем путь к установленным пакетам в PATH
    PATH="/usr/local/bin:$PATH"

# Для работы Pandas/NumPy в Alpine иногда нужны базовые библиотеки C
RUN apk add --no-cache libstdc++ curl

WORKDIR /app

# Копируем только установленные библиотеки и наш пакет из builder
# Копируем в /usr/local, чтобы всё сразу попало в системные пути Python
COPY --from=builder /install /usr/local

# Создаем volume для логов или временных данных (если нужно)
VOLUME ["/tmp"]

# FastAPI порт
EXPOSE 8000

# Здоровье контейнера (Healthcheck)
# Позволяет Docker понимать, не завис ли сервис внутри
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
CMD curl -f http://localhost:8000/docs || exit 1

RUN pip install marimo pandas

# Копируем тетрадки
COPY notebooks/ ./notebooks

# Запуск marimo в режиме сервера
CMD ["marimo", "run", "notebooks/dashboard.py", "--host", "0.0.0.0", "--port", "8080"]

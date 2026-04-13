# --- ЭТАП 1: Сборка (Builder) ---
FROM python:3.14-alpine as builder

# Устанавливаем инструменты сборки. build-base и libffi-dev могут понадобиться из-за Alpine - часто приходится компилировать из исходников, а не whl
# Pandas и NumPy часто требуют компиляции, если нет готовых wheel-файлов для Alpine.
RUN apk add --no-cache \
    build-base \
    libffi-dev

WORKDIR /app

# Улучшаем кеширование: сначала только файлы сборки
COPY pyproject.toml ./

# Устанавливаем зависимости во временную папку. 
# Мы делаем это ДО копирования исходного кода (src), 
# чтобы этот слой кэшировался и не пересобирался при правках в .py файлах.
RUN pip install --no-cache-dir --upgrade pip setuptools wheel build && \
pip install --no-cache-dir --prefix=/install pandas numpy fastapi uvicorn 

# Теперь копируем исходники и собираем наш локальный пакет
COPY src ./src
RUN python -m build && \
pip install --no-cache-dir --prefix=/install ./dist/*.whl

# --- ЭТАП 2: Финальный образ ---
FROM python:3.14-alpine

# Метаданные (полезно для администрирования)
LABEL project.name="Metrics Client API" \
      project.owner="Lex Huan Ryu" \
      version="0.1.0"

# Настройки Python (не генерим pyc и выводим сразу в консоль)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Добавляем путь к установленным пакетам в PATH (обычно в уже есть, но профилактика не помешает)
    PATH="/usr/local/bin:$PATH"

# Для работы Pandas/NumPy в Alpine иногда нужны базовые библиотеки C
RUN apk add --no-cache libstdc++ curl gcompat

# БЕЗОПАСНОСТЬ: Создаем непривилегированного пользователя
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Копируем только установленные библиотеки и наш пакет из builder
# Копируем в /usr/local, чтобы всё сразу попало в системные пути Python
COPY --from=builder /install /usr/local

# Меняем владельца рабочей директории
RUN chown -R appuser:appgroup /app
# Переключаемся на пользователя
USER appuser

# FastAPI порт
EXPOSE 8000

# Здоровье контейнера (Healthcheck)
# Позволяет Docker понимать, не завис ли сервис внутри
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

# Запуск через модуль. 
# В структуре src/metrics_client_api/main.py пакет называется metrics_client_api
CMD ["uvicorn", "metrics_client_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
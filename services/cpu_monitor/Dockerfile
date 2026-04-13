# --- ЭТАП 1: Сборка (Builder) ---
FROM python:3.14-alpine as builder

# Устанавливаем инструменты сборки + netcat для healthcheck
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    netcat-openbsd

WORKDIR /app

# Улучшаем кеширование: сначала только файлы сборки
COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip setuptools wheel build && \
pip install --no-cache-dir --prefix=/install psutil requests

# Устанавливаем во временную папку /install
# Собираем проект в wheel-пакет
COPY src ./src
RUN python -m build && \
pip install --no-cache-dir --prefix=/install ./dist/*.whl 

# --- ЭТАП 2: Финальный образ ---
FROM python:3.14-alpine

# Метаданные (полезно для администрирования)
LABEL project.name="Metrics TCP monitor" \
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

# Копируем только установленные библиотеки и наш пакет из builder
# Копируем в /usr/local, чтобы всё сразу попало в системные пути Python

# Запуск через модуль. 
CMD ["python", "-m", "cpu_monitor.main"] 


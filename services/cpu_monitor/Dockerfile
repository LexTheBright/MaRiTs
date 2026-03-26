# --- ЭТАП 1: Сборка (Builder) ---
FROM python:3.14-alpine as builder

# Устанавливаем инструменты сборки. 
# Pandas и NumPy часто требуют компиляции, если нет готовых wheel-файлов для Alpine.
# Устанавливаем инструменты сборки + netcat для healthcheck
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    netcat-openbsd

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

WORKDIR /app

# Копируем только установленные библиотеки и наш пакет из builder
# Копируем в /usr/local, чтобы всё сразу попало в системные пути Python
COPY --from=builder /install /usr/local

# Запуск через модуль. 
CMD ["python", "-m", "cpu_monitor.main"] 


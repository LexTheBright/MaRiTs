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
COPY server ./server

# Собираем проект в wheel-пакет
RUN pip install --no-cache-dir --upgrade pip setuptools wheel build && \
    python -m build && \
    # Устанавливаем во временную папку /install
    pip install --no-cache-dir --prefix=/install ./dist/*.whl 

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

WORKDIR /app

# Копируем только установленные библиотеки и наш пакет из builder
# Копируем в /usr/local, чтобы всё сразу попало в системные пути Python
COPY --from=builder /install /usr/local

# FastAPI порт
EXPOSE 8888

# Healthcheck через TCP-сокет (nc) или Python
# Вариант 1: через netcat (легковесный)
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
#   CMD echo "ping" | timeout 2 nc -w 1 localhost 8888 >/dev/null 2>&1 || exit 1

# Вариант 2 (альтернатива, если nc не нравится): через Python
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
#   CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('localhost',8888)); s.close()" || exit 1

# Запуск сервера (соответствует коду с asyncio.run(main()))
# Запуск через модуль. 
CMD ["python", "-m", "server.main"] 
# ли пакет:
# CMD ["python", "-c", "from server.main import run_server; run_server('0.0.0.0', 8888)"]
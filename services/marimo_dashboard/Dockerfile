# --- ЭТАП 1: Сборка (Builder) ---
FROM python:3.14-alpine as builder

RUN apk add --no-cache \
    build-base \
    libffi-dev 

WORKDIR /app

# Сначала устанавливаем зависимости (кешируется при изменении кода)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel build && \
    pip install --no-cache-dir --prefix=/install \
        pandas \
        numpy \
        marimo \
        packaging \ 
        requests \ 
        plotly

COPY notebooks/ ./notebooks
# RUN python -m build && \
#     pip install --no-cache-dir --prefix=/install ./dist/*.whl

# --- ЭТАП 2: Финальный образ ---
FROM python:3.14-alpine

# Метаданные (полезно для администрирования)
LABEL project.name="Metrics marimo dashboard" \
      project.owner="Lex Huan Ryu" \
      version="0.1.0"

# Настройки Python (не генерим pyc и выводим сразу в консоль)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH"

# Для работы Pandas/NumPy в Alpine иногда нужны базовые библиотеки C
RUN apk add --no-cache libstdc++ curl gcompat

# БЕЗОПАСНОСТЬ: Создаем непривилегированного пользователя
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app
COPY --from=builder /install /usr/local
# Явно переустанавливаем packaging для гарантии доступности
RUN pip install --no-cache-dir --upgrade packaging

# Меняем владельца рабочей директории
RUN chown -R appuser:appgroup /app
# Переключаемся на пользователя
USER appuser

# FastAPI порт
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c 'import urllib.request; urllib.request.urlopen("http://localhost:8080/")' || exit 1

# Запуск marimo в режиме сервера
CMD ["marimo", "run", "notebooks/dashboard.py", "--host", "0.0.0.0", "--port", "8080"]

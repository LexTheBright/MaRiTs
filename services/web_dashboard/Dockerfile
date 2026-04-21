# --- ЭТАП 1: Сборка (Builder) ---
FROM python:3.14-alpine as builder

RUN apk add --no-cache \
    build-base \
    libffi-dev

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip setuptools wheel build

COPY src ./src

RUN python -m build && \ 
pip install --no-cache-dir --prefix=/install --no-deps ./dist/*.whl 

# --- ЭТАП 2: Финальный образ ---
FROM python:3.14-alpine

LABEL project.name="Metrics web dashboard" \
      project.owner="Lex Huan Ryu" \
      version="0.1.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH" 

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY --from=builder /install /usr/local
COPY src/web_dashboard/server.py ./server.py       
COPY src/web_dashboard/static ./static         

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c 'import urllib.request; urllib.request.urlopen("http://localhost:4000/")' || exit 1

CMD ["python", "server.py"]
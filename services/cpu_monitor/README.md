# CPU Monitor

Агент для сбора метрик CPU и отправки их в `metrics_client_api`.

## Что умеет

- Собирать CPU-метрики на хосте.
- Отправлять метрики в API по HTTP.
- Работать:
  - в Docker;
  - как локальная Python-утилита на Linux;
  - как локальная Python-утилита на Windows.

## Структура проекта

```text
cpu_monitor/
├── Dockerfile
├── pyproject.toml
├── install_agent.bat
├── run_agent.bat
├── install_and_run_agent.bat
├── install_and_run.sh
└── src
    └── cpu_monitor
        ├── collector.py
        ├── compressor.py
        ├── __init__.py
        ├── main.py
        └── sender.py
```

## Зависимости

- Python 3.14+
- `psutil`
- `requests`

## Конфигурация

Агент настраивается через переменные окружения:

- `METRICS_API_URL` — адрес FastAPI-клиента.
- `CPU_SCRAPE_INTERVAL` — интервал между циклами сбора, в секундах.
- `CPU_COMPRESSOR` — имя алгоритма сжатия, например `none`.

Пример:

```bash
METRICS_API_URL=http://localhost:8000
CPU_SCRAPE_INTERVAL=5
CPU_COMPRESSOR=none
```

---

# Запуск в Docker Compose

Если весь проект поднимается через compose, агент работает как отдельный сервис и отправляет метрики в `metrics_client_api`.

## Пример сервиса в `docker-compose.yml`

```yaml
  # 4. Агент мониторинга (Читает ОС)
  cpu_monitor:
    build:
      context: ./services/cpu_monitor
    container_name: marits-cpu-monitor
    depends_on:
      - metrics_client_api
    networks:
      - metrics-net
    environment:
      METRICS_API_URL: http://metrics_client_api:8000
      CPU_SCRAPE_INTERVAL: "5.0"
      CPU_COMPRESSOR: "none"
```

## Запуск

Из корня проекта:

```bash
docker-compose up -d --build
```

## Проверка

```bash
docker-compose ps
docker-compose logs -f cpu_monitor
```

---

# Запуск на Linux без Docker

Этот сценарий подходит для локального запуска без прав администратора.

## Вариант 1. Через скрипт установки и запуска

Скрипт `install_and_run.sh` создаёт локальное виртуальное окружение, ставит зависимости и запускает агент.

### Запуск

```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

## Вариант 2. Вручную

### Создать виртуальное окружение

```bash
python3 -m venv .venv_cpu_monitor
```

### Установить пакет

```bash
.venv_cpu_monitor/bin/python -m pip install --upgrade pip
.venv_cpu_monitor/bin/python -m pip install .
```

### Запустить агент

```bash
export METRICS_API_URL="http://localhost:8000"
export CPU_SCRAPE_INTERVAL="5"
export CPU_COMPRESSOR="none"

.venv_cpu_monitor/bin/python -m cpu_monitor.main
```

## Примечание

Если на системе включена защита от установки в системный Python, не используй `pip install` без виртуального окружения. Всегда ставь пакет в локальный `venv`.

---

# Запуск на Windows без Docker

Этот сценарий подходит для локального запуска без прав администратора.

## Вариант 1. Через `install_agent.bat`

Скрипт создаёт локальное виртуальное окружение и ставит пакет туда.

### Запуск

```bat
install_agent.bat
```

## Вариант 2. Через `install_agent.bat`

Скрипт запускает уже установленный агент из локального `venv`.

### Запуск

```bat
install_agent.bat
```

## Вручную

### Создать виртуальное окружение

```bat
python -m venv .venv_cpu_monitor
```

### Установить пакет

```bat
.venv_cpu_monitor\Scripts\python.exe -m pip install --upgrade pip
.venv_cpu_monitor\Scripts\python.exe -m pip install .
```

### Запустить агент

```bat
set METRICS_API_URL=http://localhost:8000
set CPU_SCRAPE_INTERVAL=5
set CPU_COMPRESSOR=none

.venv_cpu_monitor\Scripts\python.exe -m cpu_monitor.main
```

---

# Как это работает

Агент:

1. ждёт указанный интервал;
2. собирает CPU-метрики;
3. при необходимости прогоняет их через компрессор;
4. отправляет пакет метрик в `metrics_client_api`.

`metrics_client_api` уже сам преобразует запросы в обращения к серверу метрик.

---

# Протокол отправки

Агент отправляет данные в API в формате пакета метрик.

Пример одной записи:

```json
{
  "metric": "cpu.usage_percent",
  "value": 42.5,
  "timestamp": 1711450000
}
```

---

# Полезные команды

## Linux

```bash
python3 -m venv .venv_cpu_monitor
.venv_cpu_monitor/bin/python -m pip install .
.venv_cpu_monitor/bin/python -m cpu_monitor.main
```

## Windows

```bat
python -m venv .venv_cpu_monitor
.venv_cpu_monitor\Scripts\python.exe -m pip install .
.venv_cpu_monitor\Scripts\python.exe -m cpu_monitor.main
```

## Docker Compose

```bash
docker-compose up -d --build
docker-compose logs -f cpu_monitor
```

---

# Разработка

Если ты меняешь код агента, после правок:

- в Docker — пересобери образ;
- в Linux/Windows локально — переустанови пакет в virtual environment.

Примеры:

```bash
.venv_cpu_monitor/bin/python -m pip install .
```

```bat
.venv_cpu_monitor\Scripts\python.exe -m pip install .
```

---

# Дальнейшее развитие

Планируется добавить:

- расширение пула собираемых метрик;
- кастомный компрессор временных рядов;

---
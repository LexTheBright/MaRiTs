# Web Dashboard

Веб-интерфейс для визуализации метрик в реальном времени с интерактивными графиками и аналитикой.

## Назначение

- Отображение метрик в реальном времени через Server-Sent Events (SSE)
- Построение интерактивных временных рядов с использованием Chart.js
- Расчёт и отображение статистики метрик (среднее, мин/макс, тренды)
- Гибкая настройка интервала обновления и глубины истории
- Динамический выбор отображаемых метрик

## Структура проекта

```text
web_dashboard/
├── Dockerfile
├── README.md
├── pyproject.toml
├── info.md
└── src/
    └── web_dashboard/
        ├── __init__.py
        ├── server.py          # HTTP сервер для раздачи статики
        └── static/
            ├── index.html     # Точка входа приложения
            └── metrics-dashboard.js  # Веб-компонент дашборда
```

## Зависимости

- Python 3.11+
- Chart.js (для графиков)
- Luxon (для работы со временем)
- Chart.js Adapter для Luxon

## Конфигурация

Сервис настраивается через переменные окружения:

| Переменная | Описание | Пример | По умолчанию |
|------------|----------|--------|--------------|
| `METRICS_API_BASE` | Базовый URL API метрик | `http://metrics_client_api:8000` | `http://localhost:8000` |
| `WEB_DASHBOARD_HOST` | Хост для прослушивания | `0.0.0.0` | `0.0.0.0` |
| `WEB_DASHBOARD_PORT` | Порт для прослушивания | `4000` | `4000` |

---

## Запуск в Docker Compose

### Production режим

Сервис запускается как часть общего compose-файла:

```bash
docker compose up -d web_dashboard
```

Конфигурация в `docker-compose.yml`:

```yaml
web_dashboard:
  build:
    context: ./services/web_dashboard
  container_name: marits-web-dashboard
  depends_on:
    - metrics_client_api
  ports:
    - "4000:4000"
  environment:
    METRICS_API_BASE: http://metrics_client_api:8000
  networks:
    - metrics-net
  restart: unless-stopped
```

### Debug режим

Запуск с пересборкой и просмотром логов:

```bash
# Пересборка и запуск
docker compose up web_dashboard --build

# Просмотр логов
docker compose logs -f web_dashboard

# Доступ к дашборду
# http://localhost:4000
```

---

## Запуск на хосте (без Docker)

### Установка

```bash
cd services/web_dashboard

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows

# Установить зависимости
pip install -e .
```

### Запуск в режиме разработки

```bash
# Установка переменных окружения
export METRICS_API_BASE=http://localhost:8000
export WEB_DASHBOARD_HOST=0.0.0.0
export WEB_DASHBOARD_PORT=4000

# Запуск сервера
python -m web_dashboard.server --host 0.0.0.0 --port 4000
```

Или с использованием uvicorn (если требуется auto-reload):

```bash
uvicorn web_dashboard.server:app --host 0.0.0.0 --port 4000 --reload
```

### Запуск в production режиме

```bash
# С несколькими workers для производительности
uvicorn web_dashboard.server:app --host 0.0.0.0 --port 4000 --workers 4
```

---

## Проверка работоспособности

### curl примеры

```bash
# Проверка доступности
curl http://localhost:4000/

# Проверка health endpoint
curl http://localhost:4000/health
```

### Браузер

Откройте в браузере:

```
http://localhost:4000
```

---

## Функционал дашборда

### Real-time визуализация

- **Server-Sent Events (SSE)**: Автоматическое получение обновлений метрик каждые N секунд
- **Интерактивные графики**: Масштабирование, hover-эффекты, легенда с переключением
- **Временное окно**: Настройка глубины истории от 1 минуты до 24 часов

### Аналитика метрик

Для каждой выбранной метрики отображается:
- Среднее значение за период
- Минимальное и максимальное значение
- Последнее полученное значение
- Тренд (рост/падение/стабильно)

### Управление метриками

- **Динамический выбор**: Включение/отключение метрик через чекбоксы
- **Автоматический выбор**: Первые 3 метрики выбираются автоматически при загрузке
- **Настройка интервала**: Регулировка частоты обновления данных (1-300 секунд)

### Локализация

Поддержка человеко-читаемых названий и единиц измерения:
- `cpu.usage_percent` → "Загрузка CPU" (%)
- `cpu.frequency_mhz` → "Частота CPU" (МГц)
- `memory.used_bytes` → "Использование памяти" (Б/КБ/МБ/ГБ)

---

## Архитектура

### Компоненты

#### 1. HTTP Server (`server.py`)

Минимальный HTTP-сервер на базе Python для отдачи статических файлов:
- Раздача файлов из директории `static/`
- Поддержка CORS для доступа с других доменов
- Отключение кэширования для актуальности данных
- Настройка хоста и порта через аргументы командной строки

#### 2. Frontend веб-компонент (`metrics-dashboard.js`)

**Хранилища данных:**
- `metricsDataStore`: Map для накопления точек каждой метрики
- `charts`: Map активных Chart.js графиков
- `selectedMetrics`: Set выбранных пользователем метрик
- `allAvailableMetrics`: Список всех доступных метрик

**Основные методы:**
- `initDashboard()`: Инициализация и подключение к SSE
- `_connectToStreamImpl()`: Создание EventSource для real-time обновлений
- `updateCharts(metricsData)`: Обновление графиков новыми данными
- `fetchAnalysis()`: Загрузка статистики с сервера
- `rebuildCharts()`: Перестройка графиков при изменении выбора метрик
- `applyParameters()`: Применение параметров (интервал, глубина истории)

**Механизм debounce:**
Для предотвращения частых переподключений используется debouncing (3 секунды).

---

## Troubleshooting

### Дашборд не загружается

1. Проверьте доступность API метрик:
   ```bash
   curl http://localhost:8000/metrics/names
   ```

2. Убедитесь, что порт 4000 свободен:
   ```bash
   netstat -tlnp | grep 4000
   ```

3. Проверьте логи:
   ```bash
   docker compose logs web_dashboard
   ```

### Графики не обновляются

- Проверьте подключение к SSE потоку в консоли браузера (F12)
- Убедитесь, что `METRICS_API_BASE` указывает на правильный адрес
- Проверьте наличие данных в метриках через API

### Ошибки CORS

Если дашборд открывается с другого домена, убедитесь, что сервер настроен на поддержку CORS:

```python
# В server.py должна быть поддержка CORS заголовков
```

---

## Разработка

### Добавление новых метрик

1. Добавьте конфигурацию метрики в `metricConfig` в `metrics-dashboard.js`:

```javascript
const metricConfig = {
  'new.metric': {
    title: 'Новая метрика',
    unit: 'ед.',
    min: 0,
    max: 100,
    step: 10
  }
};
```

2. Метрика автоматически появится в списке доступных после получения с `/metrics/names`

### Настройка стилей графиков

Измените параметры Chart.js в `metrics-dashboard.js`:

```javascript
const chart = new Chart(ctx, {
  type: 'line',
  data: {...},
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {...}
  }
});
```

### Изменение интервала обновления по умолчанию

```html
<!-- В index.html -->
<metrics-dashboard
  server-url="http://localhost:8000"
  interval="10"      <!-- Обновление каждые 10 секунд -->
  minutes="30"       <!-- История за 30 минут -->
></metrics-dashboard>
```

---

## Интеграция

### С Metrics Client API

Дашборд получает данные через REST API и SSE:

- **GET /metrics/names**: Список доступных метрик
- **GET /metrics/{name}**: Исторические данные метрики
- **GET /metrics/analysis**: Статистика по метрикам
- **GET /metrics/stream**: SSE поток для real-time обновлений

### С Marimo Dashboard

Оба интерфейса используют одни данные:
- **Web Dashboard** — для мониторинга в реальном времени (SSE поток)
- **Marimo Dashboard** — для глубокого анализа и отчётов по запросу

---

## Мониторинг

### Health Check

```bash
curl http://localhost:4000/health
```

Ожидаемый ответ: `{"status": "healthy"}`

### Docker Health Check

Автоматическая проверка каждые 30 секунд:

```bash
docker inspect --format='{{.State.Health.Status}}' marits-web-dashboard
```

---

## Планы развития

- Экспорт графиков в PNG/SVG
- Настройка алертов при превышении порогов
- Дополнительные типы визуализации (heatmaps, gauges)
- Сохранение пользовательских настроек в localStorage
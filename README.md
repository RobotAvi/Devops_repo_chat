## GitLab Multi-Repo Q&A Bot (LangChain + FAISS)

Сервис вопросов-ответов по нескольким репозиториям GitLab без полного клонирования. Получает структуру и содержимое файлов по API по необходимости, кэширует локально, строит векторный индекс (FAISS) и генерирует ответы через LangChain.

### Возможности
- Точечная загрузка по GitLab API с ретраями и TTL‑кэшем
- Разбор структуры репозитория (ключевые файлы, конфиги, модули)
- Порционная загрузка содержимого, фильтрация бинарей и тестов
- Эмбеддинги (OpenAI‑совместимые) + FAISS индекс
- Обновление индекса по запросу
- Контроль доступа и токены администратора
- FastAPI сервер и CLI
- Тесты на pytest

### Требования
- Python 3.11+
- GitLab PAT с правами чтения (api)

### Быстрый старт (локально)
1) Создайте файл окружения `.env` (можно пустой — базовые параметры зададите на странице /setup):
```
touch .env
```

2) Установите зависимости:
```
make install
```

3) Запустите тесты (необязательно):
```
make test
```

4) Запустите сервер:
```
make run-server
```
Откройте `http://localhost:8000` — при первом запуске вы будете перенаправлены на `/setup` для ввода настроек и сохранения их в `.env`.

### Docker (one‑command)
```
touch .env
docker compose up --build -d
# Откройте http://localhost:8000 (страница /setup появится при отсутствии настроек)
```
Docker‑компоуз монтирует каталоги `./data` и `./indices` внутрь контейнера для кэша и индексов.

### Конфигурация (.env)
Ключевые переменные окружения, читаются через `pydantic-settings`:
- GITLAB_BASE_URL — базовый URL API GitLab (например, https://gitlab.com/api/v4)
- GITLAB_TOKEN — ваш GitLab Personal Access Token
- LLM_API_KEY, LLM_BASE_URL, LLM_MODEL — ключ/endpoint/модель для LLM (опционально)
- OPENAI_API_KEY — ключ для эмбеддингов (если не задан EMBEDDING_API_KEY)
- EMBEDDING_API_KEY, EMBEDDING_BASE_URL, EMBEDDING_MODEL — настройки эмбеддингов
- CACHE_DIR (./data), CACHE_TTL_SECONDS (86400), REDIS_URL (опц.)
- INDEX_DIR (./indices), LOG_LEVEL (INFO)
- FASTAPI_HOST (0.0.0.0), FASTAPI_PORT (8000)
- ALLOWED_PROJECTS — CSV‑список разрешённых проектов (если пусто, разрешены все)
- ADMIN_TOKENS — CSV‑токены админов для обхода ALLOWED_PROJECTS

После заполнения /setup настройки сохраняются в `.env` (перезаписываются соответствующие ключи).

### API
- `GET /healthz` — проверка состояния
- `GET /setup` — страница настройки
- `GET /` — простой дашборд (после настройки)
- `POST /rebuild/{project_id}` — пересобрать индекс проекта, заголовок `X-API-Key` при необходимости доступа
- `POST /ask/{project_id}?q=...` — получить ответ по проекту, заголовок `X-API-Key` при необходимости

`project_id` — это `path_with_namespace` из GitLab (например, `group/subgroup/repo`).

### CLI
Запуск из исходников:
```
python -m src ask --project group/subgroup/repo "Где хранится конфигурация базы данных?"
```
Пересборка индекса:
```
python -m src rebuild --project group/subgroup/repo
```
Есть удобная цель Make для запроса:
```
PROJECT=group/sub/repo Q="Как запустить сервис?" make run-cli
```

### Структура проекта
```
src/
  access_control.py      # Проверка доступа и админ‑токены
  chat_interface.py      # FastAPI + CLI
  config.py              # Настройки из окружения
  gitlab_api_handler.py  # Интеграция с GitLab API + кэш
  index_builder.py       # Построение/поиск по FAISS
  index_updater.py       # Пересборка индекса по проекту
  langchain_chain.py     # Генерация ответа через LangChain
  partial_file_loader.py # Чанкинг и фильтрация файлов
  query_processor.py     # Оркестрация запроса → ответ
  structure_parser.py    # Поиск ключевых файлов/конфигов/модулей
  utils.py               # Логирование, TTL‑кэш, ретраи
templates/               # /setup и простой дашборд
static/                  # Стили для страниц
tests/                   # Pytest тесты
data/                    # Локальный кэш (создаётся в рантайме)
indices/                 # Индексы FAISS (создаётся в рантайме)
```

### Заметки по безопасности
- Доступ к проектам ограничивается `ALLOWED_PROJECTS`; при пустом значении разрешены все
- Админ‑токены из `ADMIN_TOKENS` дают доступ к любому проекту (заголовок `X-API-Key`)
- Все попытки доступа логируются

### Зависимости
См. `requirements.txt`. Основные: FastAPI, Uvicorn, httpx, langchain, langchain-openai, openai, faiss-cpu, numpy, pydantic, tenacity, redis, Jinja2, pytest, pytest-cov.

---
Название проекта: GitLab Multi‑Repo Q&A Bot

## GitLab Multi-Repo Q&A Bot (LangChain + FAISS)

A scalable question-answering bot over multiple GitLab repositories without full cloning. It fetches repository structure and selected contents on-demand, caches locally, builds a vector index (FAISS), and uses LangChain to generate grounded answers.

### Features
- Selective GitLab API fetching with retries and TTL cache
- Structure parsing to identify key files (README, Dockerfile, configs, main modules)
- Chunked loading and filtering (exclude binaries/tests)
- Vectorization (OpenAI embeddings or alternative) and FAISS index
- Reactive index updates (webhook/scheduler)
- Access control and token management
- CLI and optional FastAPI server
- Tests (unit + integration), 70%+ coverage target

### Quickstart
1) Create and fill environment:
```
cp .env.example .env
# Fill tokens and settings
```

2) Install dependencies (Python 3.8+):
```
make install
```

3) Run tests:
```
make test
```

4) Start API server:
```
make run-server
```

5) Ask via CLI:
```
python -m src ask --project project_one "Где хранится конфигурация базы данных?"
```

### Project Structure
```
src/
  access_control.py      # Access checks and token validation
  chat_interface.py      # CLI + FastAPI app
  config.py              # Settings via environment
  gitlab_api_handler.py  # GitLab API integration + caching
  index_builder.py       # FAISS index creation and updates
  index_updater.py       # Webhook/scheduler updating
  langchain_chain.py     # LangChain pipeline
  partial_file_loader.py # Chunking + file-type filtering
  query_processor.py     # Orchestration from question to answer
  structure_parser.py    # Parse repo structure to detect key files
  utils.py               # Logging, cache, helpers
tests/                   # Unit and integration tests
data/                    # Local cache (ttl) [gitignored]
indices/                 # FAISS indexes [gitignored]
```

### Configuration (.env)
See `.env.example` for all options. Important:
- GITLAB_BASE_URL, GITLAB_TOKEN
- OPENAI_API_KEY, EMBEDDING_MODEL
- CACHE_DIR, CACHE_TTL_SECONDS, REDIS_URL (optional)
- INDEX_DIR, LOG_LEVEL

### Security
- Access checks per-project
- API key/token management
- Access attempts are logged

### Roadmap
- Add Pinecone option
- Extend file-type heuristics
- Advanced RAG with multi-repo context merging

# Devops_repo_chat
Чат-бот по репозиториям с несколькими микросервисами

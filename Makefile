PY?=python3
PIP?=pip3

.PHONY: install test run-server run-cli fmt

install:
	$(PIP) install -r requirements.txt

test:
	$(PY) -m pytest --maxfail=1 --disable-warnings -q

run-server:
	$(PY) -m uvicorn src.chat_interface:app --host $${FASTAPI_HOST:-0.0.0.0} --port $${FASTAPI_PORT:-8000}

run-cli:
	$(PY) -m src ask --project $$PROJECT "$$Q"

fmt:
	@echo "(optional) add formatter here"

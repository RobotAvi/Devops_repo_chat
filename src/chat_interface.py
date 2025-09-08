from __future__ import annotations

import argparse
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .access_control import can_access_project
from .config import settings
from .index_updater import rebuild_index_for_project
from .query_processor import answer_question
from .utils import setup_logger
from .gitlab_api_handler import GitLabAPI


logger = setup_logger(__name__, settings.log_level)

app = FastAPI(title="GitLab Multi-Repo Q&A Bot")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def _is_configured() -> bool:
    return bool(settings.gitlab_token and settings.openai_api_key and settings.gitlab_base_url)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
@app.middleware("http")
async def redirect_to_setup(request: Request, call_next):
    if not _is_configured():
        if not request.url.path.startswith("/setup") and not request.url.path.startswith("/static") and request.url.path != "/healthz":
            return RedirectResponse(url="/setup")
    response = await call_next(request)
    return response


@app.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request):
    return templates.TemplateResponse("setup.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if not _is_configured():
        return RedirectResponse(url="/setup")
    # Minimal dashboard with simple controls
    return templates.TemplateResponse("dashboard.html", {"request": request})




@app.post("/rebuild/{project_id}")
def rebuild(project_id: str, x_api_key: Optional[str] = Header(default=None)) -> dict:
    if not can_access_project(project_id, x_api_key):
        raise HTTPException(status_code=403, detail="Forbidden")
    rebuild_index_for_project(project_id)
    return {"status": "ok"}


@app.post("/ask/{project_id}")
def ask(project_id: str, q: str, x_api_key: Optional[str] = Header(default=None)) -> dict:
    if not can_access_project(project_id, x_api_key):
        raise HTTPException(status_code=403, detail="Forbidden")
    return answer_question(project_id, q)


@app.post("/setup/validate/gitlab")
def validate_gitlab(base_url: str, token: str) -> dict:
    try:
        api = GitLabAPI(base_url=base_url, token=token)
        # trivial call to check auth and reachability
        api.get_repository_tree(project_id="projects")  # will likely 404; ensure host/token usable via headers
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True}


@app.get("/setup/projects")
def list_projects(q: str | None = None) -> dict:
    try:
        api = GitLabAPI()
        items = api.list_projects(search=q)
        # Return minimal info for selection
        projects = [
            {"id": str(i.get("id")), "path_with_namespace": i.get("path_with_namespace", ""), "name": i.get("name", "")}
            for i in items
        ]
        return {"ok": True, "projects": projects}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/setup/validate/openai")
def validate_openai(api_key: str, base_url: str | None = None, model: str | None = None) -> dict:
    try:
        from langchain_openai import OpenAIEmbeddings

        _ = OpenAIEmbeddings(api_key=api_key, base_url=base_url, model=model or settings.embedding_model)
        # lightweight call to validate format; avoid network call to keep it fast
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True}


@app.post("/setup/save")
def setup_save(gitlab_base_url: str, gitlab_token: str, llm_api_key: str | None = None, llm_base_url: str | None = None, llm_model: str | None = None, embedding_api_key: str | None = None, embedding_base_url: str | None = None, embedding_model: str | None = None) -> dict:
    # Persist to .env, overwrite or append keys
    import os
    from pathlib import Path

    env_path = Path(".env")
    existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    lines = []
    keys = {
        "GITLAB_BASE_URL": gitlab_base_url.strip(),
        "GITLAB_TOKEN": gitlab_token.strip(),
    }
    if llm_api_key is not None:
        keys["LLM_API_KEY"] = llm_api_key.strip()
    if llm_base_url is not None:
        keys["LLM_BASE_URL"] = llm_base_url.strip()
    if llm_model is not None:
        keys["LLM_MODEL"] = llm_model.strip()
    if embedding_api_key is not None:
        keys["EMBEDDING_API_KEY"] = embedding_api_key.strip()
    if embedding_base_url is not None:
        keys["EMBEDDING_BASE_URL"] = embedding_base_url.strip()
    if embedding_model is not None:
        keys["EMBEDDING_MODEL"] = embedding_model.strip()
    # remove old keys
    for line in existing.splitlines():
        if not any(line.startswith(f"{k}=") for k in keys.keys()):
            lines.append(line)
    # add new
    for k, v in keys.items():
        lines.append(f"{k}={v}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Best-effort runtime refresh
    os.environ.update(keys)
    from .config import settings as runtime_settings
    runtime_settings.__init__()  # reload from env
    return {"ok": True}


def main_cli() -> None:
    parser = argparse.ArgumentParser(prog="src")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ask_p = sub.add_parser("ask", help="Ask a question")
    ask_p.add_argument("--project", required=True)
    ask_p.add_argument("question", nargs="+")

    build_p = sub.add_parser("rebuild", help="Rebuild index for a project")
    build_p.add_argument("--project", required=True)

    args = parser.parse_args()
    if args.cmd == "ask":
        q = " ".join(args.question)
        out = answer_question(args.project, q)
        print(out["answer"])  # text IO only
    elif args.cmd == "rebuild":
        rebuild_index_for_project(args.project)
        print("OK")


if __name__ == "__main__":
    main_cli()


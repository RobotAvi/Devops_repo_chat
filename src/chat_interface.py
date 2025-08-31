from __future__ import annotations

import argparse
from typing import Optional

from fastapi import FastAPI, Header, HTTPException

from .access_control import can_access_project
from .config import settings
from .index_updater import rebuild_index_for_project
from .query_processor import answer_question
from .utils import setup_logger


logger = setup_logger(__name__, settings.log_level)

app = FastAPI(title="GitLab Multi-Repo Q&A Bot")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


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


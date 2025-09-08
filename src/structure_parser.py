from __future__ import annotations

from typing import Any, Dict, List


KEY_FILENAMES = {
    "README.md",
    "README",
    "Dockerfile",
    ".env",
    "docker-compose.yml",
    "docker-compose.yaml",
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "setup.py",
}

CONFIG_PATTERNS = ("config", "settings", "application.yml", "application.yaml", "application.properties")


def parse_tree(tree_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    key_files: List[str] = []
    modules: List[str] = []
    configs: List[str] = []

    for item in tree_items:
        if item.get("type") != "blob":
            continue
        path: str = item.get("path", "")
        filename = path.split("/")[-1]
        lower_path = path.lower()

        if filename in KEY_FILENAMES:
            key_files.append(path)
        if filename.endswith((".py", ".go", ".ts", ".js", ".java", ".rb")) and not (
            filename.endswith(("_test.py", ".spec.ts", ".test.ts", ".test.js"))
        ):
            modules.append(path)
        if any(p in lower_path for p in CONFIG_PATTERNS) or filename.endswith((".yml", ".yaml", ".toml", ".ini", ".conf", ".env")):
            configs.append(path)

    return {
        "key_files": sorted(set(key_files)),
        "modules": sorted(set(modules)),
        "configs": sorted(set(configs)),
    }


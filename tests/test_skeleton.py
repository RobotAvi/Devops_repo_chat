from src.structure_parser import parse_tree


def test_parse_tree_basic():
    tree = [
        {"type": "blob", "path": "README.md"},
        {"type": "blob", "path": "app/main.py"},
        {"type": "blob", "path": "config/settings.yaml"},
        {"type": "tree", "path": "tests"},
    ]
    parsed = parse_tree(tree)
    assert "README.md" in parsed["key_files"]
    assert "app/main.py" in parsed["modules"]
    assert any("config" in p for p in parsed["configs"])  # heuristic


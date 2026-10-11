"""Import rules from docs/architecture.md section 2."""

import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2] / "src" / "steam_reviews"

FORBIDDEN = {
    "domain": ("steam_reviews.application", "steam_reviews.infrastructure", "steam_reviews.presentation",
               "steam_reviews.bootstrap", "pyspark", "pandas", "streamlit"),
    "application": ("steam_reviews.infrastructure", "steam_reviews.presentation",
                    "steam_reviews.bootstrap", "pyspark", "pandas", "streamlit"),
    "infrastructure": ("steam_reviews.presentation", "steam_reviews.bootstrap"),
    "presentation": ("steam_reviews.infrastructure", "pyspark"),
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_imports(layer):
    violations = []
    for path in (PACKAGE / layer).rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith(FORBIDDEN[layer]):
                violations.append(f"{path.relative_to(PACKAGE)} imports {module}")
    assert violations == []

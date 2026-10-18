"""Architecture fitness functions asserting strict Clean Architecture layer boundaries.

Ensures that dependencies flow strictly inwards:
  ui / api -> services -> domain
  repository -> domain
Domain must remain completely isolated from outer layers, persistence drivers, and UI/web frameworks.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"


def _get_imports(directory: Path) -> list[tuple[str, str]]:
    """Extracts all imported module names from all python files in the directory."""
    imports: list[tuple[str, str]] = []
    for file_path in directory.rglob("*.py"):
        if file_path.name.startswith("__"):
            continue
        rel_path = file_path.relative_to(SRC_DIR.parent).as_posix()
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((rel_path, alias.name))
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append((rel_path, node.module))
    return imports


def test_domain_layer_isolation_has_no_outer_or_framework_dependencies():
    """Domain layer must not depend on services, repository, api, ui, or frameworks."""
    forbidden_prefixes = (
        "src.services",
        "src.repository",
        "src.api",
        "src.ui",
        "fastapi",
        "starlette",
        "streamlit",
        "sqlalchemy",
        "reportlab",
    )
    domain_imports = _get_imports(SRC_DIR / "domain")
    violations = [
        f"{source} imports {module}"
        for source, module in domain_imports
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_prefixes)
    ]
    assert not violations, f"Domain layer violations detected: {violations}"


def test_services_layer_does_not_depend_on_presentation():
    """Services layer must not depend on UI or REST API presentation layers."""
    forbidden_prefixes = (
        "src.api",
        "src.ui",
        "fastapi",
        "starlette",
        "streamlit",
    )
    service_imports = _get_imports(SRC_DIR / "services")
    violations = [
        f"{source} imports {module}"
        for source, module in service_imports
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_prefixes)
    ]
    assert not violations, f"Services layer violations detected: {violations}"


def test_repository_layer_does_not_depend_on_presentation():
    """Repository layer must not depend on UI or REST API presentation layers."""
    forbidden_prefixes = (
        "src.api",
        "src.ui",
        "fastapi",
        "starlette",
        "streamlit",
    )
    repo_imports = _get_imports(SRC_DIR / "repository")
    violations = [
        f"{source} imports {module}"
        for source, module in repo_imports
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_prefixes)
    ]
    assert not violations, f"Repository layer violations detected: {violations}"

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from app.core.logging import logger

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".dart": "Dart",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
}

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "target",
    "vendor",
    ".dart_tool",
}


class AnalysisService:
    @classmethod
    def scan_languages(cls, workspace_dir: Path) -> Dict[str, int]:
        """Calculates language composition based on lines of code."""
        counts: Dict[str, int] = {}
        for root, dirs, files in os.walk(workspace_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                ext = Path(file).suffix.lower()
                lang = LANGUAGE_EXTENSIONS.get(ext)
                if lang:
                    file_path = Path(root) / file
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            lines = sum(1 for _ in f)
                            counts[lang] = counts.get(lang, 0) + lines
                    except Exception:
                        continue
        return counts

    @classmethod
    def detect_frameworks(cls, workspace_dir: Path) -> List[str]:
        """Detects frameworks by recursively inspecting manifest files."""
        frameworks = set()

        for root, dirs, files in os.walk(workspace_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                fpath = Path(root) / file
                fname = file.lower()

                # Flutter & Dart
                if fname == "pubspec.yaml":
                    frameworks.add("Dart")
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        if "flutter:" in content or "flutter_test:" in content:
                            frameworks.add("Flutter")
                        if "provider:" in content:
                            frameworks.add("Provider (State)")
                        if "bloc:" in content or "flutter_bloc:" in content:
                            frameworks.add("BLoC")
                        if "riverpod:" in content:
                            frameworks.add("Riverpod")
                    except Exception:
                        pass

                # Node / JS
                elif fname == "package.json":
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        if "next" in content:
                            frameworks.add("Next.js")
                        if "react" in content:
                            frameworks.add("React")
                        if "express" in content:
                            frameworks.add("Express")
                        if "fastify" in content:
                            frameworks.add("Fastify")
                        if "vue" in content:
                            frameworks.add("Vue")
                        if "svelte" in content:
                            frameworks.add("Svelte")
                    except Exception:
                        pass

                # Python
                elif fname in ["requirements.txt", "pyproject.toml", "pipfile", "setup.py"]:
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore").lower()
                        if "fastapi" in content:
                            frameworks.add("FastAPI")
                        if "django" in content:
                            frameworks.add("Django")
                        if "flask" in content:
                            frameworks.add("Flask")
                        if "sqlalchemy" in content:
                            frameworks.add("SQLAlchemy")
                        if "tornado" in content:
                            frameworks.add("Tornado")
                        if "langgraph" in content:
                            frameworks.add("LangGraph")
                        if "langchain" in content:
                            frameworks.add("LangChain")
                    except Exception:
                        pass

                # Go
                elif fname == "go.mod":
                    frameworks.add("Go Modules")

                # Rust
                elif fname == "cargo.toml":
                    frameworks.add("Cargo / Rust")

        return sorted(list(frameworks))

    @classmethod
    def find_entry_points(cls, workspace_dir: Path) -> List[str]:
        """Finds primary application entry points."""
        candidates = [
            "app/app.py",
            "app/main.py",
            "src/main.py",
            "src/app.py",
            "lib/main.dart",
            "main.dart",
            "main.py",
            "app.py",
            "server.py",
            "index.ts",
            "index.js",
            "src/index.ts",
            "src/index.js",
            "cmd/main.go",
            "src/main.rs",
        ]
        found = []
        for c in candidates:
            if (workspace_dir / c).exists():
                found.append(c)
        return found

    @classmethod
    def parse_python_imports(cls, file_path: Path) -> List[str]:
        """Extracts imported module names from a Python source file using AST."""
        imports = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])
        except Exception:
            pass
        return list(set(imports))

    @classmethod
    def parse_dart_imports(cls, file_path: Path) -> List[str]:
        """Extracts imported packages/files from a Dart source file."""
        imports = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            matches = re.findall(r"import\s+['\"]([^'\"]+)['\"]", content)
            for m in matches:
                if m.startswith("package:"):
                    pkg = m.replace("package:", "").split("/")[0]
                    imports.append(pkg)
                else:
                    imports.append(Path(m).stem)
        except Exception:
            pass
        return list(set(imports))

    @classmethod
    def detect_circular_dependencies(cls, raw_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Finds circular dependencies using Tarjan's Strongly Connected Components algorithm."""
        normalized_graph: Dict[str, List[str]] = {}
        for src, targets in raw_graph.items():
            norm_src = Path(src).stem
            norm_targets = [Path(t).stem for t in targets]
            normalized_graph[norm_src] = norm_targets

        index = 0
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        on_stack: Set[str] = set()
        stack: List[str] = []
        sccs: List[List[str]] = []

        def strongconnect(node: str):
            nonlocal index
            indices[node] = index
            lowlinks[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)

            for neighbor in normalized_graph.get(node, []):
                if neighbor not in indices:
                    strongconnect(neighbor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
                elif neighbor in on_stack:
                    lowlinks[node] = min(lowlinks[node], indices[neighbor])

            if lowlinks[node] == indices[node]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == node:
                        break
                if len(scc) > 1:
                    sccs.append(scc)

        for node in list(normalized_graph.keys()):
            if node not in indices:
                strongconnect(node)

        return sccs

    @classmethod
    def analyze_architecture(cls, workspace_dir: Path) -> Dict[str, Any]:
        """Generates comprehensive architecture metrics and graphs."""
        languages = cls.scan_languages(workspace_dir)
        frameworks = cls.detect_frameworks(workspace_dir)
        entry_points = cls.find_entry_points(workspace_dir)

        dep_graph: Dict[str, List[str]] = {}
        routes: List[Dict[str, str]] = []

        for root, dirs, files in os.walk(workspace_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                ext = Path(file).suffix.lower()
                rel_path = str(Path(root, file).relative_to(workspace_dir)).replace("\\", "/")
                abs_path = Path(root) / file

                if ext == ".py":
                    imports = cls.parse_python_imports(abs_path)
                    dep_graph[rel_path] = imports

                    try:
                        content = abs_path.read_text(encoding="utf-8", errors="ignore")
                        # FastAPI / modern routes: @app.get('/...')
                        for match in re.finditer(r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', content):
                            routes.append({"method": match.group(1).upper(), "path": match.group(2), "file": rel_path})
                        # Flask routes: @app.route('/path', methods=['GET', 'POST'])
                        for match in re.finditer(r'@app\.route\(["\']([^"\']+)["\'](?:,\s*methods\s*=\s*\[([^\]]+)\])?', content):
                            route_path = match.group(1)
                            methods = match.group(2) or "'GET'"
                            for m in re.findall(r"['\"]([A-Z]+)['\"]", methods):
                                routes.append({"method": m, "path": route_path, "file": rel_path})
                    except Exception:
                        pass
                elif ext == ".dart":
                    imports = cls.parse_dart_imports(abs_path)
                    dep_graph[rel_path] = imports

        circular = cls.detect_circular_dependencies(dep_graph)

        summary = (
            f"Analyzed codebase with {sum(languages.values())} lines of code. "
            f"Detected primary stack: {', '.join(frameworks) if frameworks else 'Standard Library'}. "
            f"Discovered {len(entry_points)} entry points and {len(routes)} exposed API routes. "
            f"Found {len(circular)} circular import cycles."
        )

        return {
            "languages": languages,
            "frameworks": frameworks,
            "entry_points": entry_points,
            "modules_count": len(dep_graph),
            "circular_dependencies": circular,
            "dependencies_graph": {k: v for k, v in list(dep_graph.items())[:50]},
            "api_routes": routes,
            "summary": summary,
        }

"""
Map Dependencies Skill

Traces and maps imports, dependencies, and module relationships in codebases.
Addresses Gap #3: Understanding Legacy Code.
"""

import ast
import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Load schema
SCHEMA_PATH = Path(__file__).parent / "schema.json"
with open(SCHEMA_PATH, encoding="utf-8") as f:
    SKILL_SCHEMA = json.load(f)

app = FastAPI(
    title=SKILL_SCHEMA["name"],
    description=SKILL_SCHEMA["description"]["long"],
    version=SKILL_SCHEMA["version"],
)


# ============================================================================
# Request/Response Models
# ============================================================================


class ExecuteInputs(BaseModel):
    """Input parameters for dependency mapping."""

    source_path: str = Field(..., description="Path to file or directory to analyze")
    language: Optional[str] = Field(default="auto")
    depth: int = Field(default=3, ge=-1)
    include_external: bool = Field(default=True)
    output_format: str = Field(default="summary")


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint."""

    inputs: ExecuteInputs
    context: Optional[Dict[str, Any]] = None


class InternalDependency(BaseModel):
    """Internal dependency information."""

    source: str
    target: str
    import_type: str
    symbols: List[str] = []


class ExternalDependency(BaseModel):
    """External dependency information."""

    name: str
    used_in: List[str] = []
    import_count: int = 0


class GraphNode(BaseModel):
    """Node in dependency graph."""

    id: str
    type: str
    path: str


class GraphEdge(BaseModel):
    """Edge in dependency graph."""

    source: str
    target: str
    weight: int = 1


class DependencyGraph(BaseModel):
    """Dependency graph structure."""

    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []


class HighlyDepended(BaseModel):
    """Highly depended files."""

    path: str
    dependents_count: int


class MapOutputs(BaseModel):
    """Output of dependency mapping."""

    summary: str
    total_dependencies: int = 0
    internal_dependencies: List[InternalDependency] = []
    external_dependencies: List[ExternalDependency] = []
    dependency_graph: DependencyGraph = DependencyGraph()
    circular_dependencies: List[List[str]] = []
    entry_points: List[str] = []
    highly_depended: List[HighlyDepended] = []


class ExecuteResponse(BaseModel):
    """Response model for successful execution."""

    status: str = "success"
    outputs: MapOutputs
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Language Detection
# ============================================================================

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
}


def detect_language(file_path: str) -> str:
    """Detect language from file extension."""
    ext = Path(file_path).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext, "unknown")


def get_source_files(path: str, language: str = "auto") -> List[str]:
    """Get list of source files to analyze."""
    path_obj = Path(path)

    if path_obj.is_file():
        return [str(path_obj)]

    if not path_obj.is_dir():
        return []

    files = []
    extensions = (
        list(EXTENSION_TO_LANGUAGE.keys())
        if language == "auto"
        else [ext for ext, lang in EXTENSION_TO_LANGUAGE.items() if lang == language]
    )

    for ext in extensions:
        files.extend(str(f) for f in path_obj.rglob(f"*{ext}"))

    return files


# ============================================================================
# Python Dependency Parser
# ============================================================================


class PythonImportVisitor(ast.NodeVisitor):
    """AST visitor to extract Python imports."""

    def __init__(self):
        self.imports: List[Tuple[str, str, List[str]]] = []  # (module, type, symbols)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append((alias.name, "direct", [alias.asname or alias.name]))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        symbols = [alias.name for alias in node.names]
        self.imports.append((module, "from", symbols))
        self.generic_visit(node)


def parse_python_imports(code: str) -> List[Tuple[str, str, List[str]]]:
    """Parse Python imports from code."""
    try:
        tree = ast.parse(code)
        visitor = PythonImportVisitor()
        visitor.visit(tree)
        return visitor.imports
    except SyntaxError:
        # Fallback to regex for invalid syntax
        return parse_python_imports_regex(code)


def parse_python_imports_regex(code: str) -> List[Tuple[str, str, List[str]]]:
    """Parse Python imports using regex (fallback)."""
    imports = []

    # Match: import x, y, z
    import_pattern = r"^import\s+([\w\.,\s]+)"
    for match in re.finditer(import_pattern, code, re.MULTILINE):
        modules = [m.strip() for m in match.group(1).split(",")]
        for module in modules:
            if module:
                imports.append((module.split(".")[0], "direct", [module]))

    # Match: from x import y, z
    from_pattern = r"^from\s+([\w\.]+)\s+import\s+([\w\*,\s]+)"
    for match in re.finditer(from_pattern, code, re.MULTILINE):
        module = match.group(1)
        symbols = [s.strip() for s in match.group(2).split(",")]
        imports.append((module, "from", symbols))

    return imports


# ============================================================================
# JavaScript/TypeScript Dependency Parser
# ============================================================================


def parse_js_imports(code: str) -> List[Tuple[str, str, List[str]]]:
    """Parse JavaScript/TypeScript imports."""
    imports = []

    # ES6 imports
    # import x from 'module'
    default_import = r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]"
    for match in re.finditer(default_import, code):
        imports.append((match.group(2), "default", [match.group(1)]))

    # import { x, y } from 'module'
    named_import = r"import\s+\{([^}]+)\}\s+from\s+['\"]([^'\"]+)['\"]"
    for match in re.finditer(named_import, code):
        symbols = [s.strip().split(" as ")[0] for s in match.group(1).split(",")]
        imports.append((match.group(2), "named", symbols))

    # import * as x from 'module'
    namespace_import = r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]"
    for match in re.finditer(namespace_import, code):
        imports.append((match.group(2), "namespace", [match.group(1)]))

    # CommonJS: require('module')
    require_pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*require\s*\(['\"]([^'\"]+)['\"]\)"
    for match in re.finditer(require_pattern, code):
        imports.append((match.group(2), "require", [match.group(1)]))

    # Dynamic import: import('module')
    dynamic_import = r"import\s*\(['\"]([^'\"]+)['\"]\)"
    for match in re.finditer(dynamic_import, code):
        imports.append((match.group(1), "dynamic", []))

    return imports


# ============================================================================
# Java Dependency Parser
# ============================================================================


def parse_java_imports(code: str) -> List[Tuple[str, str, List[str]]]:
    """Parse Java imports."""
    imports = []

    # import x.y.z;
    import_pattern = r"import\s+(?:static\s+)?([\w\.]+)(?:\.\*)?;"
    for match in re.finditer(import_pattern, code):
        full_import = match.group(1)
        is_static = "static" in match.group(0)
        import_type = "static" if is_static else "direct"
        
        # Get the class name (last part) as symbol
        parts = full_import.split(".")
        symbol = parts[-1] if parts else full_import
        imports.append((full_import, import_type, [symbol]))

    return imports


# ============================================================================
# Go Dependency Parser
# ============================================================================


def parse_go_imports(code: str) -> List[Tuple[str, str, List[str]]]:
    """Parse Go imports."""
    imports = []

    # Single import: import "module"
    single_import = r'import\s+"([^"]+)"'
    for match in re.finditer(single_import, code):
        imports.append((match.group(1), "direct", []))

    # Import block: import ( "module1" \n "module2" )
    block_pattern = r"import\s*\(([\s\S]*?)\)"
    for match in re.finditer(block_pattern, code):
        block = match.group(1)
        # Parse aliases and paths
        line_pattern = r'(?:(\w+)\s+)?"([^"]+)"'
        for line_match in re.finditer(line_pattern, block):
            alias = line_match.group(1) or ""
            path = line_match.group(2)
            import_type = "aliased" if alias else "direct"
            imports.append((path, import_type, [alias] if alias else []))

    return imports


# ============================================================================
# Dependency Classification
# ============================================================================

# Standard library modules by language
PYTHON_STDLIB = {
    "os", "sys", "re", "json", "time", "datetime", "pathlib", "collections",
    "itertools", "functools", "typing", "abc", "ast", "io", "math", "random",
    "subprocess", "threading", "multiprocessing", "logging", "unittest",
    "argparse", "configparser", "dataclasses", "enum", "copy", "hashlib",
    "base64", "urllib", "http", "socket", "email", "html", "xml", "sqlite3",
}

JAVASCRIPT_BUILTIN = {
    "fs", "path", "http", "https", "crypto", "os", "child_process", "events",
    "stream", "util", "url", "querystring", "assert", "buffer", "cluster",
    "dns", "net", "process", "readline", "tls", "vm", "zlib",
}


def is_external_dependency(module: str, language: str, source_file: str = "") -> bool:
    """Determine if a module is external (third-party) or internal."""
    # Relative imports are internal
    if module.startswith("."):
        return False

    if language == "python":
        root_module = module.split(".")[0]
        return root_module not in PYTHON_STDLIB

    elif language in ("javascript", "typescript"):
        # Paths starting with . or / are local
        if module.startswith(".") or module.startswith("/"):
            return False
        # Node built-ins
        if module in JAVASCRIPT_BUILTIN or module.startswith("node:"):
            return True  # Treat as external (not project code)
        # npm packages
        return True

    elif language == "java":
        # java.* and javax.* are standard
        return not (module.startswith("java.") or module.startswith("javax."))

    elif language == "go":
        # Standard library has no dots in path
        return "." in module or "/" in module

    return True


# ============================================================================
# Dependency Mapping
# ============================================================================


def parse_file_imports(file_path: str, language: str) -> List[Tuple[str, str, List[str]]]:
    """Parse imports from a single file."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception:
        return []

    if language == "python":
        return parse_python_imports(code)
    elif language in ("javascript", "typescript"):
        return parse_js_imports(code)
    elif language == "java":
        return parse_java_imports(code)
    elif language == "go":
        return parse_go_imports(code)
    else:
        return []


def find_circular_dependencies(edges: Dict[str, Set[str]]) -> List[List[str]]:
    """Find circular dependencies using DFS."""
    cycles = []
    visited = set()
    rec_stack = []

    def dfs(node: str, path: List[str]):
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            if len(cycle) > 1 and cycle not in cycles:
                cycles.append(cycle)
            return

        if node in visited:
            return

        visited.add(node)
        rec_stack.append(node)

        for neighbor in edges.get(node, set()):
            dfs(neighbor, path + [node])

        rec_stack.pop()

    for node in edges:
        if node not in visited:
            dfs(node, [])

    return cycles[:10]  # Limit to 10 cycles


def map_dependencies(inputs: ExecuteInputs) -> MapOutputs:
    """Perform full dependency mapping."""
    source_path = inputs.source_path
    language = inputs.language

    # Check if path exists
    if not Path(source_path).exists():
        return MapOutputs(
            summary=f"Path not found: {source_path}",
            total_dependencies=0,
        )

    # Get source files
    source_files = get_source_files(source_path, language)

    if not source_files:
        return MapOutputs(
            summary=f"No source files found in: {source_path}",
            total_dependencies=0,
        )

    # Analyze each file
    internal_deps: List[InternalDependency] = []
    external_deps_map: Dict[str, Dict] = defaultdict(lambda: {"used_in": [], "count": 0})
    edges: Dict[str, Set[str]] = defaultdict(set)
    all_nodes: Set[str] = set()
    external_nodes: Set[str] = set()

    for file_path in source_files:
        file_lang = language if language != "auto" else detect_language(file_path)
        imports = parse_file_imports(file_path, file_lang)
        relative_path = str(Path(file_path).relative_to(Path(source_path).parent) if Path(source_path).is_file() else Path(file_path).relative_to(source_path))

        all_nodes.add(relative_path)

        for module, import_type, symbols in imports:
            if not module:
                continue

            is_external = is_external_dependency(module, file_lang, file_path)

            if is_external:
                if inputs.include_external:
                    root_module = module.split("/")[0].split(".")[0]
                    external_deps_map[root_module]["used_in"].append(relative_path)
                    external_deps_map[root_module]["count"] += 1
                    external_nodes.add(root_module)
            else:
                internal_deps.append(InternalDependency(
                    source=relative_path,
                    target=module,
                    import_type=import_type,
                    symbols=symbols,
                ))
                edges[relative_path].add(module)
                all_nodes.add(module)

    # Build external dependency list
    external_deps = [
        ExternalDependency(
            name=name,
            used_in=list(set(info["used_in"]))[:10],
            import_count=info["count"],
        )
        for name, info in sorted(external_deps_map.items(), key=lambda x: x[1]["count"], reverse=True)
    ]

    # Build graph
    graph_nodes = [
        GraphNode(id=node, type="internal", path=node) for node in all_nodes
    ] + [
        GraphNode(id=node, type="external", path=node) for node in external_nodes
    ]

    graph_edges = []
    for source, targets in edges.items():
        for target in targets:
            graph_edges.append(GraphEdge(source=source, target=target, weight=1))

    # Find circular dependencies
    circular = find_circular_dependencies(edges)

    # Find entry points (nodes with no incoming edges)
    targets = set()
    for t_set in edges.values():
        targets.update(t_set)
    entry_points = [n for n in all_nodes if n not in targets and n in edges]

    # Find highly depended files
    dependent_counts: Dict[str, int] = defaultdict(int)
    for target in targets:
        dependent_counts[target] = sum(1 for deps in edges.values() if target in deps)

    highly_depended = [
        HighlyDepended(path=path, dependents_count=count)
        for path, count in sorted(dependent_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # Build summary
    total = len(internal_deps) + len(external_deps)
    summary_parts = [
        f"Analyzed {len(source_files)} file(s).",
        f"Found {len(internal_deps)} internal and {len(external_deps)} external dependencies.",
    ]
    if circular:
        summary_parts.append(f"Detected {len(circular)} circular dependency chain(s).")
    if highly_depended:
        top = highly_depended[0]
        summary_parts.append(f"Most depended: {top.path} ({top.dependents_count} dependents).")

    return MapOutputs(
        summary=" ".join(summary_parts),
        total_dependencies=total,
        internal_dependencies=internal_deps[:100],  # Limit to 100
        external_dependencies=external_deps[:50],  # Limit to 50
        dependency_graph=DependencyGraph(nodes=graph_nodes[:200], edges=graph_edges[:500]),
        circular_dependencies=circular,
        entry_points=entry_points[:20],
        highly_depended=highly_depended,
    )


# ============================================================================
# API Endpoints
# ============================================================================


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute the dependency mapping skill."""
    start_time = time.time()

    try:
        outputs = map_dependencies(request.inputs)
        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecuteResponse(
            outputs=outputs,
            metadata={
                "execution_time_ms": execution_time_ms,
                "source_path": request.inputs.source_path,
                "language": request.inputs.language,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": SKILL_SCHEMA["version"],
        "skill_id": SKILL_SCHEMA["id"],
    }


@app.get("/describe")
async def describe():
    """Return the skill's schema."""
    return SKILL_SCHEMA


# ============================================================================
# Development Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Code Summarizer Skill

Summarizes source code files or functions with structural and contextual understanding.
Addresses Gap #3: Understanding Legacy Code.
"""

import ast
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    """Input parameters for code summarization."""

    code: str = Field(..., description="The source code to summarize")
    language: str = Field(default="auto", description="Programming language")
    context: Optional[str] = Field(default=None, description="Optional context")
    detail_level: str = Field(default="standard", pattern="^(brief|standard|detailed)$")
    focus: str = Field(default="all", pattern="^(purpose|structure|behavior|all)$")


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint."""

    inputs: ExecuteInputs
    context: Optional[Dict[str, Any]] = None


class KeyComponent(BaseModel):
    """A key component identified in the code."""

    name: str
    type: str
    description: str


class ComplexityIndicators(BaseModel):
    """Metrics indicating code complexity."""

    lines_of_code: int
    num_functions: int
    num_classes: int
    estimated_complexity: str


class SummarizeOutputs(BaseModel):
    """Output of code summarization."""

    summary: str
    purpose: str
    key_components: List[KeyComponent] = []
    dependencies: List[str] = []
    complexity_indicators: Optional[ComplexityIndicators] = None
    notable_patterns: List[str] = []


class ExecuteResponse(BaseModel):
    """Response model for successful execution."""

    status: str = "success"
    outputs: SummarizeOutputs
    metadata: Optional[Dict[str, Any]] = None


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Response model for errors."""

    status: str = "error"
    error: ErrorDetail


# ============================================================================
# Code Analysis Engine
# ============================================================================


class PythonAnalyzer:
    """Analyze Python source code using AST."""

    def __init__(self, code: str):
        self.code = code
        self.tree = None
        self.parse_error = None
        try:
            self.tree = ast.parse(code)
        except SyntaxError as e:
            self.parse_error = str(e)

    def get_functions(self) -> List[Dict[str, str]]:
        """Extract function definitions."""
        if self.tree is None:
            return []

        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                docstring = ast.get_docstring(node) or "No description"
                functions.append({
                    "name": node.name,
                    "type": "async function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                    "description": docstring.split("\n")[0],  # First line of docstring
                })
        return functions

    def get_classes(self) -> List[Dict[str, str]]:
        """Extract class definitions."""
        if self.tree is None:
            return []

        classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or "No description"
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "type": "class",
                    "description": f"{docstring.split(chr(10))[0]} (methods: {', '.join(methods[:3])}{'...' if len(methods) > 3 else ''})",
                })
        return classes

    def get_imports(self) -> List[str]:
        """Extract import statements."""
        if self.tree is None:
            return []

        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
        return list(set(imports))

    def get_complexity_indicators(self) -> Dict[str, Any]:
        """Calculate complexity metrics."""
        lines = self.code.count("\n") + 1
        num_functions = len(self.get_functions())
        num_classes = len(self.get_classes())

        # Simple complexity estimation
        if lines < 50 and num_functions < 5:
            complexity = "low"
        elif lines < 200 and num_functions < 15:
            complexity = "medium"
        else:
            complexity = "high"

        return {
            "lines_of_code": lines,
            "num_functions": num_functions,
            "num_classes": num_classes,
            "estimated_complexity": complexity,
        }

    def detect_patterns(self) -> List[str]:
        """Detect common design patterns."""
        patterns = []

        # Singleton pattern
        if re.search(r"_instance\s*=\s*None|__new__\s*\(", self.code):
            patterns.append("Singleton pattern detected")

        # Decorator pattern
        if re.search(r"@\w+\s*\n\s*def ", self.code):
            patterns.append("Uses decorators")

        # Context manager
        if re.search(r"__enter__|__exit__|with\s+\w+", self.code):
            patterns.append("Context manager pattern")

        # Factory pattern
        if re.search(r"def\s+create_|def\s+make_|Factory", self.code):
            patterns.append("Factory pattern detected")

        # Async/await
        if re.search(r"async\s+def|await\s+", self.code):
            patterns.append("Asynchronous programming")

        # Error handling
        if re.search(r"try:|except\s+\w+:", self.code):
            patterns.append("Exception handling")

        # Type hints
        if re.search(r"def\s+\w+\([^)]*:\s*\w+", self.code):
            patterns.append("Uses type hints")

        return patterns


class GenericAnalyzer:
    """Generic analyzer for non-Python code."""

    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language

    def get_functions(self) -> List[Dict[str, str]]:
        """Extract function-like definitions using regex."""
        functions = []

        # JavaScript/TypeScript
        if self.language in ("javascript", "typescript", "js", "ts"):
            pattern = r"(?:async\s+)?function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\("
            for match in re.finditer(pattern, self.code):
                name = match.group(1) or match.group(2)
                if name:
                    functions.append({
                        "name": name,
                        "type": "function",
                        "description": "JavaScript function",
                    })

        # Java/C#
        elif self.language in ("java", "csharp", "cs"):
            pattern = r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)\s*\{"
            for match in re.finditer(pattern, self.code):
                functions.append({
                    "name": match.group(1),
                    "type": "method",
                    "description": "Method definition",
                })

        # Go
        elif self.language == "go":
            pattern = r"func\s+(?:\([^)]+\)\s*)?(\w+)\s*\("
            for match in re.finditer(pattern, self.code):
                functions.append({
                    "name": match.group(1),
                    "type": "function",
                    "description": "Go function",
                })

        return functions

    def get_classes(self) -> List[Dict[str, str]]:
        """Extract class-like definitions."""
        classes = []

        # JavaScript/TypeScript class
        if self.language in ("javascript", "typescript", "js", "ts"):
            pattern = r"class\s+(\w+)"
            for match in re.finditer(pattern, self.code):
                classes.append({
                    "name": match.group(1),
                    "type": "class",
                    "description": "JavaScript/TypeScript class",
                })

        # Java/C# class
        elif self.language in ("java", "csharp", "cs"):
            pattern = r"(?:public|private)?\s*class\s+(\w+)"
            for match in re.finditer(pattern, self.code):
                classes.append({
                    "name": match.group(1),
                    "type": "class",
                    "description": "Class definition",
                })

        # Go struct
        elif self.language == "go":
            pattern = r"type\s+(\w+)\s+struct"
            for match in re.finditer(pattern, self.code):
                classes.append({
                    "name": match.group(1),
                    "type": "struct",
                    "description": "Go struct",
                })

        return classes

    def get_imports(self) -> List[str]:
        """Extract imports/includes."""
        imports = []

        # JavaScript/TypeScript
        if self.language in ("javascript", "typescript", "js", "ts"):
            pattern = r"(?:import\s+.*?from\s+['\"]([^'\"]+)['\"]|require\s*\(['\"]([^'\"]+)['\"]\))"
            for match in re.finditer(pattern, self.code):
                imports.append(match.group(1) or match.group(2))

        # Java
        elif self.language == "java":
            pattern = r"import\s+([\w.]+);"
            for match in re.finditer(pattern, self.code):
                imports.append(match.group(1))

        # Go
        elif self.language == "go":
            pattern = r'import\s+(?:\(\s*)?"([^"]+)"'
            for match in re.finditer(pattern, self.code):
                imports.append(match.group(1))

        # C/C++
        elif self.language in ("c", "cpp", "c++"):
            pattern = r'#include\s*[<"]([^>"]+)[>"]'
            for match in re.finditer(pattern, self.code):
                imports.append(match.group(1))

        return list(set(imports))

    def get_complexity_indicators(self) -> Dict[str, Any]:
        """Calculate basic complexity metrics."""
        lines = self.code.count("\n") + 1
        num_functions = len(self.get_functions())
        num_classes = len(self.get_classes())

        if lines < 100 and num_functions < 10:
            complexity = "low"
        elif lines < 500 and num_functions < 30:
            complexity = "medium"
        else:
            complexity = "high"

        return {
            "lines_of_code": lines,
            "num_functions": num_functions,
            "num_classes": num_classes,
            "estimated_complexity": complexity,
        }


def detect_language(code: str) -> str:
    """Auto-detect programming language from code."""
    # Python indicators
    if re.search(r"def\s+\w+\s*\(|import\s+\w+|from\s+\w+\s+import", code):
        return "python"

    # JavaScript/TypeScript
    if re.search(r"const\s+\w+\s*=|let\s+\w+\s*=|function\s+\w+|=>\s*\{", code):
        if re.search(r":\s*(string|number|boolean|any)\s*[;=,)]", code):
            return "typescript"
        return "javascript"

    # Java
    if re.search(r"public\s+class\s+\w+|private\s+\w+\s+\w+\s*\(|System\.out", code):
        return "java"

    # Go
    if re.search(r"package\s+\w+|func\s+\w+|:=", code):
        return "go"

    # C/C++
    if re.search(r"#include\s*<|int\s+main\s*\(|printf\s*\(", code):
        return "c"

    return "unknown"


def generate_summary(
    code: str,
    language: str,
    detail_level: str,
    focus: str,
    context: Optional[str] = None,
) -> SummarizeOutputs:
    """Generate a comprehensive summary of the code."""

    # Detect language if auto
    if language == "auto":
        language = detect_language(code)

    # Use appropriate analyzer
    if language == "python":
        analyzer = PythonAnalyzer(code)
    else:
        analyzer = GenericAnalyzer(code, language)

    # Extract components
    functions = analyzer.get_functions()
    if hasattr(analyzer, "get_classes"):
        classes = analyzer.get_classes()
    else:
        classes = []

    imports = analyzer.get_imports() if hasattr(analyzer, "get_imports") else []
    complexity = analyzer.get_complexity_indicators()
    patterns = analyzer.detect_patterns() if hasattr(analyzer, "detect_patterns") else []

    # Combine key components
    key_components = [
        KeyComponent(name=c["name"], type=c["type"], description=c["description"])
        for c in (classes + functions)[:10]  # Limit to top 10
    ]

    # Generate purpose statement
    if classes and not functions:
        purpose = f"Defines {len(classes)} class(es) for {language} application"
    elif functions and not classes:
        purpose = f"Provides {len(functions)} utility function(s)"
    elif classes and functions:
        purpose = f"Implements {len(classes)} class(es) with {len(functions)} function(s)"
    else:
        purpose = "Code snippet with no clear structural elements"

    # Add context to purpose if provided
    if context:
        purpose = f"{context}. {purpose}"

    # Generate summary based on detail level
    if detail_level == "brief":
        summary = f"{language.title()} code with {complexity['lines_of_code']} lines. {purpose}."
    elif detail_level == "detailed":
        component_names = [c.name for c in key_components[:5]]
        pattern_str = f" Patterns: {', '.join(patterns[:3])}." if patterns else ""
        summary = (
            f"{language.title()} code ({complexity['lines_of_code']} lines, "
            f"{complexity['estimated_complexity']} complexity). "
            f"Key components: {', '.join(component_names) if component_names else 'none identified'}. "
            f"Dependencies: {', '.join(imports[:5]) if imports else 'none'}.{pattern_str}"
        )
    else:  # standard
        summary = (
            f"{language.title()} code with {complexity['lines_of_code']} lines "
            f"({complexity['estimated_complexity']} complexity). {purpose}."
        )

    return SummarizeOutputs(
        summary=summary,
        purpose=purpose,
        key_components=key_components,
        dependencies=imports[:20],
        complexity_indicators=ComplexityIndicators(**complexity),
        notable_patterns=patterns,
    )


# ============================================================================
# API Endpoints
# ============================================================================


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute the code summarization skill."""
    start_time = time.time()

    try:
        inputs = request.inputs
        outputs = generate_summary(
            code=inputs.code,
            language=inputs.language,
            detail_level=inputs.detail_level,
            focus=inputs.focus,
            context=inputs.context,
        )

        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecuteResponse(
            outputs=outputs,
            metadata={
                "execution_time_ms": execution_time_ms,
                "language_detected": inputs.language if inputs.language != "auto" else detect_language(inputs.code),
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

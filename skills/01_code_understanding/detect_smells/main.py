"""
Detect Code Smells and Survivor Patterns Skill

Identifies code smells and patterns that 'survived for a reason' in legacy code.
Addresses Gap #3: Understanding Legacy Code.
"""

import ast
import json
import re
import time
from dataclasses import dataclass, field
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


class CodeContext(BaseModel):
    """Additional context about the code."""

    file_path: Optional[str] = None
    age_years: Optional[float] = None
    framework: Optional[str] = None
    is_generated: Optional[bool] = None


class ExecuteInputs(BaseModel):
    """Input parameters for smell detection."""

    code: str = Field(..., description="Source code to analyze")
    language: Optional[str] = Field(default="auto")
    context: Optional[CodeContext] = None
    severity_threshold: str = Field(default="info")


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint."""

    inputs: ExecuteInputs
    context: Optional[Dict[str, Any]] = None


class SmellInfo(BaseModel):
    """Information about a detected smell."""

    id: str
    name: str
    severity: str
    line: int
    description: str
    likely_reason: str
    is_survivor: bool
    suggestion: str


class SurvivorPattern(BaseModel):
    """A pattern that looks intentional."""

    pattern: str
    evidence: str
    respect_recommendation: str


class CodeMetrics(BaseModel):
    """Code quality metrics."""

    cyclomatic_complexity: int = 0
    lines_of_code: int = 0
    comment_ratio: float = 0.0
    function_count: int = 0
    max_nesting_depth: int = 0


class DetectOutputs(BaseModel):
    """Output of smell detection."""

    summary: str
    smells: List[SmellInfo] = []
    survivor_patterns: List[SurvivorPattern] = []
    metrics: CodeMetrics = CodeMetrics()
    health_score: int = 100


class ExecuteResponse(BaseModel):
    """Response model for successful execution."""

    status: str = "success"
    outputs: DetectOutputs
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Smell Detection Patterns
# ============================================================================

@dataclass
class SmellPattern:
    """Pattern for detecting a code smell."""

    id: str
    name: str
    severity: str
    pattern: re.Pattern
    description_template: str
    likely_reasons: List[str]
    suggestion: str
    survivor_indicators: List[str] = field(default_factory=list)


# Common code smell patterns
SMELL_PATTERNS = [
    SmellPattern(
        id="long_function",
        name="Long Function",
        severity="warning",
        pattern=re.compile(r"^(def|function|func)\s+\w+", re.MULTILINE),
        description_template="Function appears to be very long ({lines} lines)",
        likely_reasons=[
            "Complex business logic that's hard to decompose",
            "Legacy code that hasn't been refactored",
            "Performance optimization requiring inline code",
        ],
        suggestion="Consider breaking into smaller functions if business logic allows",
        survivor_indicators=["PERF:", "OPTIMIZATION:", "DO NOT SPLIT"],
    ),
    SmellPattern(
        id="magic_number",
        name="Magic Number",
        severity="info",
        pattern=re.compile(r"(?<!['\"\w])\b(?!0\b|1\b|2\b|-1\b)\d{2,}\b(?!['\"])", re.MULTILINE),
        description_template="Unexplained numeric literal: {value}",
        likely_reasons=[
            "Protocol-defined constant (HTTP status, port, etc.)",
            "Business rule value",
            "Configuration that should be extracted",
        ],
        suggestion="Extract to named constant for clarity",
        survivor_indicators=["# HTTP", "# Port", "# RFC", "# Status"],
    ),
    SmellPattern(
        id="deeply_nested",
        name="Deep Nesting",
        severity="warning",
        pattern=re.compile(r"^(\s{16,}|\t{4,})\S", re.MULTILINE),
        description_template="Code nested {depth} levels deep",
        likely_reasons=[
            "Complex validation logic",
            "State machine implementation",
            "Matching external API structure",
        ],
        suggestion="Consider early returns or extracting nested logic",
        survivor_indicators=["state machine", "FSM", "validator"],
    ),
    SmellPattern(
        id="god_class",
        name="God Class",
        severity="error",
        pattern=re.compile(r"^class\s+\w+", re.MULTILINE),
        description_template="Class has too many methods ({count})",
        likely_reasons=[
            "Central coordinator that grew organically",
            "Facade pattern implementation",
            "Legacy monolith component",
        ],
        suggestion="Consider splitting into focused classes using SRP",
        survivor_indicators=["Facade", "Coordinator", "Manager", "Controller"],
    ),
    SmellPattern(
        id="duplicate_code",
        name="Duplicate Code Block",
        severity="warning",
        pattern=re.compile(r"(.{50,})\n.*\1", re.MULTILINE | re.DOTALL),
        description_template="Repeated code block detected",
        likely_reasons=[
            "Copy-paste during rapid development",
            "Similar but subtly different logic",
            "Generated code patterns",
        ],
        suggestion="Extract common logic to shared function",
        survivor_indicators=["# Similar to", "# Copy of", "GENERATED"],
    ),
    SmellPattern(
        id="broad_except",
        name="Broad Exception Handling",
        severity="warning",
        pattern=re.compile(r"except\s*(?:Exception|BaseException|\:)", re.MULTILINE),
        description_template="Catching broad exception type",
        likely_reasons=[
            "Defensive programming against unknown failures",
            "Integration point with unreliable external service",
            "Graceful degradation requirement",
        ],
        suggestion="Catch specific exceptions when possible",
        survivor_indicators=["# fallback", "# graceful", "# external", "WORKAROUND"],
    ),
    SmellPattern(
        id="commented_code",
        name="Commented Out Code",
        severity="info",
        pattern=re.compile(r"^\s*#.*(?:def |class |import |return |if |for |while )", re.MULTILINE),
        description_template="Commented out code detected",
        likely_reasons=[
            "Preserved for rollback",
            "Alternative implementation for future",
            "Debugging leftover",
        ],
        suggestion="Remove if not needed, document if kept intentionally",
        survivor_indicators=["TODO:", "KEEP:", "ALTERNATIVE:", "ROLLBACK:"],
    ),
    SmellPattern(
        id="hardcoded_secret",
        name="Potential Hardcoded Secret",
        severity="error",
        pattern=re.compile(r"(?:password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
        description_template="Possible hardcoded credential",
        likely_reasons=[
            "Development placeholder",
            "Test fixture data",
            "Should be environment variable",
        ],
        suggestion="Move to environment variable or secrets manager",
        survivor_indicators=["# test", "# mock", "# fake", "# placeholder"],
    ),
    SmellPattern(
        id="todo_fixme",
        name="TODO/FIXME Comment",
        severity="info",
        pattern=re.compile(r"#\s*(?:TODO|FIXME|XXX|HACK|BUG):", re.IGNORECASE),
        description_template="Technical debt marker: {marker}",
        likely_reasons=[
            "Known issue awaiting fix",
            "Planned improvement",
            "Workaround documentation",
        ],
        suggestion="Address if possible or create tracking issue",
        survivor_indicators=[],  # These are always intentional
    ),
    SmellPattern(
        id="global_variable",
        name="Global Mutable State",
        severity="warning",
        pattern=re.compile(r"^(?!(?:import|from|def|class|#|@|\s*$))(\w+)\s*=\s*(?:\[|\{|dict\(|list\()", re.MULTILINE),
        description_template="Global mutable variable: {name}",
        likely_reasons=[
            "Configuration storage",
            "Singleton pattern",
            "Module-level cache",
        ],
        suggestion="Consider encapsulating in a class or using dependency injection",
        survivor_indicators=["cache", "registry", "config", "CONFIG", "CACHE"],
    ),
]


# ============================================================================
# Survivor Pattern Detection
# ============================================================================


SURVIVOR_COMMENT_PATTERNS = [
    (r"#\s*WORKAROUND:", "Documented workaround"),
    (r"#\s*INTENTIONAL:", "Explicitly marked as intentional"),
    (r"#\s*DO NOT (?:CHANGE|MODIFY|REMOVE|DELETE)", "Protected code"),
    (r"#\s*REQUIRED BY", "External requirement"),
    (r"#\s*(?:BUG|ISSUE|TICKET)\s*#?\d+", "Linked to issue tracker"),
    (r"#\s*PERFORMANCE:", "Performance optimization"),
    (r"#\s*COMPATIBILITY:", "Compatibility requirement"),
    (r"#\s*LEGACY:", "Legacy support"),
    (r"#\s*API (?:BUG|QUIRK|WORKAROUND)", "External API issue"),
]


def detect_survivor_comments(code: str) -> List[tuple]:
    """Detect comments indicating intentional patterns."""
    survivors = []
    lines = code.split("\n")

    for i, line in enumerate(lines):
        for pattern, description in SURVIVOR_COMMENT_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                survivors.append((i + 1, description, line.strip()))

    return survivors


def is_survivor_pattern(smell: SmellInfo, code: str, survivor_comments: List[tuple]) -> bool:
    """Check if a smell is actually an intentional survivor pattern."""
    # Check if there's a survivor comment nearby (within 3 lines)
    for line_no, _, comment in survivor_comments:
        if abs(line_no - smell.line) <= 3:
            return True

    # Check for inline survivor indicators
    lines = code.split("\n")
    if 0 <= smell.line - 1 < len(lines):
        line = lines[smell.line - 1]
        for pattern in SMELL_PATTERNS:
            if pattern.id == smell.id:
                for indicator in pattern.survivor_indicators:
                    if indicator.lower() in line.lower():
                        return True

    return False


# ============================================================================
# Python AST Analysis
# ============================================================================


class PythonAnalyzer(ast.NodeVisitor):
    """AST-based analyzer for Python code."""

    def __init__(self):
        self.function_count = 0
        self.class_count = 0
        self.function_lengths: List[tuple] = []
        self.class_method_counts: List[tuple] = []
        self.max_nesting = 0
        self.complexity = 0
        self._current_nesting = 0

    def visit_FunctionDef(self, node):
        self.function_count += 1
        end_line = getattr(node, "end_lineno", node.lineno + 10)
        length = end_line - node.lineno
        self.function_lengths.append((node.name, node.lineno, length))
        self._analyze_nesting(node)
        self._count_complexity(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.class_count += 1
        method_count = sum(
            1 for child in ast.walk(node) if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        self.class_method_counts.append((node.name, node.lineno, method_count))
        self.generic_visit(node)

    def _analyze_nesting(self, node):
        """Analyze nesting depth."""
        max_depth = 0

        def visit(n, depth):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            for child in ast.iter_child_nodes(n):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    visit(child, depth + 1)
                else:
                    visit(child, depth)

        visit(node, 0)
        self.max_nesting = max(self.max_nesting, max_depth)

    def _count_complexity(self, node):
        """Count cyclomatic complexity."""
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                self.complexity += 1
            elif isinstance(child, ast.BoolOp):
                self.complexity += len(child.values) - 1


def analyze_python_ast(code: str) -> PythonAnalyzer:
    """Analyze Python code using AST."""
    try:
        tree = ast.parse(code)
        analyzer = PythonAnalyzer()
        analyzer.visit(tree)
        return analyzer
    except SyntaxError:
        return PythonAnalyzer()


# ============================================================================
# Code Metrics
# ============================================================================


def calculate_metrics(code: str, language: str) -> CodeMetrics:
    """Calculate code quality metrics."""
    lines = code.split("\n")
    loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
    comment_lines = len([l for l in lines if l.strip().startswith("#")])
    comment_ratio = comment_lines / max(loc, 1)

    if language == "python":
        analyzer = analyze_python_ast(code)
        return CodeMetrics(
            cyclomatic_complexity=max(1, analyzer.complexity),
            lines_of_code=loc,
            comment_ratio=round(comment_ratio, 2),
            function_count=analyzer.function_count,
            max_nesting_depth=analyzer.max_nesting,
        )
    else:
        # Generic metrics for other languages
        func_pattern = r"(?:def |function |func |fn )\w+"
        function_count = len(re.findall(func_pattern, code))
        return CodeMetrics(
            cyclomatic_complexity=1,
            lines_of_code=loc,
            comment_ratio=round(comment_ratio, 2),
            function_count=function_count,
            max_nesting_depth=0,
        )


# ============================================================================
# Smell Detection
# ============================================================================


def detect_smells(inputs: ExecuteInputs) -> DetectOutputs:
    """Perform smell detection on code."""
    code = inputs.code
    language = inputs.language or "auto"
    context = inputs.context
    severity_levels = {"info": 0, "warning": 1, "error": 2}
    threshold = severity_levels.get(inputs.severity_threshold, 0)

    smells: List[SmellInfo] = []
    lines = code.split("\n")
    total_lines = len(lines)

    # Detect survivor comments first
    survivor_comments = detect_survivor_comments(code)

    # Python-specific AST analysis
    if language in ("auto", "python"):
        try:
            analyzer = analyze_python_ast(code)

            # Long function detection
            for name, line, length in analyzer.function_lengths:
                if length > 50:
                    smells.append(SmellInfo(
                        id="long_function",
                        name="Long Function",
                        severity="warning",
                        line=line,
                        description=f"Function '{name}' is {length} lines long",
                        likely_reason="Complex business logic or organic growth",
                        is_survivor=False,
                        suggestion="Consider breaking into smaller functions",
                    ))

            # God class detection
            for name, line, method_count in analyzer.class_method_counts:
                if method_count > 15:
                    smells.append(SmellInfo(
                        id="god_class",
                        name="God Class",
                        severity="error",
                        line=line,
                        description=f"Class '{name}' has {method_count} methods",
                        likely_reason="Central coordinator or facade pattern",
                        is_survivor=False,
                        suggestion="Consider splitting into focused classes",
                    ))
        except Exception:
            pass

    # Pattern-based detection
    for pattern in SMELL_PATTERNS:
        if pattern.id in ("long_function", "god_class"):
            continue  # Already handled by AST

        for match in pattern.pattern.finditer(code):
            line_no = code[:match.start()].count("\n") + 1

            description = pattern.description_template
            if "{value}" in description:
                description = description.format(value=match.group(0)[:20])
            if "{marker}" in description:
                description = description.format(marker=match.group(0))
            if "{name}" in description:
                description = description.format(name=match.group(1) if match.groups() else "unknown")

            smell = SmellInfo(
                id=pattern.id,
                name=pattern.name,
                severity=pattern.severity,
                line=line_no,
                description=description,
                likely_reason=pattern.likely_reasons[0] if pattern.likely_reasons else "Unknown",
                is_survivor=False,
                suggestion=pattern.suggestion,
            )

            # Check if this is a survivor pattern
            smell.is_survivor = is_survivor_pattern(smell, code, survivor_comments)

            smells.append(smell)

    # Filter by severity threshold
    smells = [s for s in smells if severity_levels.get(s.severity, 0) >= threshold]

    # Remove duplicates (same smell on same line)
    seen = set()
    unique_smells = []
    for smell in smells:
        key = (smell.id, smell.line)
        if key not in seen:
            seen.add(key)
            unique_smells.append(smell)
    smells = unique_smells

    # Build survivor patterns list
    survivor_patterns = []
    for smell in smells:
        if smell.is_survivor:
            survivor_patterns.append(SurvivorPattern(
                pattern=smell.name,
                evidence=f"Line {smell.line}: {smell.description}",
                respect_recommendation="Review before modifying - likely intentional",
            ))

    # Add survivor comments that weren't matched to smells
    for line_no, description, comment in survivor_comments:
        if not any(abs(s.line - line_no) <= 1 for s in smells):
            survivor_patterns.append(SurvivorPattern(
                pattern=description,
                evidence=f"Line {line_no}: {comment}",
                respect_recommendation="Developer left explicit documentation",
            ))

    # Calculate metrics
    metrics = calculate_metrics(code, language)

    # Calculate health score
    error_count = sum(1 for s in smells if s.severity == "error" and not s.is_survivor)
    warning_count = sum(1 for s in smells if s.severity == "warning" and not s.is_survivor)
    info_count = sum(1 for s in smells if s.severity == "info" and not s.is_survivor)

    health_penalty = error_count * 15 + warning_count * 5 + info_count * 1
    health_score = max(0, min(100, 100 - health_penalty))

    # Adjust for code age (older code gets slight leniency)
    if context and context.age_years and context.age_years > 3:
        health_score = min(100, health_score + 5)

    # Build summary
    if not smells:
        summary = "No code smells detected. Code appears clean."
    else:
        parts = [f"Found {len(smells)} issue(s)."]
        if survivor_patterns:
            parts.append(f"{len(survivor_patterns)} appear to be intentional 'survivor' patterns.")
        if error_count:
            parts.append(f"{error_count} error-level issue(s) need attention.")
        summary = " ".join(parts)

    return DetectOutputs(
        summary=summary,
        smells=smells[:50],  # Limit output
        survivor_patterns=survivor_patterns[:20],
        metrics=metrics,
        health_score=health_score,
    )


# ============================================================================
# API Endpoints
# ============================================================================


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute the smell detection skill."""
    start_time = time.time()

    try:
        outputs = detect_smells(request.inputs)
        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecuteResponse(
            outputs=outputs,
            metadata={
                "execution_time_ms": execution_time_ms,
                "language": request.inputs.language,
                "code_length": len(request.inputs.code),
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

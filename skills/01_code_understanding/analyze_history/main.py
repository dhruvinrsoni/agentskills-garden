"""
Git History Analyzer Skill

Analyzes git history to explain why code exists and how it evolved.
Addresses Gap #3: Understanding Legacy Code.
"""

import json
import re
import subprocess
import time
from datetime import datetime
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


class LineRange(BaseModel):
    """Line range specification."""

    start: int = Field(ge=1)
    end: int = Field(ge=1)


class ExecuteInputs(BaseModel):
    """Input parameters for history analysis."""

    file_path: str = Field(..., description="Path to the file to analyze")
    repo_path: str = Field(default=".", description="Path to git repository root")
    line_range: Optional[LineRange] = None
    max_commits: int = Field(default=50, ge=1, le=500)
    include_blame: bool = Field(default=True)


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint."""

    inputs: ExecuteInputs
    context: Optional[Dict[str, Any]] = None


class CreationContext(BaseModel):
    """Context about when/why file was created."""

    created_date: str
    created_by: str
    initial_purpose: str


class TimelineEntry(BaseModel):
    """Entry in the evolution timeline."""

    date: str
    author: str
    message: str
    change_type: str


class ContributorInfo(BaseModel):
    """Information about a contributor."""

    name: str
    commits: int
    lines_contributed: int


class ChangePatterns(BaseModel):
    """Patterns in code changes."""

    total_commits: int
    change_frequency: str
    last_modified: str
    stability_assessment: str


class NotableDecision(BaseModel):
    """A notable decision from history."""

    date: str
    decision: str
    context: str


class AnalyzeOutputs(BaseModel):
    """Output of history analysis."""

    summary: str
    creation_context: Optional[CreationContext] = None
    evolution_timeline: List[TimelineEntry] = []
    key_contributors: List[ContributorInfo] = []
    change_patterns: ChangePatterns
    notable_decisions: List[NotableDecision] = []
    related_files: List[str] = []


class ExecuteResponse(BaseModel):
    """Response model for successful execution."""

    status: str = "success"
    outputs: AnalyzeOutputs
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Git Command Utilities
# ============================================================================


def run_git_command(args: List[str], repo_path: str) -> tuple[bool, str]:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, "Git not found"
    except Exception as e:
        return False, str(e)


def is_git_repo(repo_path: str) -> bool:
    """Check if path is a git repository."""
    success, _ = run_git_command(["rev-parse", "--git-dir"], repo_path)
    return success


def get_file_commits(
    file_path: str,
    repo_path: str,
    max_commits: int,
    line_range: Optional[LineRange] = None,
) -> List[Dict[str, str]]:
    """Get commit history for a file."""
    args = [
        "log",
        f"-{max_commits}",
        "--format=%H|%an|%ae|%ai|%s",
        "--follow",
    ]

    if line_range:
        args.append(f"-L {line_range.start},{line_range.end}:{file_path}")
    else:
        args.append("--")
        args.append(file_path)

    success, output = run_git_command(args, repo_path)
    if not success or not output:
        return []

    commits = []
    for line in output.split("\n"):
        if "|" in line:
            parts = line.split("|", 4)
            if len(parts) >= 5:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4],
                })
    return commits


def get_blame_info(
    file_path: str,
    repo_path: str,
    line_range: Optional[LineRange] = None,
) -> Dict[str, Any]:
    """Get git blame information."""
    args = ["blame", "--porcelain"]
    
    if line_range:
        args.extend([f"-L{line_range.start},{line_range.end}"])
    
    args.append(file_path)
    
    success, output = run_git_command(args, repo_path)
    if not success:
        return {"authors": {}, "line_count": 0}

    authors: Dict[str, int] = {}
    current_author = None
    line_count = 0

    for line in output.split("\n"):
        if line.startswith("author "):
            current_author = line[7:]
        elif line.startswith("\t"):
            line_count += 1
            if current_author:
                authors[current_author] = authors.get(current_author, 0) + 1

    return {"authors": authors, "line_count": line_count}


def get_related_files(file_path: str, repo_path: str, max_commits: int = 20) -> List[str]:
    """Find files frequently changed together with this file."""
    # Get commits that modified this file
    args = ["log", f"-{max_commits}", "--format=%H", "--", file_path]
    success, output = run_git_command(args, repo_path)
    if not success or not output:
        return []

    commit_hashes = output.split("\n")[:max_commits]
    file_counts: Dict[str, int] = {}

    for commit_hash in commit_hashes:
        if not commit_hash:
            continue
        # Get files changed in this commit
        args = ["diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
        success, files_output = run_git_command(args, repo_path)
        if success and files_output:
            for f in files_output.split("\n"):
                if f and f != file_path:
                    file_counts[f] = file_counts.get(f, 0) + 1

    # Sort by frequency and return top 10
    sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
    return [f for f, _ in sorted_files[:10]]


def classify_commit_message(message: str) -> str:
    """Classify commit message to determine change type."""
    message_lower = message.lower()

    if any(word in message_lower for word in ["fix", "bug", "issue", "error", "crash"]):
        return "bugfix"
    elif any(word in message_lower for word in ["feat", "add", "new", "implement"]):
        return "feature"
    elif any(word in message_lower for word in ["refactor", "clean", "improve", "optimize"]):
        return "refactor"
    elif any(word in message_lower for word in ["doc", "comment", "readme"]):
        return "documentation"
    elif any(word in message_lower for word in ["test", "spec"]):
        return "testing"
    elif any(word in message_lower for word in ["merge", "revert"]):
        return "merge"
    else:
        return "update"


def extract_notable_decisions(commits: List[Dict[str, str]]) -> List[NotableDecision]:
    """Extract notable decisions from commit messages."""
    keywords = [
        "because", "due to", "in order to", "to fix", "to prevent",
        "breaking change", "deprecate", "removed", "replaced",
        "IMPORTANT", "BREAKING", "TODO", "FIXME", "refactor"
    ]

    decisions = []
    for commit in commits:
        message = commit["message"]
        if any(keyword.lower() in message.lower() for keyword in keywords):
            # Try to extract the reasoning
            decision = message
            context = classify_commit_message(message)
            
            decisions.append(NotableDecision(
                date=commit["date"][:10],
                decision=decision[:200],  # Truncate long messages
                context=f"Change type: {context}",
            ))
    
    return decisions[:10]  # Return top 10 notable decisions


def assess_stability(commits: List[Dict[str, str]]) -> str:
    """Assess the stability of a file based on its history."""
    if not commits:
        return "unknown"

    if len(commits) == 1:
        return "stable - rarely modified"

    # Parse dates and calculate time spans
    try:
        dates = []
        for c in commits:
            date_str = c["date"][:10]
            dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        
        if len(dates) < 2:
            return "stable"

        # Calculate average days between commits
        dates.sort(reverse=True)
        total_days = (dates[0] - dates[-1]).days
        avg_days_between = total_days / (len(dates) - 1) if len(dates) > 1 else 0

        if avg_days_between > 180:
            return "very stable - changes every 6+ months"
        elif avg_days_between > 30:
            return "stable - changes monthly"
        elif avg_days_between > 7:
            return "moderately active - changes weekly"
        else:
            return "highly active - changes frequently"
    except Exception:
        return "unknown"


def calculate_change_frequency(commits: List[Dict[str, str]]) -> str:
    """Calculate how often the file changes."""
    if not commits:
        return "never"
    elif len(commits) == 1:
        return "once"
    
    try:
        dates = [datetime.strptime(c["date"][:10], "%Y-%m-%d") for c in commits]
        dates.sort()
        total_days = (dates[-1] - dates[0]).days
        
        if total_days == 0:
            return f"{len(commits)} changes in one day"
        
        changes_per_month = (len(commits) / total_days) * 30
        
        if changes_per_month > 10:
            return "very frequently (10+ changes/month)"
        elif changes_per_month > 2:
            return "frequently (2-10 changes/month)"
        elif changes_per_month > 0.5:
            return "occasionally (monthly)"
        else:
            return "rarely (less than monthly)"
    except Exception:
        return f"{len(commits)} total commits"


def analyze_file_history(inputs: ExecuteInputs) -> AnalyzeOutputs:
    """Perform full history analysis on a file."""
    file_path = inputs.file_path
    repo_path = inputs.repo_path

    # Check if git repo
    if not is_git_repo(repo_path):
        return AnalyzeOutputs(
            summary=f"'{repo_path}' is not a git repository",
            change_patterns=ChangePatterns(
                total_commits=0,
                change_frequency="N/A",
                last_modified="N/A",
                stability_assessment="Not a git repository",
            ),
        )

    # Get commit history
    commits = get_file_commits(file_path, repo_path, inputs.max_commits, inputs.line_range)

    if not commits:
        return AnalyzeOutputs(
            summary=f"No git history found for '{file_path}'",
            change_patterns=ChangePatterns(
                total_commits=0,
                change_frequency="never",
                last_modified="N/A",
                stability_assessment="No history available",
            ),
        )

    # Creation context (oldest commit)
    oldest_commit = commits[-1] if commits else None
    creation_context = None
    if oldest_commit:
        creation_context = CreationContext(
            created_date=oldest_commit["date"][:10],
            created_by=oldest_commit["author"],
            initial_purpose=oldest_commit["message"][:200],
        )

    # Build evolution timeline (key commits)
    timeline = []
    for commit in commits[:10]:  # Top 10 most recent
        timeline.append(TimelineEntry(
            date=commit["date"][:10],
            author=commit["author"],
            message=commit["message"][:100],
            change_type=classify_commit_message(commit["message"]),
        ))

    # Key contributors
    author_commits: Dict[str, int] = {}
    for commit in commits:
        author = commit["author"]
        author_commits[author] = author_commits.get(author, 0) + 1

    # Get blame info for lines contributed
    blame_info = {}
    if inputs.include_blame:
        blame_info = get_blame_info(file_path, repo_path, inputs.line_range)

    contributors = []
    for author, commit_count in sorted(author_commits.items(), key=lambda x: x[1], reverse=True)[:5]:
        lines = blame_info.get("authors", {}).get(author, 0)
        contributors.append(ContributorInfo(
            name=author,
            commits=commit_count,
            lines_contributed=lines,
        ))

    # Change patterns
    change_patterns = ChangePatterns(
        total_commits=len(commits),
        change_frequency=calculate_change_frequency(commits),
        last_modified=commits[0]["date"][:10] if commits else "N/A",
        stability_assessment=assess_stability(commits),
    )

    # Notable decisions
    notable_decisions = extract_notable_decisions(commits)

    # Related files
    related_files = get_related_files(file_path, repo_path)

    # Generate summary
    summary_parts = [
        f"'{file_path}' has {len(commits)} commits from {len(author_commits)} contributor(s).",
    ]
    if creation_context:
        summary_parts.append(
            f"Created on {creation_context.created_date} by {creation_context.created_by}."
        )
    summary_parts.append(f"Stability: {change_patterns.stability_assessment}.")
    if notable_decisions:
        summary_parts.append(f"Found {len(notable_decisions)} notable decision(s) in history.")

    return AnalyzeOutputs(
        summary=" ".join(summary_parts),
        creation_context=creation_context,
        evolution_timeline=timeline,
        key_contributors=contributors,
        change_patterns=change_patterns,
        notable_decisions=notable_decisions,
        related_files=related_files,
    )


# ============================================================================
# API Endpoints
# ============================================================================


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute the git history analysis skill."""
    start_time = time.time()

    try:
        outputs = analyze_file_history(request.inputs)
        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecuteResponse(
            outputs=outputs,
            metadata={
                "execution_time_ms": execution_time_ms,
                "file_analyzed": request.inputs.file_path,
                "repo_path": request.inputs.repo_path,
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
    # Check if git is available
    git_available, _ = run_git_command(["--version"], ".")
    
    return {
        "status": "healthy" if git_available else "degraded",
        "version": SKILL_SCHEMA["version"],
        "skill_id": SKILL_SCHEMA["id"],
        "checks": {
            "git": {"status": "pass" if git_available else "fail", "message": "Git CLI available" if git_available else "Git not found"}
        },
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

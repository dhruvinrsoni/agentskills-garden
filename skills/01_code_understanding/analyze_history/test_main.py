"""
Tests for Git History Analyzer skill.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from . import main
from .main import (
    app,
    classify_commit_message,
    is_git_repo,
    run_git_command,
    calculate_change_frequency,
    assess_stability,
    extract_notable_decisions,
    analyze_file_history,
    ExecuteInputs,
)

client = TestClient(app)


# ============================================================================
# Unit Tests - Utility Functions
# ============================================================================


class TestClassifyCommitMessage:
    """Tests for commit message classification."""

    def test_bugfix_detection(self):
        assert classify_commit_message("fix: resolve null pointer") == "bugfix"
        assert classify_commit_message("Bug in parsing logic") == "bugfix"
        assert classify_commit_message("Fixed issue #123") == "bugfix"
        assert classify_commit_message("Fix crash on startup") == "bugfix"

    def test_feature_detection(self):
        assert classify_commit_message("feat: add user auth") == "feature"
        assert classify_commit_message("Add new login page") == "feature"
        assert classify_commit_message("Implement caching layer") == "feature"
        assert classify_commit_message("New feature: dashboard") == "feature"

    def test_refactor_detection(self):
        assert classify_commit_message("refactor: clean up handlers") == "refactor"
        assert classify_commit_message("Improve performance of query") == "refactor"
        assert classify_commit_message("Optimize database calls") == "refactor"
        assert classify_commit_message("Clean up legacy code") == "refactor"

    def test_documentation_detection(self):
        assert classify_commit_message("docs: update README") == "documentation"
        assert classify_commit_message("Add comments to complex function") == "documentation"
        assert classify_commit_message("Update README.md") == "documentation"

    def test_testing_detection(self):
        assert classify_commit_message("test: add unit tests") == "testing"
        assert classify_commit_message("Add spec for auth module") == "testing"

    def test_merge_detection(self):
        assert classify_commit_message("Merge branch 'feature/x'") == "merge"
        assert classify_commit_message("Revert 'add new feature'") == "merge"

    def test_generic_update(self):
        assert classify_commit_message("Update version") == "update"
        assert classify_commit_message("Minor changes") == "update"


class TestCalculateChangeFrequency:
    """Tests for change frequency calculation."""

    def test_empty_commits(self):
        assert calculate_change_frequency([]) == "never"

    def test_single_commit(self):
        assert calculate_change_frequency([{"date": "2024-01-15 10:00:00 +0000"}]) == "once"

    def test_multiple_commits(self):
        commits = [
            {"date": "2024-01-01 10:00:00 +0000"},
            {"date": "2024-01-15 10:00:00 +0000"},
            {"date": "2024-02-01 10:00:00 +0000"},
        ]
        result = calculate_change_frequency(commits)
        assert "changes" in result or "month" in result.lower()


class TestAssessStability:
    """Tests for stability assessment."""

    def test_empty_commits(self):
        assert assess_stability([]) == "unknown"

    def test_single_commit(self):
        commits = [{"date": "2024-01-15 10:00:00 +0000"}]
        assert "stable" in assess_stability(commits).lower()

    def test_frequent_changes(self):
        # Commits every day
        commits = [
            {"date": "2024-01-01 10:00:00 +0000"},
            {"date": "2024-01-02 10:00:00 +0000"},
            {"date": "2024-01-03 10:00:00 +0000"},
            {"date": "2024-01-04 10:00:00 +0000"},
        ]
        result = assess_stability(commits)
        assert "active" in result.lower() or "frequent" in result.lower()


class TestExtractNotableDecisions:
    """Tests for notable decision extraction."""

    def test_empty_commits(self):
        assert extract_notable_decisions([]) == []

    def test_with_reasoning(self):
        commits = [
            {
                "date": "2024-01-15 10:00:00 +0000",
                "message": "Refactor auth because the old system was insecure",
            },
            {
                "date": "2024-01-10 10:00:00 +0000",
                "message": "Update deps",
            },
        ]
        decisions = extract_notable_decisions(commits)
        assert len(decisions) == 1
        assert "because" in decisions[0].decision.lower()

    def test_breaking_change(self):
        commits = [
            {
                "date": "2024-01-15 10:00:00 +0000",
                "message": "BREAKING CHANGE: remove deprecated API",
            },
        ]
        decisions = extract_notable_decisions(commits)
        assert len(decisions) == 1


# ============================================================================
# Unit Tests - Git Commands
# ============================================================================


class TestRunGitCommand:
    """Tests for git command execution."""

    def test_git_version(self):
        success, output = run_git_command(["--version"], ".")
        # Git should be available in standard dev environments
        assert success is True or "not found" in output.lower()

    def test_invalid_command(self):
        success, output = run_git_command(["invalid-command-xyz"], ".")
        assert success is False

    def test_invalid_path(self):
        success, output = run_git_command(["status"], "/nonexistent/path/xyz")
        assert success is False


class TestIsGitRepo:
    """Tests for git repository detection."""

    def test_current_directory(self):
        # This test assumes we're in a git repo
        result = is_git_repo(".")
        # Just verify function works without error
        assert isinstance(result, bool)

    def test_nonexistent_path(self):
        result = is_git_repo("/nonexistent/path/xyz")
        assert result is False


# ============================================================================
# Integration Tests - Mocked Git
# ============================================================================


class TestAnalyzeFileHistoryMocked:
    """Tests for file history analysis with mocked git commands."""

    @patch.object(main, "is_git_repo")
    def test_not_git_repo(self, mock_is_repo):
        mock_is_repo.return_value = False
        
        inputs = ExecuteInputs(file_path="test.py", repo_path="/not/a/repo")
        result = analyze_file_history(inputs)
        
        assert "not a git repository" in result.summary.lower()
        assert result.change_patterns.total_commits == 0

    @patch.object(main, "is_git_repo")
    @patch.object(main, "get_file_commits")
    def test_no_history(self, mock_commits, mock_is_repo):
        mock_is_repo.return_value = True
        mock_commits.return_value = []
        
        inputs = ExecuteInputs(file_path="new.py", repo_path=".")
        result = analyze_file_history(inputs)
        
        assert "no git history" in result.summary.lower()
        assert result.change_patterns.total_commits == 0

    @patch.object(main, "is_git_repo")
    @patch.object(main, "get_file_commits")
    @patch.object(main, "get_blame_info")
    @patch.object(main, "get_related_files")
    def test_full_analysis(self, mock_related, mock_blame, mock_commits, mock_is_repo):
        mock_is_repo.return_value = True
        mock_commits.return_value = [
            {"hash": "abc123", "author": "Dev1", "email": "dev1@test.com", 
             "date": "2024-01-15 10:00:00 +0000", "message": "fix: resolve bug"},
            {"hash": "def456", "author": "Dev2", "email": "dev2@test.com",
             "date": "2024-01-01 10:00:00 +0000", "message": "feat: initial implementation"},
        ]
        mock_blame.return_value = {"authors": {"Dev1": 50, "Dev2": 30}, "line_count": 80}
        mock_related.return_value = ["other.py", "utils.py"]
        
        inputs = ExecuteInputs(file_path="test.py", repo_path=".")
        result = analyze_file_history(inputs)
        
        assert result.change_patterns.total_commits == 2
        assert len(result.key_contributors) == 2
        assert len(result.evolution_timeline) == 2
        assert result.creation_context is not None
        assert result.creation_context.created_by == "Dev2"
        assert len(result.related_files) == 2


# ============================================================================
# API Endpoint Tests
# ============================================================================


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_status(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "skill_id" in data


class TestDescribeEndpoint:
    """Tests for /describe endpoint."""

    def test_describe_returns_schema(self):
        response = client.get("/describe")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "interface" in data
        assert "inputs" in data["interface"]
        assert "outputs" in data["interface"]


class TestExecuteEndpoint:
    """Tests for /execute endpoint."""

    def test_execute_requires_inputs(self):
        response = client.post("/execute", json={})
        assert response.status_code == 422  # Validation error

    def test_execute_requires_file_path(self):
        response = client.post("/execute", json={"inputs": {}})
        assert response.status_code == 422

    @patch.object(main, "is_git_repo")
    def test_execute_not_git_repo(self, mock_is_repo):
        mock_is_repo.return_value = False
        
        response = client.post(
            "/execute",
            json={"inputs": {"file_path": "test.py", "repo_path": "/fake"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "not a git repository" in data["outputs"]["summary"].lower()

    @patch.object(main, "analyze_file_history")
    def test_execute_returns_metadata(self, mock_analyze):
        from .main import AnalyzeOutputs, ChangePatterns
        
        mock_analyze.return_value = AnalyzeOutputs(
            summary="Test summary",
            change_patterns=ChangePatterns(
                total_commits=5,
                change_frequency="weekly",
                last_modified="2024-01-15",
                stability_assessment="stable",
            ),
        )
        
        response = client.post(
            "/execute",
            json={"inputs": {"file_path": "test.py"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert "execution_time_ms" in data["metadata"]


# ============================================================================
# Schema Invariant Tests
# ============================================================================


class TestSchemaInvariants:
    """Tests validating schema invariants."""

    def test_schema_file_exists(self):
        schema_path = Path(__file__).parent / "schema.json"
        assert schema_path.exists()

    def test_schema_has_required_fields(self):
        import json
        schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        
        assert "id" in schema
        assert "name" in schema
        assert "version" in schema
        assert "level" in schema
        assert "domain" in schema
        assert "interface" in schema

    def test_schema_level_is_valid(self):
        import json
        schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        
        assert schema["level"] >= 0
        assert schema["level"] <= 4

    def test_outputs_match_schema_structure(self):
        """Verify that AnalyzeOutputs matches the schema outputs definition."""
        import json
        from .main import AnalyzeOutputs, ChangePatterns
        
        schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        
        # Create a valid output and verify all schema-required fields exist
        output = AnalyzeOutputs(
            summary="Test",
            change_patterns=ChangePatterns(
                total_commits=0,
                change_frequency="never",
                last_modified="N/A",
                stability_assessment="unknown",
            ),
        )
        
        output_dict = output.model_dump()
        # Get the properties from the schema outputs object
        schema_outputs = schema["interface"]["outputs"]["properties"]
        
        for key in schema_outputs:
            assert key in output_dict, f"Missing output field: {key}"


# ============================================================================
# Real Git Repository Tests (Skip if not in git repo)
# ============================================================================


@pytest.mark.skipif(
    not is_git_repo("."),
    reason="Not running in a git repository"
)
class TestRealGitRepository:
    """Integration tests using actual git repository."""

    def test_analyze_existing_file(self):
        # Try to analyze a file that exists in this repo
        test_files = ["main.py", "schema.json", "README.md"]
        
        for test_file in test_files:
            if Path(test_file).exists():
                response = client.post(
                    "/execute",
                    json={"inputs": {"file_path": test_file, "repo_path": "."}}
                )
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
                break


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_special_characters_in_path(self):
        inputs = ExecuteInputs(
            file_path="path with spaces/file.py",
            repo_path="."
        )
        # Should not crash
        result = analyze_file_history(inputs)
        assert isinstance(result.summary, str)

    def test_very_long_commit_message_truncation(self):
        commits = [{
            "date": "2024-01-15 10:00:00 +0000",
            "message": "A" * 500 + " because this is a very long commit message",
        }]
        decisions = extract_notable_decisions(commits)
        if decisions:
            assert len(decisions[0].decision) <= 200

    def test_line_range_input(self):
        from .main import LineRange
        
        inputs = ExecuteInputs(
            file_path="test.py",
            repo_path=".",
            line_range=LineRange(start=10, end=20),
        )
        
        assert inputs.line_range.start == 10
        assert inputs.line_range.end == 20

    @patch.object(main, "is_git_repo", return_value=True)
    @patch.object(main, "get_file_commits", return_value=[])
    def test_include_blame_false(self, mock_commits, mock_repo):
        inputs = ExecuteInputs(
            file_path="test.py",
            repo_path=".",
            include_blame=False,
        )
        result = analyze_file_history(inputs)
        # Should complete without error
        assert isinstance(result.summary, str)


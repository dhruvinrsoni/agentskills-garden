"""
Tests for Detect Code Smells skill.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import (
    app,
    detect_smells,
    detect_survivor_comments,
    is_survivor_pattern,
    calculate_metrics,
    analyze_python_ast,
    ExecuteInputs,
    SmellInfo,
    CodeContext,
)

client = TestClient(app)


# ============================================================================
# Unit Tests - Survivor Comment Detection
# ============================================================================


class TestDetectSurvivorComments:
    """Tests for survivor comment detection."""

    def test_workaround_comment(self):
        code = "# WORKAROUND: API returns wrong format\ndata = fix_format(response)"
        survivors = detect_survivor_comments(code)
        assert len(survivors) == 1
        assert "workaround" in survivors[0][1].lower()

    def test_do_not_change_comment(self):
        code = "# DO NOT CHANGE - breaks legacy system\nmagic_value = 42"
        survivors = detect_survivor_comments(code)
        assert len(survivors) == 1
        assert "protected" in survivors[0][1].lower()

    def test_issue_reference(self):
        code = "# BUG #1234 - awaiting upstream fix\nerror_handling()"
        survivors = detect_survivor_comments(code)
        assert len(survivors) == 1
        assert "issue" in survivors[0][1].lower()

    def test_performance_comment(self):
        code = "# PERFORMANCE: inlined for speed\nfor i in range(1000): pass"
        survivors = detect_survivor_comments(code)
        assert len(survivors) == 1

    def test_no_survivor_comments(self):
        code = "# Regular comment\nx = 1"
        survivors = detect_survivor_comments(code)
        assert len(survivors) == 0


# ============================================================================
# Unit Tests - Python AST Analysis
# ============================================================================


class TestAnalyzePythonAst:
    """Tests for Python AST analysis."""

    def test_function_count(self):
        code = """
def foo():
    pass

def bar():
    pass
"""
        analyzer = analyze_python_ast(code)
        assert analyzer.function_count == 2

    def test_class_method_count(self):
        code = """
class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass

    def method3(self):
        pass
"""
        analyzer = analyze_python_ast(code)
        assert analyzer.class_count == 1
        assert len(analyzer.class_method_counts) == 1
        assert analyzer.class_method_counts[0][2] == 3  # 3 methods

    def test_nesting_depth(self):
        code = """
def foo():
    if True:
        for i in range(10):
            if i > 5:
                print(i)
"""
        analyzer = analyze_python_ast(code)
        assert analyzer.max_nesting >= 3

    def test_complexity(self):
        code = """
def complex_func():
    if a:
        pass
    elif b:
        pass
    for i in range(10):
        if i > 5:
            pass
"""
        analyzer = analyze_python_ast(code)
        assert analyzer.complexity >= 3

    def test_invalid_syntax_handling(self):
        code = "def broken(\n"
        analyzer = analyze_python_ast(code)
        # Should not crash, return empty analyzer
        assert analyzer.function_count == 0


# ============================================================================
# Unit Tests - Code Metrics
# ============================================================================


class TestCalculateMetrics:
    """Tests for code metrics calculation."""

    def test_lines_of_code(self):
        code = "x = 1\ny = 2\n# comment\nz = 3"
        metrics = calculate_metrics(code, "python")
        assert metrics.lines_of_code == 3  # Excludes comment

    def test_comment_ratio(self):
        code = "x = 1\n# comment\ny = 2"
        metrics = calculate_metrics(code, "python")
        assert metrics.comment_ratio > 0

    def test_function_count(self):
        code = "def foo(): pass\ndef bar(): pass"
        metrics = calculate_metrics(code, "python")
        assert metrics.function_count == 2


# ============================================================================
# Unit Tests - Smell Detection
# ============================================================================


class TestDetectSmells:
    """Tests for smell detection."""

    def test_clean_code(self):
        code = """
def add(a, b):
    return a + b
"""
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        assert result.health_score >= 80
        
    def test_detect_magic_number(self):
        code = "timeout = 3600"
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        magic_smells = [s for s in result.smells if s.id == "magic_number"]
        assert len(magic_smells) >= 1

    def test_detect_broad_except(self):
        code = """
try:
    risky()
except Exception:
    pass
"""
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        except_smells = [s for s in result.smells if s.id == "broad_except"]
        assert len(except_smells) >= 1

    def test_detect_todo_fixme(self):
        code = "# TODO: refactor this\nx = 1"
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        todo_smells = [s for s in result.smells if s.id == "todo_fixme"]
        assert len(todo_smells) >= 1

    def test_detect_hardcoded_secret(self):
        code = "password = 'supersecret123'"
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        secret_smells = [s for s in result.smells if s.id == "hardcoded_secret"]
        assert len(secret_smells) >= 1

    def test_detect_long_function(self):
        # Create a function with 60 lines
        code = "def long_func():\n" + "    x = 1\n" * 60
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        long_smells = [s for s in result.smells if s.id == "long_function"]
        assert len(long_smells) >= 1

    def test_detect_god_class(self):
        # Create a class with 20 methods
        methods = "\n".join([f"    def method{i}(self): pass" for i in range(20)])
        code = f"class GodClass:\n{methods}"
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        god_smells = [s for s in result.smells if s.id == "god_class"]
        assert len(god_smells) >= 1

    def test_survivor_detection(self):
        code = """
# WORKAROUND: API bug
try:
    unstable_api()
except Exception:
    fallback()
"""
        inputs = ExecuteInputs(code=code, language="python")
        result = detect_smells(inputs)
        # The broad except should be marked as survivor
        survivors = [s for s in result.smells if s.is_survivor]
        assert len(survivors) >= 1 or len(result.survivor_patterns) >= 1

    def test_severity_threshold_filters(self):
        code = "# TODO: fix\npassword = 'secret'"
        
        # With warning threshold, should filter out info-level TODO
        inputs = ExecuteInputs(code=code, language="python", severity_threshold="warning")
        result = detect_smells(inputs)
        todo_smells = [s for s in result.smells if s.id == "todo_fixme"]
        assert len(todo_smells) == 0

    def test_health_score_decreases_with_errors(self):
        clean_code = "x = 1"
        problem_code = "password = 'secret'\napi_key = 'abc123'"
        
        clean_result = detect_smells(ExecuteInputs(code=clean_code))
        problem_result = detect_smells(ExecuteInputs(code=problem_code))
        
        assert clean_result.health_score > problem_result.health_score

    def test_age_leniency(self):
        code = "# TODO: old code\nx = 1"
        
        young_code = ExecuteInputs(code=code, context=CodeContext(age_years=1))
        old_code = ExecuteInputs(code=code, context=CodeContext(age_years=5))
        
        young_result = detect_smells(young_code)
        old_result = detect_smells(old_code)
        
        # Old code should get slight leniency
        assert old_result.health_score >= young_result.health_score


# ============================================================================
# API Endpoint Tests
# ============================================================================


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_status(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "skill_id" in data


class TestDescribeEndpoint:
    """Tests for /describe endpoint."""

    def test_describe_returns_schema(self):
        response = client.get("/describe")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "detect_smells"
        assert "interface" in data


class TestExecuteEndpoint:
    """Tests for /execute endpoint."""

    def test_execute_requires_code(self):
        response = client.post("/execute", json={"inputs": {}})
        assert response.status_code == 422

    def test_execute_with_valid_code(self):
        response = client.post(
            "/execute",
            json={"inputs": {"code": "x = 1"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "outputs" in data
        assert "health_score" in data["outputs"]

    def test_execute_returns_metadata(self):
        response = client.post(
            "/execute",
            json={"inputs": {"code": "x = 1", "language": "python"}}
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
        
        assert schema["id"] == "detect_smells"
        assert schema["level"] == 2
        assert schema["domain"] == "code_understanding"

    def test_health_score_range(self):
        """Invariant: health_score must be between 0 and 100"""
        # Test with clean code
        clean_result = detect_smells(ExecuteInputs(code="x = 1"))
        assert 0 <= clean_result.health_score <= 100
        
        # Test with many problems
        problem_code = "\n".join([f"password_{i} = 'secret'" for i in range(20)])
        problem_result = detect_smells(ExecuteInputs(code=problem_code))
        assert 0 <= problem_result.health_score <= 100

    def test_smells_have_valid_lines(self):
        """Invariant: All smells must have valid line numbers"""
        code = "x = 1\npassword = 'secret'\ny = 2"
        result = detect_smells(ExecuteInputs(code=code))
        
        total_lines = len(code.split("\n"))
        for smell in result.smells:
            assert 1 <= smell.line <= total_lines


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_code(self):
        result = detect_smells(ExecuteInputs(code=""))
        assert result.health_score == 100
        assert len(result.smells) == 0

    def test_only_comments(self):
        code = "# Just a comment\n# Another comment"
        result = detect_smells(ExecuteInputs(code=code))
        assert isinstance(result.health_score, int)

    def test_very_long_code(self):
        # 1000 lines of code
        code = "\n".join([f"x_{i} = {i}" for i in range(1000)])
        result = detect_smells(ExecuteInputs(code=code))
        assert len(result.smells) <= 50  # Should be limited

    def test_special_characters(self):
        code = "emoji = '🎉'\nweird = '™®©'"
        result = detect_smells(ExecuteInputs(code=code))
        # Should not crash
        assert isinstance(result.summary, str)

    def test_multiline_strings(self):
        code = '''
doc = """
This is a multiline string
with various content
password = 'not real'
"""
'''
        result = detect_smells(ExecuteInputs(code=code))
        # Should handle multiline strings
        assert isinstance(result.summary, str)

    def test_auto_language_detection(self):
        code = "def foo(): pass"
        result = detect_smells(ExecuteInputs(code=code, language="auto"))
        assert result.metrics.function_count == 1

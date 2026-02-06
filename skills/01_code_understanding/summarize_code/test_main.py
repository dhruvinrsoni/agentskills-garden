"""Tests for summarize_code skill."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import (
    app,
    detect_language,
    generate_summary,
    PythonAnalyzer,
    GenericAnalyzer,
)

client = TestClient(app)


# ============================================================================
# API Endpoint Tests
# ============================================================================


class TestHealthEndpoint:
    """Test the /health endpoint."""

    def test_health_returns_healthy(self):
        """Health check should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["skill_id"] == "summarize_code"

    def test_health_includes_version(self):
        """Health check should include version."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "0.1.0"


class TestDescribeEndpoint:
    """Test the /describe endpoint."""

    def test_describe_returns_schema(self):
        """Describe should return the full skill schema."""
        response = client.get("/describe")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "summarize_code"
        assert "interface" in data
        assert "description" in data

    def test_describe_schema_matches_file(self):
        """Describe output should match schema.json file."""
        response = client.get("/describe")
        schema_file = Path(__file__).parent / "schema.json"
        with open(schema_file) as f:
            expected = json.load(f)
        assert response.json() == expected


class TestExecuteEndpoint:
    """Test the /execute endpoint."""

    def test_execute_simple_function(self):
        """Test summarizing a simple Python function."""
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "code": "def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    return a + b",
                    "language": "python",
                    "detail_level": "brief",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "outputs" in data
        assert "summary" in data["outputs"]
        assert "purpose" in data["outputs"]

    def test_execute_with_auto_language(self):
        """Test auto-detection of Python."""
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "code": "import os\n\ndef main():\n    print('hello')",
                    "language": "auto",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["language_detected"] == "python"

    def test_execute_returns_metadata(self):
        """Test that execution returns metadata."""
        response = client.post(
            "/execute",
            json={"inputs": {"code": "x = 1"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert "execution_time_ms" in data["metadata"]

    def test_execute_python_class(self):
        """Test summarizing a Python class."""
        code = """
class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(result)
        return result
"""
        response = client.post(
            "/execute",
            json={"inputs": {"code": code, "language": "python", "detail_level": "detailed"}},
        )
        assert response.status_code == 200
        data = response.json()
        outputs = data["outputs"]
        
        # Should detect the class
        class_names = [c["name"] for c in outputs["key_components"] if c["type"] == "class"]
        assert "Calculator" in class_names

    def test_execute_with_context(self):
        """Test providing additional context."""
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "code": "def process(data): return data",
                    "context": "Part of the data pipeline module",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "data pipeline" in data["outputs"]["purpose"].lower()


# ============================================================================
# Language Detection Tests
# ============================================================================


class TestLanguageDetection:
    """Test the language detection functionality."""

    def test_detect_python(self):
        """Detect Python code."""
        code = "def foo():\n    pass"
        assert detect_language(code) == "python"

    def test_detect_python_with_import(self):
        """Detect Python code with imports."""
        code = "import os\nimport sys"
        assert detect_language(code) == "python"

    def test_detect_javascript(self):
        """Detect JavaScript code."""
        code = "const x = 5;\nfunction foo() { return x; }"
        assert detect_language(code) == "javascript"

    def test_detect_typescript(self):
        """Detect TypeScript code."""
        code = "const x: number = 5;\nfunction foo(): string { return 'hi'; }"
        assert detect_language(code) == "typescript"

    def test_detect_java(self):
        """Detect Java code."""
        code = "public class Main {\n    public static void main(String[] args) {}\n}"
        assert detect_language(code) == "java"

    def test_detect_go(self):
        """Detect Go code."""
        code = "package main\n\nfunc main() {\n    fmt.Println()\n}"
        assert detect_language(code) == "go"


# ============================================================================
# Python Analyzer Tests
# ============================================================================


class TestPythonAnalyzer:
    """Test the Python AST analyzer."""

    def test_get_functions(self):
        """Extract function definitions."""
        code = """
def foo():
    '''Foo function.'''
    pass

def bar(x):
    return x * 2
"""
        analyzer = PythonAnalyzer(code)
        functions = analyzer.get_functions()
        names = [f["name"] for f in functions]
        assert "foo" in names
        assert "bar" in names

    def test_get_async_functions(self):
        """Extract async function definitions."""
        code = """
async def fetch_data():
    '''Fetch data asynchronously.'''
    return await get_data()
"""
        analyzer = PythonAnalyzer(code)
        functions = analyzer.get_functions()
        assert functions[0]["type"] == "async function"

    def test_get_classes(self):
        """Extract class definitions."""
        code = """
class MyClass:
    '''A test class.'''
    
    def method(self):
        pass
"""
        analyzer = PythonAnalyzer(code)
        classes = analyzer.get_classes()
        assert len(classes) == 1
        assert classes[0]["name"] == "MyClass"

    def test_get_imports(self):
        """Extract imports."""
        code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        analyzer = PythonAnalyzer(code)
        imports = analyzer.get_imports()
        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports
        assert "typing" in imports

    def test_complexity_low(self):
        """Low complexity detection."""
        code = "def foo(): pass"
        analyzer = PythonAnalyzer(code)
        complexity = analyzer.get_complexity_indicators()
        assert complexity["estimated_complexity"] == "low"

    def test_detect_decorator_pattern(self):
        """Detect decorator pattern."""
        code = "@decorator\ndef foo(): pass"
        analyzer = PythonAnalyzer(code)
        patterns = analyzer.detect_patterns()
        assert any("decorator" in p.lower() for p in patterns)

    def test_handle_syntax_error(self):
        """Handle invalid Python syntax."""
        code = "def foo( invalid syntax"
        analyzer = PythonAnalyzer(code)
        assert analyzer.parse_error is not None
        assert analyzer.get_functions() == []


# ============================================================================
# Generic Analyzer Tests
# ============================================================================


class TestGenericAnalyzer:
    """Test the generic code analyzer."""

    def test_javascript_functions(self):
        """Extract JavaScript functions."""
        code = """
function hello() { return 'hi'; }
const greet = (name) => { return 'hello ' + name; }
"""
        analyzer = GenericAnalyzer(code, "javascript")
        functions = analyzer.get_functions()
        names = [f["name"] for f in functions]
        assert "hello" in names

    def test_javascript_imports(self):
        """Extract JavaScript imports."""
        code = """
import React from 'react';
const fs = require('fs');
"""
        analyzer = GenericAnalyzer(code, "javascript")
        imports = analyzer.get_imports()
        assert "react" in imports
        assert "fs" in imports

    def test_go_functions(self):
        """Extract Go functions."""
        code = """
func main() {
    fmt.Println("Hello")
}

func (s *Server) Start() {
    // start server
}
"""
        analyzer = GenericAnalyzer(code, "go")
        functions = analyzer.get_functions()
        names = [f["name"] for f in functions]
        assert "main" in names
        assert "Start" in names


# ============================================================================
# Summary Generation Tests
# ============================================================================


class TestSummaryGeneration:
    """Test the summary generation function."""

    def test_brief_summary(self):
        """Brief summary should be concise."""
        code = "def add(a, b): return a + b"
        result = generate_summary(code, "python", "brief", "all")
        assert len(result.summary) < 200

    def test_detailed_summary(self):
        """Detailed summary should include more information."""
        code = """
import os
import sys

def main():
    '''Main entry point.'''
    print("Hello")

class Config:
    '''Configuration class.'''
    pass
"""
        result = generate_summary(code, "python", "detailed", "all")
        assert "complexity" in result.summary.lower()

    def test_includes_dependencies(self):
        """Summary should include detected dependencies."""
        code = "import requests\nimport json"
        result = generate_summary(code, "python", "standard", "all")
        assert "requests" in result.dependencies

    def test_includes_patterns(self):
        """Summary should detect patterns."""
        code = """
@app.route('/')
def index():
    try:
        return 'ok'
    except Exception as e:
        return str(e)
"""
        result = generate_summary(code, "python", "standard", "all")
        assert len(result.notable_patterns) > 0


# ============================================================================
# Integration Tests (from schema test cases)
# ============================================================================


class TestSchemaTestCases:
    """Run test cases defined in schema.json."""

    @pytest.fixture
    def schema_test_cases(self):
        """Load test cases from schema."""
        schema_file = Path(__file__).parent / "schema.json"
        with open(schema_file) as f:
            schema = json.load(f)
        return schema.get("validation", {}).get("test_cases", [])

    def test_simple_function_case(self, schema_test_cases):
        """Test the simple_function test case from schema."""
        test_case = next((tc for tc in schema_test_cases if tc["name"] == "simple_function"), None)
        if test_case is None:
            pytest.skip("simple_function test case not found in schema")

        response = client.post("/execute", json={"inputs": test_case["input"]})
        assert response.status_code == 200
        outputs = response.json()["outputs"]
        
        # Output should have required fields
        assert "summary" in outputs
        assert "purpose" in outputs

    def test_class_with_methods_case(self, schema_test_cases):
        """Test the class_with_methods test case from schema."""
        test_case = next((tc for tc in schema_test_cases if tc["name"] == "class_with_methods"), None)
        if test_case is None:
            pytest.skip("class_with_methods test case not found in schema")

        response = client.post("/execute", json={"inputs": test_case["input"]})
        assert response.status_code == 200
        outputs = response.json()["outputs"]
        
        # Should detect the Calculator class
        class_names = [c["name"] for c in outputs.get("key_components", []) if c["type"] == "class"]
        assert "Calculator" in class_names


# ============================================================================
# Invariant Tests
# ============================================================================


class TestInvariants:
    """Test schema-defined invariants."""

    def test_always_returns_summary_and_purpose(self):
        """Output must always include 'summary' and 'purpose' fields."""
        test_codes = [
            "",  # Empty
            "x = 1",  # Simple assignment
            "# just a comment",  # Comment only
            "def foo(): pass",  # Function
            "class Foo: pass",  # Class
        ]
        
        for code in test_codes:
            response = client.post("/execute", json={"inputs": {"code": code}})
            assert response.status_code == 200
            outputs = response.json()["outputs"]
            assert "summary" in outputs, f"Missing summary for code: {code[:20]}"
            assert "purpose" in outputs, f"Missing purpose for code: {code[:20]}"

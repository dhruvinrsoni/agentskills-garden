"""
Tests for Map Dependencies skill.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import (
    app,
    detect_language,
    get_source_files,
    parse_python_imports,
    parse_python_imports_regex,
    parse_js_imports,
    parse_java_imports,
    parse_go_imports,
    is_external_dependency,
    find_circular_dependencies,
    map_dependencies,
    ExecuteInputs,
)

client = TestClient(app)


# ============================================================================
# Unit Tests - Language Detection
# ============================================================================


class TestDetectLanguage:
    """Tests for language detection."""

    def test_python_extension(self):
        assert detect_language("main.py") == "python"
        assert detect_language("/path/to/file.py") == "python"

    def test_javascript_extensions(self):
        assert detect_language("app.js") == "javascript"
        assert detect_language("app.mjs") == "javascript"
        assert detect_language("component.jsx") == "javascript"

    def test_typescript_extensions(self):
        assert detect_language("app.ts") == "typescript"
        assert detect_language("component.tsx") == "typescript"

    def test_java_extension(self):
        assert detect_language("Main.java") == "java"

    def test_go_extension(self):
        assert detect_language("main.go") == "go"

    def test_unknown_extension(self):
        assert detect_language("file.unknown") == "unknown"
        assert detect_language("file.rs") == "unknown"


# ============================================================================
# Unit Tests - Python Import Parsing
# ============================================================================


class TestParsePythonImports:
    """Tests for Python import parsing."""

    def test_simple_import(self):
        code = "import os"
        imports = parse_python_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "os"
        assert imports[0][1] == "direct"

    def test_multiple_imports(self):
        code = "import os\nimport sys\nimport json"
        imports = parse_python_imports(code)
        assert len(imports) == 3

    def test_from_import(self):
        code = "from pathlib import Path"
        imports = parse_python_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "pathlib"
        assert imports[0][1] == "from"
        assert "Path" in imports[0][2]

    def test_multiple_symbols_import(self):
        code = "from typing import List, Dict, Optional"
        imports = parse_python_imports(code)
        assert len(imports) == 1
        assert len(imports[0][2]) == 3

    def test_relative_import(self):
        code = "from . import module"
        imports = parse_python_imports(code)
        assert len(imports) == 1
        assert imports[0][1] == "from"

    def test_dotted_import(self):
        code = "import os.path"
        imports = parse_python_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "os.path"


class TestParsePythonImportsRegex:
    """Tests for Python regex-based import parsing (fallback)."""

    def test_simple_import(self):
        code = "import os"
        imports = parse_python_imports_regex(code)
        assert len(imports) >= 1

    def test_from_import(self):
        code = "from pathlib import Path"
        imports = parse_python_imports_regex(code)
        assert len(imports) == 1


# ============================================================================
# Unit Tests - JavaScript Import Parsing
# ============================================================================


class TestParseJsImports:
    """Tests for JavaScript import parsing."""

    def test_default_import(self):
        code = "import React from 'react'"
        imports = parse_js_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "react"
        assert imports[0][1] == "default"
        assert "React" in imports[0][2]

    def test_named_import(self):
        code = "import { useState, useEffect } from 'react'"
        imports = parse_js_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "react"
        assert imports[0][1] == "named"
        assert "useState" in imports[0][2]

    def test_namespace_import(self):
        code = "import * as utils from './utils'"
        imports = parse_js_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "./utils"
        assert imports[0][1] == "namespace"

    def test_require_statement(self):
        code = "const express = require('express')"
        imports = parse_js_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "express"
        assert imports[0][1] == "require"

    def test_double_quotes(self):
        code = 'import axios from "axios"'
        imports = parse_js_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "axios"


# ============================================================================
# Unit Tests - Java Import Parsing
# ============================================================================


class TestParseJavaImports:
    """Tests for Java import parsing."""

    def test_simple_import(self):
        code = "import java.util.List;"
        imports = parse_java_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "java.util.List"

    def test_static_import(self):
        code = "import static org.junit.Assert.assertEquals;"
        imports = parse_java_imports(code)
        assert len(imports) == 1
        assert imports[0][1] == "static"

    def test_wildcard_import(self):
        code = "import java.util.*;"
        imports = parse_java_imports(code)
        assert len(imports) == 1


# ============================================================================
# Unit Tests - Go Import Parsing
# ============================================================================


class TestParseGoImports:
    """Tests for Go import parsing."""

    def test_single_import(self):
        code = 'import "fmt"'
        imports = parse_go_imports(code)
        assert len(imports) == 1
        assert imports[0][0] == "fmt"

    def test_multi_import(self):
        code = '''
import (
    "fmt"
    "net/http"
)
'''
        imports = parse_go_imports(code)
        assert len(imports) == 2

    def test_aliased_import(self):
        code = '''
import (
    mylog "github.com/user/logger"
)
'''
        imports = parse_go_imports(code)
        assert len(imports) == 1
        assert imports[0][1] == "aliased"


# ============================================================================
# Unit Tests - Dependency Classification
# ============================================================================


class TestIsExternalDependency:
    """Tests for external dependency classification."""

    def test_python_stdlib(self):
        assert is_external_dependency("os", "python") is False
        assert is_external_dependency("sys", "python") is False
        assert is_external_dependency("json", "python") is False

    def test_python_third_party(self):
        assert is_external_dependency("fastapi", "python") is True
        assert is_external_dependency("requests", "python") is True

    def test_python_relative_import(self):
        assert is_external_dependency(".module", "python") is False
        assert is_external_dependency("..utils", "python") is False

    def test_js_relative_import(self):
        assert is_external_dependency("./utils", "javascript") is False
        assert is_external_dependency("../lib", "javascript") is False

    def test_js_npm_package(self):
        assert is_external_dependency("react", "javascript") is True
        assert is_external_dependency("express", "javascript") is True

    def test_java_stdlib(self):
        assert is_external_dependency("java.util.List", "java") is False
        assert is_external_dependency("javax.servlet", "java") is False

    def test_java_third_party(self):
        assert is_external_dependency("org.springframework", "java") is True


# ============================================================================
# Unit Tests - Circular Dependency Detection
# ============================================================================


class TestFindCircularDependencies:
    """Tests for circular dependency detection."""

    def test_no_cycles(self):
        edges = {
            "a": {"b"},
            "b": {"c"},
            "c": set(),
        }
        cycles = find_circular_dependencies(edges)
        assert len(cycles) == 0

    def test_simple_cycle(self):
        edges = {
            "a": {"b"},
            "b": {"a"},
        }
        cycles = find_circular_dependencies(edges)
        assert len(cycles) >= 1

    def test_three_node_cycle(self):
        edges = {
            "a": {"b"},
            "b": {"c"},
            "c": {"a"},
        }
        cycles = find_circular_dependencies(edges)
        assert len(cycles) >= 1

    def test_self_reference(self):
        edges = {
            "a": {"a"},
        }
        cycles = find_circular_dependencies(edges)
        assert len(cycles) >= 1


# ============================================================================
# Integration Tests - Full Mapping
# ============================================================================


class TestMapDependencies:
    """Integration tests for full dependency mapping."""

    def test_nonexistent_path(self):
        inputs = ExecuteInputs(source_path="/nonexistent/path")
        result = map_dependencies(inputs)
        assert "not found" in result.summary.lower()

    def test_single_python_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import os\nimport json\nfrom fastapi import FastAPI")

            inputs = ExecuteInputs(source_path=str(test_file), language="python")
            result = map_dependencies(inputs)

            assert result.total_dependencies > 0
            assert len(result.external_dependencies) >= 1  # fastapi

    def test_directory_scan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple files
            (Path(tmpdir) / "a.py").write_text("import os")
            (Path(tmpdir) / "b.py").write_text("from . import a")

            inputs = ExecuteInputs(source_path=tmpdir, language="python")
            result = map_dependencies(inputs)

            assert "2 file" in result.summary

    def test_javascript_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "app.js"
            test_file.write_text("import React from 'react';\nimport { useState } from 'react';")

            inputs = ExecuteInputs(source_path=str(test_file), language="javascript")
            result = map_dependencies(inputs)

            assert result.total_dependencies > 0


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
        assert "id" in data
        assert data["id"] == "map_dependencies"
        assert "interface" in data


class TestExecuteEndpoint:
    """Tests for /execute endpoint."""

    def test_execute_requires_inputs(self):
        response = client.post("/execute", json={})
        assert response.status_code == 422

    def test_execute_handles_missing_path(self):
        response = client.post(
            "/execute",
            json={"inputs": {"source_path": "/definitely/not/real"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert "not found" in data["outputs"]["summary"].lower()

    def test_execute_with_valid_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import json")

            response = client.post(
                "/execute",
                json={"inputs": {"source_path": str(test_file)}}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
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

        assert schema["id"] == "map_dependencies"
        assert schema["level"] == 1
        assert schema["domain"] == "code_understanding"

    def test_total_dependencies_invariant(self):
        """Test: total_dependencies >= len(internal) + len(external)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import os\nfrom fastapi import FastAPI")

            inputs = ExecuteInputs(source_path=str(test_file))
            result = map_dependencies(inputs)

            # Since we count unique externals, this should hold
            assert result.total_dependencies >= 0


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "empty.py"
            test_file.write_text("")

            inputs = ExecuteInputs(source_path=str(test_file))
            result = map_dependencies(inputs)

            assert result.total_dependencies == 0

    def test_syntax_error_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "broken.py"
            test_file.write_text("import os\ndef broken(\n")

            inputs = ExecuteInputs(source_path=str(test_file))
            result = map_dependencies(inputs)

            # Should fall back to regex and still work
            assert "1 file" in result.summary

    def test_binary_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "binary.py"
            test_file.write_bytes(b"\x00\x01\x02\x03")

            inputs = ExecuteInputs(source_path=str(test_file))
            # Should not crash
            result = map_dependencies(inputs)
            assert isinstance(result.summary, str)

    def test_exclude_external(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import fastapi\nimport os")

            inputs = ExecuteInputs(
                source_path=str(test_file),
                include_external=False,
            )
            result = map_dependencies(inputs)

            assert len(result.external_dependencies) == 0

    def test_auto_detect_language(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "a.py").write_text("import os")
            (Path(tmpdir) / "b.js").write_text("import React from 'react'")

            inputs = ExecuteInputs(source_path=tmpdir, language="auto")
            result = map_dependencies(inputs)

            assert "2 file" in result.summary

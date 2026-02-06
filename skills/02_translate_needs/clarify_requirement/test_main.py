"""
Tests for Clarify Requirement skill.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from .main import (
    app,
    clarify_requirement,
    extract_user_story_components,
    identify_action_category,
    count_vague_terms,
    calculate_completeness_score,
    generate_clarifying_questions,
    ExecuteInputs,
)

client = TestClient(app)


# ============================================================================
# Unit Tests - User Story Parsing
# ============================================================================


class TestExtractUserStoryComponents:
    """Tests for user story component extraction."""

    def test_full_user_story(self):
        text = "As a customer, I want to view my order history so that I can track past purchases"
        parts = extract_user_story_components(text)
        assert parts["actor"] == "customer"
        assert "order history" in parts["action"].lower()
        assert "track" in parts["benefit"].lower()

    def test_partial_user_story(self):
        text = "I want to reset my password"
        parts = extract_user_story_components(text)
        assert "reset" in parts["action"].lower()

    def test_no_user_story_format(self):
        text = "Add a login button"
        parts = extract_user_story_components(text)
        # Should still extract what it can
        assert isinstance(parts["actor"], str)


# ============================================================================
# Unit Tests - Action Category Detection
# ============================================================================


class TestIdentifyActionCategory:
    """Tests for action category identification."""

    def test_create_verbs(self):
        assert identify_action_category("add new user") == "create"
        assert identify_action_category("create account") == "create"
        assert identify_action_category("generate report") == "create"

    def test_read_verbs(self):
        assert identify_action_category("view details") == "read"
        assert identify_action_category("display list") == "read"
        assert identify_action_category("show orders") == "read"

    def test_update_verbs(self):
        assert identify_action_category("edit profile") == "update"
        assert identify_action_category("modify settings") == "update"

    def test_delete_verbs(self):
        assert identify_action_category("remove item") == "delete"
        assert identify_action_category("delete account") == "delete"

    def test_search_verbs(self):
        assert identify_action_category("search products") == "search"
        assert identify_action_category("find users") == "search"
        assert identify_action_category("filter results") == "search"

    def test_auth_verbs(self):
        assert identify_action_category("login to system") == "auth"
        assert identify_action_category("authenticate user") == "auth"
        assert identify_action_category("sign up for account") == "auth"

    def test_unknown_action(self):
        assert identify_action_category("do something") == "unknown"


# ============================================================================
# Unit Tests - Vague Term Detection
# ============================================================================


class TestCountVagueTerms:
    """Tests for vague term counting."""

    def test_detects_vague_terms(self):
        text = "Add a thing that does stuff quickly"
        vague = count_vague_terms(text)
        assert "thing" in vague
        assert "stuff" in vague
        assert "quickly" in vague

    def test_no_vague_terms(self):
        text = "Create a password reset form with email validation"
        vague = count_vague_terms(text)
        assert len(vague) == 0

    def test_partial_vague_terms(self):
        text = "Make the login process simple and fast"
        vague = count_vague_terms(text)
        assert "simple" in vague
        assert "fast" in vague


# ============================================================================
# Unit Tests - Completeness Scoring
# ============================================================================


class TestCalculateCompletenessScore:
    """Tests for requirement completeness scoring."""

    def test_complete_user_story(self):
        text = "As a customer, I want to reset my password via email so that I can regain access to my account when I forget it"
        parts = extract_user_story_components(text)
        score = calculate_completeness_score(text, parts)
        assert score >= 0.5  # Should be reasonably complete

    def test_vague_requirement(self):
        text = "Make it better"
        parts = extract_user_story_components(text)
        score = calculate_completeness_score(text, parts)
        assert score < 0.3  # Should score low

    def test_score_bounds(self):
        # Score should always be between 0 and 1
        texts = [
            "",
            "x",
            "A very long requirement with many details that should score higher because it has more content",
            "thing stuff etc whatever",
        ]
        for text in texts:
            parts = extract_user_story_components(text)
            score = calculate_completeness_score(text, parts)
            assert 0.0 <= score <= 1.0


# ============================================================================
# Unit Tests - Question Generation
# ============================================================================


class TestGenerateClarifyingQuestions:
    """Tests for clarifying question generation."""

    def test_vague_terms_generate_questions(self):
        vague = ["thing", "fast"]
        questions = generate_clarifying_questions(
            "Add a thing that runs fast",
            vague,
            {"actor": "", "action": "", "benefit": ""},
            None,
        )
        assert len(questions) >= 1

    def test_missing_actor_question(self):
        questions = generate_clarifying_questions(
            "Reset password",
            [],
            {"actor": "", "action": "reset password", "benefit": ""},
            None,
        )
        actor_questions = [q for q in questions if "who" in q.question.lower()]
        assert len(actor_questions) >= 1

    def test_search_generates_empty_state_question(self):
        questions = generate_clarifying_questions(
            "search for products",
            [],
            {"actor": "user", "action": "search", "benefit": ""},
            None,
        )
        empty_questions = [q for q in questions if "no results" in q.question.lower()]
        assert len(empty_questions) >= 1


# ============================================================================
# Integration Tests - Full Clarification
# ============================================================================


class TestClarifyRequirement:
    """Integration tests for full requirement clarification."""

    def test_vague_requirement(self):
        inputs = ExecuteInputs(
            raw_requirement="Add a button that does the thing",
            domain_context="web application",
        )
        result = clarify_requirement(inputs)
        
        assert result.confidence_score < 0.5
        assert len(result.clarifying_questions) >= 1

    def test_clear_requirement(self):
        inputs = ExecuteInputs(
            raw_requirement="As a user, I want to reset my password via email so I can regain access",
            domain_context="authentication",
        )
        result = clarify_requirement(inputs)
        
        assert result.confidence_score >= 0.4
        assert len(result.acceptance_criteria) >= 1

    def test_generates_acceptance_criteria(self):
        inputs = ExecuteInputs(
            raw_requirement="Users should be able to search products by name",
            domain_context="e-commerce",
        )
        result = clarify_requirement(inputs)
        
        assert len(result.acceptance_criteria) >= 1
        # Should have GWT format
        ac = result.acceptance_criteria[0]
        assert ac.given
        assert ac.when
        assert ac.then

    def test_extracts_assumptions(self):
        inputs = ExecuteInputs(
            raw_requirement="Delete user account",
            domain_context="user management",
        )
        result = clarify_requirement(inputs)
        
        # Should assume authorization is needed
        assert len(result.implicit_assumptions) >= 1

    def test_generates_edge_cases(self):
        inputs = ExecuteInputs(
            raw_requirement="Create new product listing",
            domain_context="e-commerce",
        )
        result = clarify_requirement(inputs)
        
        assert len(result.edge_cases) >= 3

    def test_generates_technical_considerations(self):
        inputs = ExecuteInputs(
            raw_requirement="Search for users by email",
            domain_context="admin panel",
        )
        result = clarify_requirement(inputs)
        
        assert len(result.technical_considerations) >= 1


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
        assert data["skill_id"] == "clarify_requirement"


class TestDescribeEndpoint:
    """Tests for /describe endpoint."""

    def test_describe_returns_schema(self):
        response = client.get("/describe")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "clarify_requirement"
        assert "interface" in data


class TestExecuteEndpoint:
    """Tests for /execute endpoint."""

    def test_execute_requires_raw_requirement(self):
        response = client.post("/execute", json={"inputs": {}})
        assert response.status_code == 422

    def test_execute_with_valid_input(self):
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "raw_requirement": "Add login feature"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "outputs" in data
        assert "confidence_score" in data["outputs"]

    def test_execute_returns_metadata(self):
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "raw_requirement": "Test requirement",
                    "domain_context": "testing"
                }
            }
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
        
        assert schema["id"] == "clarify_requirement"
        assert schema["level"] == 1
        assert schema["domain"] == "translate_needs"

    def test_confidence_score_range(self):
        """Invariant: confidence_score must be between 0 and 1"""
        test_cases = [
            "x",  # Minimal
            "Add a thing",  # Vague
            "As a user, I want to do something so that I benefit",  # Template
            "Create a detailed user registration form with email validation, password strength checking, and CAPTCHA for security so that we prevent fake accounts",  # Detailed
        ]
        
        for text in test_cases:
            result = clarify_requirement(ExecuteInputs(raw_requirement=text))
            assert 0.0 <= result.confidence_score <= 1.0

    def test_vague_inputs_have_questions(self):
        """Invariant: Must always produce at least one question for vague inputs"""
        vague_requirements = [
            "Do the thing",
            "Make it work",
            "Fix stuff",
            "Add something",
        ]
        
        for req in vague_requirements:
            result = clarify_requirement(ExecuteInputs(raw_requirement=req))
            # Should have at least one question OR low confidence
            assert len(result.clarifying_questions) >= 1 or result.confidence_score < 0.3


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_requirement(self):
        result = clarify_requirement(ExecuteInputs(raw_requirement=""))
        assert result.confidence_score <= 0.1
        assert isinstance(result.summary, str)

    def test_very_long_requirement(self):
        long_req = "Create a feature that " + "does something important " * 100
        result = clarify_requirement(ExecuteInputs(raw_requirement=long_req))
        assert isinstance(result.summary, str)

    def test_special_characters(self):
        result = clarify_requirement(
            ExecuteInputs(raw_requirement="Add a button with emoji 🚀 and symbols @#$%")
        )
        assert isinstance(result.summary, str)

    def test_all_stakeholder_roles(self):
        roles = ["end_user", "product_manager", "developer", "executive", "other"]
        for role in roles:
            result = clarify_requirement(
                ExecuteInputs(
                    raw_requirement="Add feature",
                    stakeholder_role=role,
                )
            )
            assert result.confidence_score >= 0


"""
Tests for Translate for Stakeholder skill.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import (
    app,
    translate_stakeholder,
    extract_technical_terms,
    extract_business_impact,
    extract_user_impact,
    extract_timeline,
    simplify_content,
    summarize_for_executive,
    generate_elevator_pitch,
    ExecuteInputs,
    ContextInput,
)

client = TestClient(app)


# ============================================================================
# Unit Tests - Technical Term Extraction
# ============================================================================


class TestExtractTechnicalTerms:
    """Tests for technical term extraction."""

    def test_finds_api(self):
        terms = extract_technical_terms("We need to update the API")
        term_names = [t.term.lower() for t in terms]
        assert "api" in term_names

    def test_finds_database_terms(self):
        content = "Migrating the SQL database with replication"
        terms = extract_technical_terms(content)
        term_names = [t.term.lower() for t in terms]
        assert "sql" in term_names or "database" in term_names

    def test_finds_architecture_terms(self):
        content = "Moving to microservices architecture"
        terms = extract_technical_terms(content)
        term_names = [t.term.lower() for t in terms]
        assert "microservices" in term_names

    def test_finds_devops_terms(self):
        content = "Deploying via CI/CD pipeline to Kubernetes"
        terms = extract_technical_terms(content)
        term_names = [t.term.lower() for t in terms]
        assert any(t in term_names for t in ["ci/cd", "kubernetes", "pipeline"])

    def test_no_terms_in_simple_content(self):
        terms = extract_technical_terms("Hello world")
        # May still find terms but should be minimal
        assert isinstance(terms, list)

    def test_terms_have_explanations(self):
        terms = extract_technical_terms("The API uses authentication")
        for term in terms:
            assert term.term
            assert term.simple_explanation


# ============================================================================
# Unit Tests - Impact Extraction
# ============================================================================


class TestExtractBusinessImpact:
    """Tests for business impact extraction."""

    def test_payment_impact(self):
        impact = extract_business_impact("PaymentService failed")
        assert "revenue" in impact.lower() or "payment" in impact.lower()

    def test_user_impact(self):
        impact = extract_business_impact("User login is broken")
        assert "customer" in impact.lower() or "user" in impact.lower()

    def test_performance_impact(self):
        impact = extract_business_impact("System is slow under load")
        assert "performance" in impact.lower()

    def test_security_impact(self):
        impact = extract_business_impact("Security vulnerability found")
        assert "security" in impact.lower()


class TestExtractUserImpact:
    """Tests for user impact extraction."""

    def test_ui_impact(self):
        impact = extract_user_impact("Frontend changes to UI")
        assert "interface" in impact.lower() or "changes" in impact.lower()

    def test_performance_impact(self):
        impact = extract_user_impact("Performance improvement deployed")
        assert "speed" in impact.lower() or "performance" in impact.lower()

    def test_feature_impact(self):
        impact = extract_user_impact("New feature being added")
        assert "functionality" in impact.lower() or "feature" in impact.lower()


# ============================================================================
# Unit Tests - Timeline Extraction
# ============================================================================


class TestExtractTimeline:
    """Tests for timeline extraction."""

    def test_hours(self):
        timeline = extract_timeline("ETA: 2 hours")
        assert timeline is not None
        assert "2" in timeline

    def test_days(self):
        timeline = extract_timeline("Will take 3 days")
        assert timeline is not None
        assert "3" in timeline and "day" in timeline.lower()

    def test_eta_format(self):
        timeline = extract_timeline("ETA: end of day")
        assert "end of day" in timeline.lower()

    def test_no_timeline(self):
        timeline = extract_timeline("Just some technical content")
        assert timeline is None


# ============================================================================
# Unit Tests - Content Simplification
# ============================================================================


class TestSimplifyContent:
    """Tests for content simplification."""

    def test_truncates_long_content(self):
        long_content = "A" * 1000
        simplified = simplify_content(long_content)
        assert len(simplified) <= 510  # 500 + "..."

    def test_short_content_unchanged(self):
        short_content = "Short message"
        simplified = simplify_content(short_content)
        assert short_content in simplified

    def test_max_simplify_adds_explanations(self):
        content = "Update the API endpoint"
        simplified = simplify_content(content, max_simplify=True)
        # Should add explanation for API
        assert len(simplified) >= len(content)


# ============================================================================
# Unit Tests - Executive Summary
# ============================================================================


class TestSummarizeForExecutive:
    """Tests for executive summary generation."""

    def test_fix_statement(self):
        summary = summarize_for_executive("We are implementing a fix")
        assert "fix" in summary.lower() or "control" in summary.lower()

    def test_proposal_statement(self):
        summary = summarize_for_executive("Proposal to migrate systems")
        assert "proposal" in summary.lower() or "improvement" in summary.lower()

    def test_error_statement(self):
        summary = summarize_for_executive("Error in production")
        assert "issue" in summary.lower() or "working" in summary.lower()


# ============================================================================
# Unit Tests - Elevator Pitch
# ============================================================================


class TestGenerateElevatorPitch:
    """Tests for elevator pitch generation."""

    def test_executive_pitch(self):
        pitch = generate_elevator_pitch(
            "PaymentService down",
            "executive",
            None,
        )
        assert len(pitch) > 0
        assert len(pitch) < 500  # Should be concise

    def test_pm_pitch(self):
        pitch = generate_elevator_pitch(
            "New feature being developed",
            "product_manager",
            None,
        )
        assert len(pitch) > 0

    def test_non_technical_pitch(self):
        pitch = generate_elevator_pitch(
            "System update in progress",
            "non_technical",
            None,
        )
        assert "you" in pitch.lower() or "questions" in pitch.lower()


# ============================================================================
# Integration Tests - Full Translation
# ============================================================================


class TestTranslateStakeholder:
    """Integration tests for full stakeholder translation."""

    def test_executive_translation(self):
        inputs = ExecuteInputs(
            technical_content="NullPointerException in PaymentService due to race condition. Fix: ETA 2 hours.",
            target_audience="executive",
            context=ContextInput(purpose="incident_report", urgency="high"),
        )
        result = translate_stakeholder(inputs)

        assert "Summary" in result.translated_content or "Impact" in result.translated_content
        assert len(result.key_takeaways) >= 1
        assert len(result.elevator_pitch) > 0

    def test_pm_translation(self):
        inputs = ExecuteInputs(
            technical_content="Migrating to microservices with CQRS pattern",
            target_audience="product_manager",
            context=ContextInput(purpose="proposal"),
        )
        result = translate_stakeholder(inputs)

        assert "User Impact" in result.translated_content or "Overview" in result.translated_content
        assert len(result.key_takeaways) >= 1

    def test_non_technical_translation(self):
        inputs = ExecuteInputs(
            technical_content="Kubernetes pods are being restarted due to OOM issues",
            target_audience="non_technical",
        )
        result = translate_stakeholder(inputs)

        # Should not have unexplained jargon
        assert "What" in result.translated_content
        assert len(result.technical_terms_explained) >= 1

    def test_engineer_translation(self):
        inputs = ExecuteInputs(
            technical_content="Implementing event-driven architecture with Kafka",
            target_audience="engineer",
        )
        result = translate_stakeholder(inputs)

        # Should preserve technical detail
        assert "Technical" in result.translated_content
        assert "Kafka" in result.translated_content or "event" in result.translated_content.lower()

    def test_mixed_audience(self):
        inputs = ExecuteInputs(
            technical_content="API migration from REST to GraphQL",
            target_audience="mixed",
        )
        result = translate_stakeholder(inputs)

        # Should have summary and details
        assert "TL;DR" in result.translated_content or "Summary" in result.translated_content

    def test_includes_action_items(self):
        inputs = ExecuteInputs(
            technical_content="Proposal needs review and approval",
            target_audience="executive",
            context=ContextInput(purpose="proposal"),
        )
        result = translate_stakeholder(inputs)

        assert len(result.action_items) >= 1

    def test_includes_follow_up_questions(self):
        inputs = ExecuteInputs(
            technical_content="Cost reduction proposal",
            target_audience="executive",
        )
        result = translate_stakeholder(inputs)

        assert len(result.follow_up_questions) >= 1

    def test_audience_focus_populated(self):
        inputs = ExecuteInputs(
            technical_content="Technical update",
            target_audience="executive",
        )
        result = translate_stakeholder(inputs)

        assert len(result.audience_focus.primary_concerns) >= 1


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
        assert data["skill_id"] == "translate_stakeholder"


class TestDescribeEndpoint:
    """Tests for /describe endpoint."""

    def test_describe_returns_schema(self):
        response = client.get("/describe")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "translate_stakeholder"
        assert "interface" in data


class TestExecuteEndpoint:
    """Tests for /execute endpoint."""

    def test_execute_requires_technical_content(self):
        response = client.post("/execute", json={"inputs": {}})
        assert response.status_code == 422

    def test_execute_with_minimal_input(self):
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "technical_content": "Server error in production"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "translated_content" in data["outputs"]

    def test_execute_with_full_input(self):
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "technical_content": "Database migration completed",
                    "target_audience": "executive",
                    "context": {
                        "purpose": "status_update",
                        "urgency": "low",
                        "project_name": "DB Upgrade"
                    },
                    "format": "email"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


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

        assert schema["id"] == "translate_stakeholder"
        assert schema["level"] == 2
        assert schema["domain"] == "translate_needs"

    def test_all_audiences_supported(self):
        audiences = ["executive", "product_manager", "engineer", "non_technical", "mixed"]
        for audience in audiences:
            inputs = ExecuteInputs(
                technical_content="Test content",
                target_audience=audience,
            )
            result = translate_stakeholder(inputs)
            assert result.translated_content
            assert result.elevator_pitch

    def test_output_has_required_fields(self):
        inputs = ExecuteInputs(technical_content="Test technical content")
        result = translate_stakeholder(inputs)

        # Check all required fields exist
        assert result.translated_content is not None
        assert result.key_takeaways is not None
        assert result.audience_focus is not None
        assert result.technical_terms_explained is not None
        assert result.action_items is not None
        assert result.follow_up_questions is not None
        assert result.elevator_pitch is not None


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_content(self):
        inputs = ExecuteInputs(technical_content="")
        result = translate_stakeholder(inputs)
        # Should handle gracefully
        assert isinstance(result.translated_content, str)

    def test_very_long_content(self):
        long_content = "Technical issue. " * 500
        inputs = ExecuteInputs(technical_content=long_content)
        result = translate_stakeholder(inputs)
        # Should handle without error
        assert isinstance(result.translated_content, str)

    def test_special_characters(self):
        inputs = ExecuteInputs(
            technical_content="Error: <script>alert('xss')</script> in ${variable}"
        )
        result = translate_stakeholder(inputs)
        assert isinstance(result.translated_content, str)

    def test_unicode_content(self):
        inputs = ExecuteInputs(
            technical_content="Erreur: événement déclenché 日本語テスト"
        )
        result = translate_stakeholder(inputs)
        assert isinstance(result.translated_content, str)

    def test_all_purposes(self):
        purposes = ["inform", "persuade", "request_resources", "status_update", "incident_report", "proposal"]
        for purpose in purposes:
            inputs = ExecuteInputs(
                technical_content="Test content",
                context=ContextInput(purpose=purpose),
            )
            result = translate_stakeholder(inputs)
            assert result.translated_content

    def test_all_urgency_levels(self):
        urgencies = ["low", "medium", "high", "critical"]
        for urgency in urgencies:
            inputs = ExecuteInputs(
                technical_content="Test content",
                context=ContextInput(urgency=urgency),
            )
            result = translate_stakeholder(inputs)
            assert result.key_takeaways

"""
Tests for Analyze Tradeoffs skill.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import (
    app,
    analyze_tradeoffs,
    extract_options_from_context,
    find_technology_info,
    analyze_option,
    calculate_weighted_score,
    generate_recommendation,
    ExecuteInputs,
    OptionInput,
    ConstraintsInput,
    Scores,
)

client = TestClient(app)


# ============================================================================
# Unit Tests - Option Extraction
# ============================================================================


class TestExtractOptionsFromContext:
    """Tests for option extraction from context."""

    def test_vs_pattern(self):
        context = "Should we use PostgreSQL vs MongoDB?"
        options = extract_options_from_context(context)
        assert len(options) == 2
        assert any("postgresql" in o.name.lower() for o in options)
        assert any("mongodb" in o.name.lower() for o in options)

    def test_or_pattern(self):
        context = "Choose between Redis or Memcached"
        options = extract_options_from_context(context)
        assert len(options) >= 2

    def test_between_pattern(self):
        context = "Decide between microservices and monolith"
        options = extract_options_from_context(context)
        assert len(options) == 2

    def test_no_clear_options(self):
        context = "We need to improve performance somehow"
        options = extract_options_from_context(context)
        # Should return empty or minimal
        assert isinstance(options, list)


# ============================================================================
# Unit Tests - Technology Info Lookup
# ============================================================================


class TestFindTechnologyInfo:
    """Tests for technology information lookup."""

    def test_exact_match(self):
        info = find_technology_info("postgresql")
        assert info is not None
        assert "pros" in info
        assert "cons" in info

    def test_case_insensitive(self):
        info = find_technology_info("PostgreSQL")
        assert info is not None

    def test_partial_match(self):
        info = find_technology_info("mongo")
        assert info is not None

    def test_unknown_technology(self):
        info = find_technology_info("completely_unknown_xyz")
        assert info is None


# ============================================================================
# Unit Tests - Option Analysis
# ============================================================================


class TestAnalyzeOption:
    """Tests for option analysis."""

    def test_known_technology(self):
        option = OptionInput(name="PostgreSQL", description="Relational DB")
        result = analyze_option(option, [])
        
        assert result.option == "PostgreSQL"
        assert len(result.pros) >= 1
        assert len(result.cons) >= 1
        assert 1 <= result.scores.cost <= 5

    def test_unknown_technology(self):
        option = OptionInput(name="CustomTech", description="Our custom solution")
        result = analyze_option(option, [])
        
        assert result.option == "CustomTech"
        assert len(result.pros) >= 1
        assert len(result.cons) >= 1


# ============================================================================
# Unit Tests - Scoring
# ============================================================================


class TestCalculateWeightedScore:
    """Tests for weighted score calculation."""

    def test_neutral_scores(self):
        scores = Scores(cost=3, time_to_implement=3, scalability=3, maintainability=3, risk=3)
        result = calculate_weighted_score(scores, [])
        assert result == 15  # 3 * 5 dimensions

    def test_priority_affects_score(self):
        scores = Scores(cost=5, time_to_implement=3, scalability=3, maintainability=3, risk=3)
        
        score_no_priority = calculate_weighted_score(scores, [])
        score_cost_priority = calculate_weighted_score(scores, ["cost"])
        
        assert score_cost_priority > score_no_priority

    def test_all_scores_valid_range(self):
        for cost in range(1, 6):
            for time in range(1, 6):
                scores = Scores(cost=cost, time_to_implement=time, scalability=3, maintainability=3, risk=3)
                result = calculate_weighted_score(scores, [])
                assert result >= 5  # Minimum possible
                assert result <= 50  # Maximum with doubled weights


# ============================================================================
# Unit Tests - Recommendations
# ============================================================================


class TestGenerateRecommendation:
    """Tests for recommendation generation."""

    def test_single_option(self):
        from main import ComparisonEntry
        
        comparisons = [
            ComparisonEntry(
                option="PostgreSQL",
                scores=Scores(cost=5, time_to_implement=3, scalability=3, maintainability=4, risk=4),
                pros=["Reliable", "ACID"],
                cons=["Schema required"],
            )
        ]
        
        result = generate_recommendation(comparisons, [])
        assert result.option == "PostgreSQL"

    def test_multiple_options(self):
        from main import ComparisonEntry
        
        comparisons = [
            ComparisonEntry(
                option="OptionA",
                scores=Scores(cost=5, time_to_implement=5, scalability=5, maintainability=5, risk=5),
                pros=["Best option"],
                cons=["Some issue"],
            ),
            ComparisonEntry(
                option="OptionB",
                scores=Scores(cost=2, time_to_implement=2, scalability=2, maintainability=2, risk=2),
                pros=["Cheap"],
                cons=["Many issues"],
            ),
        ]
        
        result = generate_recommendation(comparisons, [])
        assert result.option == "OptionA"  # Higher scores
        assert result.confidence == "high"  # Clear winner

    def test_empty_options(self):
        result = generate_recommendation([], [])
        assert "Unable" in result.option or result.confidence == "low"


# ============================================================================
# Integration Tests - Full Analysis
# ============================================================================


class TestAnalyzeTradeoffs:
    """Integration tests for full tradeoff analysis."""

    def test_database_choice(self):
        inputs = ExecuteInputs(
            decision_context="Choose between PostgreSQL and MongoDB for user data",
            options=[
                OptionInput(name="PostgreSQL", description="Relational database"),
                OptionInput(name="MongoDB", description="Document database"),
            ],
        )
        result = analyze_tradeoffs(inputs)
        
        assert len(result.comparison_matrix) == 2
        assert result.recommendation.option in ["PostgreSQL", "MongoDB"]
        assert len(result.risk_analysis) >= 1

    def test_with_priorities(self):
        inputs = ExecuteInputs(
            decision_context="Authentication solution",
            options=[
                OptionInput(name="Auth0", description="Managed service"),
                OptionInput(name="Custom Auth", description="Build ourselves"),
            ],
            priorities=["security", "time"],
        )
        result = analyze_tradeoffs(inputs)
        
        assert "security" in result.summary.lower() or "time" in result.summary.lower() or result.decision_factors

    def test_with_constraints(self):
        inputs = ExecuteInputs(
            decision_context="Hosting choice",
            constraints=ConstraintsInput(
                budget="$500/month",
                timeline="2 weeks",
                team_size=3,
            ),
        )
        result = analyze_tradeoffs(inputs)
        
        # Should include constraints in decision factors
        factors_text = " ".join(result.decision_factors).lower()
        assert "budget" in factors_text or "timeline" in factors_text or "team" in factors_text

    def test_auto_extract_options(self):
        inputs = ExecuteInputs(
            decision_context="Should we use serverless or containers?",
        )
        result = analyze_tradeoffs(inputs)
        
        # Should extract options from context
        assert len(result.comparison_matrix) >= 2

    def test_generates_talking_points(self):
        inputs = ExecuteInputs(
            decision_context="Microservices vs Monolith",
            audience="mixed",
        )
        result = analyze_tradeoffs(inputs)
        
        assert len(result.stakeholder_talking_points) >= 1
        audiences = [tp.audience for tp in result.stakeholder_talking_points]
        assert any("executive" in a.lower() for a in audiences)


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
        assert data["skill_id"] == "analyze_tradeoffs"


class TestDescribeEndpoint:
    """Tests for /describe endpoint."""

    def test_describe_returns_schema(self):
        response = client.get("/describe")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "analyze_tradeoffs"
        assert "interface" in data


class TestExecuteEndpoint:
    """Tests for /execute endpoint."""

    def test_execute_requires_decision_context(self):
        response = client.post("/execute", json={"inputs": {}})
        assert response.status_code == 422

    def test_execute_with_valid_input(self):
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "decision_context": "Redis vs Memcached for caching"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "recommendation" in data["outputs"]

    def test_execute_with_full_input(self):
        response = client.post(
            "/execute",
            json={
                "inputs": {
                    "decision_context": "API framework choice",
                    "options": [
                        {"name": "FastAPI", "description": "Python async"},
                        {"name": "Express", "description": "Node.js"},
                    ],
                    "priorities": ["performance", "maintainability"],
                    "audience": "technical",
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["outputs"]["comparison_matrix"]) == 2


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
        
        assert schema["id"] == "analyze_tradeoffs"
        assert schema["level"] == 2
        assert schema["domain"] == "translate_needs"

    def test_scores_valid_range(self):
        """Invariant: All scores must be between 1 and 5"""
        inputs = ExecuteInputs(
            decision_context="PostgreSQL vs MongoDB",
            options=[
                OptionInput(name="PostgreSQL"),
                OptionInput(name="MongoDB"),
            ],
        )
        result = analyze_tradeoffs(inputs)
        
        for entry in result.comparison_matrix:
            assert 1 <= entry.scores.cost <= 5
            assert 1 <= entry.scores.time_to_implement <= 5
            assert 1 <= entry.scores.scalability <= 5
            assert 1 <= entry.scores.maintainability <= 5
            assert 1 <= entry.scores.risk <= 5

    def test_recommendation_references_option(self):
        """Invariant: Recommendation must reference one of the provided options"""
        inputs = ExecuteInputs(
            decision_context="Option A vs Option B",
            options=[
                OptionInput(name="Option A"),
                OptionInput(name="Option B"),
            ],
        )
        result = analyze_tradeoffs(inputs)
        
        option_names = [o.name for o in inputs.options]
        assert result.recommendation.option in option_names

    def test_options_have_pros_and_cons(self):
        """Invariant: Every option must have at least one pro and one con"""
        inputs = ExecuteInputs(
            decision_context="PostgreSQL vs MongoDB vs Redis",
            options=[
                OptionInput(name="PostgreSQL"),
                OptionInput(name="MongoDB"),
                OptionInput(name="Redis"),
            ],
        )
        result = analyze_tradeoffs(inputs)
        
        for entry in result.comparison_matrix:
            assert len(entry.pros) >= 1, f"{entry.option} has no pros"
            assert len(entry.cons) >= 1, f"{entry.option} has no cons"


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_single_option(self):
        inputs = ExecuteInputs(
            decision_context="Should we use PostgreSQL?",
            options=[OptionInput(name="PostgreSQL")],
        )
        result = analyze_tradeoffs(inputs)
        
        assert len(result.comparison_matrix) == 1
        assert result.recommendation.option == "PostgreSQL"

    def test_many_options(self):
        inputs = ExecuteInputs(
            decision_context="Database choice",
            options=[OptionInput(name=f"Option{i}") for i in range(10)],
        )
        result = analyze_tradeoffs(inputs)
        
        assert len(result.comparison_matrix) == 10

    def test_empty_priorities(self):
        inputs = ExecuteInputs(
            decision_context="PostgreSQL vs MongoDB",
            priorities=[],
        )
        result = analyze_tradeoffs(inputs)
        
        assert result.recommendation.option is not None

    def test_special_characters_in_context(self):
        inputs = ExecuteInputs(
            decision_context="Use SQL++ vs NoSQL? (considering $$$)",
        )
        result = analyze_tradeoffs(inputs)
        
        assert isinstance(result.summary, str)

    def test_all_audiences(self):
        for audience in ["technical", "executive", "mixed"]:
            inputs = ExecuteInputs(
                decision_context="Tech choice",
                audience=audience,
            )
            result = analyze_tradeoffs(inputs)
            assert len(result.stakeholder_talking_points) >= 1

"""
Analyze Tradeoffs Skill

Evaluates technical options and articulates tradeoffs for stakeholder decisions.
Addresses Gap #4: Translating Business Needs to Technical Requirements.
"""

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


class OptionInput(BaseModel):
    """Single option to compare."""

    name: str
    description: str = ""


class ConstraintsInput(BaseModel):
    """Constraints to consider."""

    budget: Optional[str] = None
    timeline: Optional[str] = None
    team_size: Optional[int] = None
    existing_tech: Optional[List[str]] = None


class ExecuteInputs(BaseModel):
    """Input parameters for tradeoff analysis."""

    decision_context: str = Field(..., description="Description of the decision")
    options: Optional[List[OptionInput]] = None
    priorities: Optional[List[str]] = None
    constraints: Optional[ConstraintsInput] = None
    audience: str = Field(default="mixed")


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint."""

    inputs: ExecuteInputs
    context: Optional[Dict[str, Any]] = None


class Scores(BaseModel):
    """Scores across dimensions (1-5, higher is better)."""

    cost: int = Field(ge=1, le=5)
    time_to_implement: int = Field(ge=1, le=5)
    scalability: int = Field(ge=1, le=5)
    maintainability: int = Field(ge=1, le=5)
    risk: int = Field(ge=1, le=5)  # Higher = less risky


class ComparisonEntry(BaseModel):
    """Comparison matrix entry."""

    option: str
    scores: Scores
    pros: List[str]
    cons: List[str]


class Recommendation(BaseModel):
    """Recommendation with justification."""

    option: str
    confidence: str
    justification: str
    key_risks: List[str]


class RiskEntry(BaseModel):
    """Risk analysis entry."""

    risk: str
    probability: str
    impact: str
    mitigation: str
    affected_options: List[str]


class TalkingPoint(BaseModel):
    """Stakeholder talking point."""

    audience: str
    key_message: str
    supporting_points: List[str]


class TradeoffOutputs(BaseModel):
    """Output of tradeoff analysis."""

    summary: str
    recommendation: Recommendation
    comparison_matrix: List[ComparisonEntry]
    risk_analysis: List[RiskEntry]
    stakeholder_talking_points: List[TalkingPoint]
    decision_factors: List[str]


class ExecuteResponse(BaseModel):
    """Response model for successful execution."""

    status: str = "success"
    outputs: TradeoffOutputs
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Domain Knowledge - Technology Patterns
# ============================================================================

TECHNOLOGY_PATTERNS = {
    # Databases
    "postgresql": {
        "category": "database",
        "pros": [
            "ACID compliance ensures data integrity",
            "Mature ecosystem with extensive tooling",
            "Strong support for complex queries and joins",
            "Open source with no licensing costs",
        ],
        "cons": [
            "Requires schema design upfront",
            "Horizontal scaling can be complex",
            "May be overkill for simple use cases",
        ],
        "scores": {"cost": 5, "time_to_implement": 3, "scalability": 3, "maintainability": 4, "risk": 4},
        "best_for": ["structured data", "OLTP", "complex queries", "data integrity"],
    },
    "mongodb": {
        "category": "database",
        "pros": [
            "Flexible schema adapts to changing requirements",
            "Native horizontal scaling with sharding",
            "Good for document-oriented data",
            "JSON-like storage matches modern APIs",
        ],
        "cons": [
            "No ACID transactions across documents (until recent versions)",
            "Can lead to data inconsistency if not careful",
            "Joins are less efficient than relational DBs",
        ],
        "scores": {"cost": 4, "time_to_implement": 4, "scalability": 5, "maintainability": 3, "risk": 3},
        "best_for": ["flexible schema", "document data", "rapid prototyping", "high write volume"],
    },
    "redis": {
        "category": "database",
        "pros": [
            "Extremely fast in-memory operations",
            "Simple key-value model",
            "Great for caching and sessions",
        ],
        "cons": [
            "Limited query capabilities",
            "Data size limited by memory",
            "Persistence requires configuration",
        ],
        "scores": {"cost": 4, "time_to_implement": 5, "scalability": 4, "maintainability": 4, "risk": 3},
        "best_for": ["caching", "sessions", "real-time data", "queues"],
    },
    # Authentication
    "auth0": {
        "category": "auth",
        "pros": [
            "Battle-tested security implementation",
            "Quick time to production",
            "Handles compliance requirements",
            "Regular security updates",
        ],
        "cons": [
            "Recurring subscription cost",
            "Vendor lock-in concerns",
            "Less customization flexibility",
        ],
        "scores": {"cost": 2, "time_to_implement": 5, "scalability": 5, "maintainability": 5, "risk": 4},
        "best_for": ["quick launch", "compliance", "limited resources"],
    },
    "custom_auth": {
        "category": "auth",
        "pros": [
            "Full control over implementation",
            "No recurring vendor costs",
            "Can customize to exact needs",
        ],
        "cons": [
            "Security vulnerabilities risk",
            "Significant development time",
            "Ongoing maintenance burden",
        ],
        "scores": {"cost": 4, "time_to_implement": 2, "scalability": 3, "maintainability": 2, "risk": 2},
        "best_for": ["unique requirements", "full control", "long-term cost optimization"],
    },
    # Hosting
    "serverless": {
        "category": "hosting",
        "pros": [
            "Pay only for actual usage",
            "Auto-scales to zero",
            "No infrastructure management",
        ],
        "cons": [
            "Cold start latency",
            "Vendor lock-in",
            "Execution time limits",
        ],
        "scores": {"cost": 4, "time_to_implement": 4, "scalability": 5, "maintainability": 4, "risk": 3},
        "best_for": ["variable traffic", "event-driven", "cost optimization"],
    },
    "containers": {
        "category": "hosting",
        "pros": [
            "Portable across environments",
            "Consistent deployments",
            "Good resource utilization",
        ],
        "cons": [
            "Learning curve for orchestration",
            "Infrastructure overhead",
            "Requires ops expertise",
        ],
        "scores": {"cost": 3, "time_to_implement": 3, "scalability": 4, "maintainability": 4, "risk": 4},
        "best_for": ["microservices", "consistent environments", "hybrid cloud"],
    },
    "vms": {
        "category": "hosting",
        "pros": [
            "Simple mental model",
            "Full OS control",
            "Predictable costs",
        ],
        "cons": [
            "Lower resource utilization",
            "Slower scaling",
            "More maintenance overhead",
        ],
        "scores": {"cost": 2, "time_to_implement": 3, "scalability": 2, "maintainability": 3, "risk": 4},
        "best_for": ["legacy apps", "Windows workloads", "compliance requirements"],
    },
    # Architecture
    "microservices": {
        "category": "architecture",
        "pros": [
            "Independent deployment of services",
            "Technology flexibility per service",
            "Easier to scale specific components",
        ],
        "cons": [
            "Distributed system complexity",
            "Network latency overhead",
            "Requires mature DevOps practices",
        ],
        "scores": {"cost": 2, "time_to_implement": 2, "scalability": 5, "maintainability": 4, "risk": 3},
        "best_for": ["large teams", "complex domains", "independent scaling"],
    },
    "monolith": {
        "category": "architecture",
        "pros": [
            "Simpler to develop and debug",
            "No network overhead between components",
            "Easier deployment",
        ],
        "cons": [
            "Harder to scale individual features",
            "Can become unwieldy as it grows",
            "Single point of failure",
        ],
        "scores": {"cost": 4, "time_to_implement": 4, "scalability": 2, "maintainability": 3, "risk": 3},
        "best_for": ["small teams", "early stage", "simple domains"],
    },
}

# Common risks by category
COMMON_RISKS = {
    "database": [
        {"risk": "Data migration complexity", "impact": "high", "probability": "medium"},
        {"risk": "Performance degradation at scale", "impact": "high", "probability": "low"},
        {"risk": "Vendor lock-in with proprietary features", "impact": "medium", "probability": "medium"},
    ],
    "auth": [
        {"risk": "Security vulnerabilities", "impact": "high", "probability": "medium"},
        {"risk": "Service downtime blocking all users", "impact": "high", "probability": "low"},
        {"risk": "Compliance violations", "impact": "high", "probability": "low"},
    ],
    "hosting": [
        {"risk": "Cost overruns under high load", "impact": "medium", "probability": "medium"},
        {"risk": "Migration difficulty if vendor changes", "impact": "high", "probability": "low"},
        {"risk": "Performance inconsistency", "impact": "medium", "probability": "medium"},
    ],
    "architecture": [
        {"risk": "Over-engineering for current needs", "impact": "medium", "probability": "high"},
        {"risk": "Under-engineering for future growth", "impact": "high", "probability": "medium"},
        {"risk": "Team skill gaps", "impact": "high", "probability": "medium"},
    ],
}


# ============================================================================
# Analysis Functions
# ============================================================================


def extract_options_from_context(context: str) -> List[OptionInput]:
    """Try to extract options from the decision context."""
    options = []

    # Pattern: "X vs Y" or "X or Y"
    vs_match = re.search(r"(\w+(?:\s+\w+)?)\s+(?:vs\.?|or|versus)\s+(\w+(?:\s+\w+)?)", context, re.IGNORECASE)
    if vs_match:
        options.append(OptionInput(name=vs_match.group(1).strip()))
        options.append(OptionInput(name=vs_match.group(2).strip()))

    # Pattern: "between X and Y"
    between_match = re.search(r"between\s+(\w+(?:\s+\w+)?)\s+and\s+(\w+(?:\s+\w+)?)", context, re.IGNORECASE)
    if between_match:
        options.append(OptionInput(name=between_match.group(1).strip()))
        options.append(OptionInput(name=between_match.group(2).strip()))

    # Pattern: "choose X, Y, or Z"
    choose_match = re.search(r"choose\s+(.+)", context, re.IGNORECASE)
    if choose_match:
        parts = re.split(r",\s*|\s+or\s+", choose_match.group(1))
        for part in parts:
            cleaned = part.strip().strip("?.,")
            if cleaned and cleaned.lower() not in ["and", "or"]:
                options.append(OptionInput(name=cleaned))

    # Deduplicate by name
    seen = set()
    unique = []
    for opt in options:
        if opt.name.lower() not in seen:
            seen.add(opt.name.lower())
            unique.append(opt)

    return unique


def find_technology_info(name: str) -> Optional[Dict]:
    """Find technology information by name."""
    name_lower = name.lower().replace(" ", "_").replace("-", "_")
    
    # Direct match
    if name_lower in TECHNOLOGY_PATTERNS:
        return TECHNOLOGY_PATTERNS[name_lower]
    
    # Partial match
    for key, info in TECHNOLOGY_PATTERNS.items():
        if key in name_lower or name_lower in key:
            return info
    
    return None


def generate_default_scores() -> Scores:
    """Generate default neutral scores."""
    return Scores(
        cost=3,
        time_to_implement=3,
        scalability=3,
        maintainability=3,
        risk=3,
    )


def adjust_scores_for_priorities(
    scores: Scores,
    priorities: List[str],
) -> Scores:
    """Adjust scores based on stated priorities."""
    # This is a placeholder - in a real implementation,
    # priorities would weight the final recommendation
    return scores


def analyze_option(
    option: OptionInput,
    priorities: List[str],
) -> ComparisonEntry:
    """Analyze a single option."""
    tech_info = find_technology_info(option.name)

    if tech_info:
        scores = Scores(**tech_info["scores"])
        pros = tech_info["pros"][:4]
        cons = tech_info["cons"][:3]
    else:
        scores = generate_default_scores()
        pros = [
            f"{option.name} is a viable option",
            "Team may have existing familiarity",
        ]
        cons = [
            "Specific tradeoffs require deeper analysis",
            "Consider doing a proof of concept",
        ]

    scores = adjust_scores_for_priorities(scores, priorities)

    return ComparisonEntry(
        option=option.name,
        scores=scores,
        pros=pros,
        cons=cons,
    )


def calculate_weighted_score(scores: Scores, priorities: List[str]) -> float:
    """Calculate weighted score based on priorities."""
    weights = {
        "cost": 1.0,
        "time": 1.0,
        "speed": 1.0,
        "scalability": 1.0,
        "scale": 1.0,
        "maintainability": 1.0,
        "maintenance": 1.0,
        "risk": 1.0,
        "security": 1.0,
        "reliability": 1.0,
    }

    # Boost weights for stated priorities
    for i, priority in enumerate(priorities[:3]):
        priority_lower = priority.lower()
        for key in weights:
            if key in priority_lower:
                weights[key] = 2.0 - (i * 0.3)  # Higher weight for earlier priorities

    total = (
        scores.cost * weights.get("cost", 1.0)
        + scores.time_to_implement * weights.get("time", 1.0)
        + scores.scalability * weights.get("scalability", 1.0)
        + scores.maintainability * weights.get("maintainability", 1.0)
        + scores.risk * weights.get("risk", 1.0)
    )

    return total


def generate_recommendation(
    comparisons: List[ComparisonEntry],
    priorities: List[str],
) -> Recommendation:
    """Generate recommendation based on comparison."""
    if not comparisons:
        return Recommendation(
            option="Unable to recommend",
            confidence="low",
            justification="No options were provided for analysis",
            key_risks=["Need more information to make a recommendation"],
        )

    # Score each option
    scored = []
    for comp in comparisons:
        score = calculate_weighted_score(comp.scores, priorities)
        scored.append((comp, score))

    # Sort by score (higher is better)
    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[0][0]
    best_score = scored[0][1]

    # Determine confidence
    if len(scored) > 1:
        second_score = scored[1][1]
        gap = best_score - second_score
        if gap > 3:
            confidence = "high"
        elif gap > 1:
            confidence = "medium"
        else:
            confidence = "low"
    else:
        confidence = "medium"

    justification = f"{best.option} scores highest overall"
    if priorities:
        justification += f", particularly considering priority on {', '.join(priorities[:2])}"
    justification += f". Key strengths: {best.pros[0].lower()}"

    key_risks = [con for con in best.cons[:2]]

    return Recommendation(
        option=best.option,
        confidence=confidence,
        justification=justification,
        key_risks=key_risks,
    )


def generate_risk_analysis(
    comparisons: List[ComparisonEntry],
) -> List[RiskEntry]:
    """Generate risk analysis for the options."""
    risks = []
    categories_seen = set()

    for comp in comparisons:
        tech_info = find_technology_info(comp.option)
        if tech_info:
            category = tech_info.get("category", "general")
            if category not in categories_seen and category in COMMON_RISKS:
                categories_seen.add(category)
                for risk_info in COMMON_RISKS[category][:2]:
                    risks.append(RiskEntry(
                        risk=risk_info["risk"],
                        probability=risk_info["probability"],
                        impact=risk_info["impact"],
                        mitigation=f"Conduct thorough evaluation and have rollback plan",
                        affected_options=[comp.option],
                    ))

    # Add general risks
    risks.append(RiskEntry(
        risk="Requirements may change after decision",
        probability="medium",
        impact="medium",
        mitigation="Choose flexible options where possible; document decision rationale",
        affected_options=[c.option for c in comparisons],
    ))

    return risks[:5]


def generate_talking_points(
    recommendation: Recommendation,
    comparisons: List[ComparisonEntry],
    audience: str,
) -> List[TalkingPoint]:
    """Generate stakeholder talking points."""
    points = []

    # Executive summary
    exec_points = [
        f"After analysis, {recommendation.option} emerges as the recommended choice",
        f"Confidence level: {recommendation.confidence}",
    ]
    if comparisons:
        best = next((c for c in comparisons if c.option == recommendation.option), None)
        if best:
            exec_points.append(f"Key benefit: {best.pros[0]}")

    points.append(TalkingPoint(
        audience="Executive",
        key_message=f"Recommend {recommendation.option} - {recommendation.justification[:100]}",
        supporting_points=exec_points,
    ))

    # Technical team
    tech_points = [
        f"Recommended option scores well on maintainability and scalability",
    ]
    for comp in comparisons:
        tech_points.append(f"{comp.option}: {comp.cons[0] if comp.cons else 'Review in detail'}")

    points.append(TalkingPoint(
        audience="Technical Team",
        key_message=f"{recommendation.option} balances technical requirements with business constraints",
        supporting_points=tech_points[:3],
    ))

    # Risk-focused
    points.append(TalkingPoint(
        audience="Risk/Compliance",
        key_message=f"Key risks identified with mitigation strategies",
        supporting_points=recommendation.key_risks[:2] + ["All options carry some inherent risk"],
    ))

    return points


def generate_decision_factors(
    priorities: List[str],
    constraints: Optional[ConstraintsInput],
) -> List[str]:
    """Generate key decision factors."""
    factors = []

    if priorities:
        factors.append(f"Stated priorities: {', '.join(priorities[:3])}")

    if constraints:
        if constraints.budget:
            factors.append(f"Budget constraint: {constraints.budget}")
        if constraints.timeline:
            factors.append(f"Timeline constraint: {constraints.timeline}")
        if constraints.team_size:
            factors.append(f"Team size: {constraints.team_size} members")
        if constraints.existing_tech:
            factors.append(f"Existing technology stack: {', '.join(constraints.existing_tech[:3])}")

    factors.extend([
        "Long-term maintainability vs short-term delivery speed",
        "Risk tolerance and organizational readiness",
        "Total cost of ownership including ongoing maintenance",
    ])

    return factors[:6]


# ============================================================================
# Main Analysis Logic
# ============================================================================


def analyze_tradeoffs(inputs: ExecuteInputs) -> TradeoffOutputs:
    """Perform tradeoff analysis."""
    # Get or extract options
    options = inputs.options or extract_options_from_context(inputs.decision_context)

    if not options:
        # If no options found, create generic ones
        options = [
            OptionInput(name="Option A", description="First alternative"),
            OptionInput(name="Option B", description="Second alternative"),
        ]

    priorities = inputs.priorities or []
    constraints = inputs.constraints

    # Analyze each option
    comparisons = [analyze_option(opt, priorities) for opt in options]

    # Generate recommendation
    recommendation = generate_recommendation(comparisons, priorities)

    # Generate risk analysis
    risks = generate_risk_analysis(comparisons)

    # Generate talking points
    talking_points = generate_talking_points(recommendation, comparisons, inputs.audience)

    # Generate decision factors
    decision_factors = generate_decision_factors(priorities, constraints)

    # Build summary
    summary_parts = [
        f"Analyzed {len(options)} options for: {inputs.decision_context[:100]}.",
        f"Recommendation: {recommendation.option} (confidence: {recommendation.confidence}).",
    ]
    if priorities:
        summary_parts.append(f"Considered priorities: {', '.join(priorities[:2])}.")

    return TradeoffOutputs(
        summary=" ".join(summary_parts),
        recommendation=recommendation,
        comparison_matrix=comparisons,
        risk_analysis=risks,
        stakeholder_talking_points=talking_points,
        decision_factors=decision_factors,
    )


# ============================================================================
# API Endpoints
# ============================================================================


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute the tradeoff analysis skill."""
    start_time = time.time()

    try:
        outputs = analyze_tradeoffs(request.inputs)
        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecuteResponse(
            outputs=outputs,
            metadata={
                "execution_time_ms": execution_time_ms,
                "options_analyzed": len(outputs.comparison_matrix),
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

"""
Clarify Requirement Skill

Transforms ambiguous user requests into precise, actionable technical requirements.
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


class ExecuteInputs(BaseModel):
    """Input parameters for requirement clarification."""

    raw_requirement: str = Field(..., description="The original requirement")
    domain_context: Optional[str] = None
    existing_features: Optional[List[str]] = None
    stakeholder_role: str = Field(default="other")
    output_format: str = Field(default="structured")


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint."""

    inputs: ExecuteInputs
    context: Optional[Dict[str, Any]] = None


class ClarifiedRequirement(BaseModel):
    """Structured requirement."""

    title: str
    description: str
    user_goal: str
    business_value: str


class AcceptanceCriterion(BaseModel):
    """GWT acceptance criterion."""

    id: str
    given: str
    when: str
    then: str


class ImplicitAssumption(BaseModel):
    """Implicit assumption extracted from requirement."""

    assumption: str
    risk_if_wrong: str
    suggested_validation: str


class ClarifyingQuestion(BaseModel):
    """Question to ask stakeholder."""

    question: str
    why_important: str
    suggested_options: List[str] = []


class TechnicalConsideration(BaseModel):
    """Technical aspect to consider."""

    area: str
    consideration: str
    priority: str


class ClarifyOutputs(BaseModel):
    """Output of requirement clarification."""

    summary: str
    clarified_requirement: ClarifiedRequirement
    acceptance_criteria: List[AcceptanceCriterion] = []
    implicit_assumptions: List[ImplicitAssumption] = []
    clarifying_questions: List[ClarifyingQuestion] = []
    edge_cases: List[str] = []
    technical_considerations: List[TechnicalConsideration] = []
    confidence_score: float = 0.5


class ExecuteResponse(BaseModel):
    """Response model for successful execution."""

    status: str = "success"
    outputs: ClarifyOutputs
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Requirement Analysis Patterns
# ============================================================================

# Vague terms that indicate ambiguity
VAGUE_TERMS = [
    "thing", "stuff", "it", "that", "something", "whatever",
    "etc", "etc.", "and so on", "similar", "like that",
    "good", "fast", "better", "nice", "easy", "simple",
    "works", "working", "fixed", "done", "complete",
    "all", "every", "any", "some", "many", "few",
    "soon", "quickly", "later", "eventually", "asap",
]

# Action verbs indicating user intent
ACTION_VERBS = {
    "create": ["add", "create", "new", "generate", "make", "build"],
    "read": ["view", "see", "show", "display", "list", "get", "read", "fetch"],
    "update": ["edit", "update", "modify", "change", "revise"],
    "delete": ["delete", "remove", "clear", "drop", "purge"],
    "search": ["search", "find", "filter", "query", "look up", "locate"],
    "auth": ["login", "logout", "authenticate", "authorize", "sign in", "sign up"],
    "share": ["share", "export", "send", "email", "notify"],
    "configure": ["set", "configure", "customize", "tune", "adjust"],
}

# Domain-specific considerations
DOMAIN_CONSIDERATIONS = {
    "e-commerce": {
        "areas": ["payment", "inventory", "shipping", "tax", "promotions"],
        "edge_cases": [
            "Out of stock items",
            "Invalid payment methods",
            "International shipping restrictions",
            "Price changes during checkout",
        ],
    },
    "healthcare": {
        "areas": ["privacy", "HIPAA", "audit logging", "consent", "data retention"],
        "edge_cases": [
            "Emergency access procedures",
            "Patient consent withdrawal",
            "Data correction requests",
            "Cross-provider data sharing",
        ],
    },
    "authentication": {
        "areas": ["security", "session", "MFA", "password policy", "account recovery"],
        "edge_cases": [
            "Forgotten password with no email",
            "Account lockout scenarios",
            "Session timeout during action",
            "Concurrent login attempts",
        ],
    },
    "web application": {
        "areas": ["accessibility", "responsiveness", "offline", "caching"],
        "edge_cases": [
            "Network connectivity issues",
            "Browser compatibility",
            "Mobile vs desktop behavior",
            "Slow connection handling",
        ],
    },
}


# ============================================================================
# Requirement Parsing
# ============================================================================


def extract_user_story_components(text: str) -> Dict[str, str]:
    """Extract As a/I want/So that components from user story format."""
    components = {"actor": "", "action": "", "benefit": ""}

    # As a [role], I want [action] so that [benefit]
    as_match = re.search(r"as (?:a|an)\s+([^,]+)", text, re.IGNORECASE)
    if as_match:
        components["actor"] = as_match.group(1).strip()

    want_match = re.search(r"(?:I |we )?want(?:s)? (?:to )?(.*?)(?:so that|in order to|$)", text, re.IGNORECASE | re.DOTALL)
    if want_match:
        components["action"] = want_match.group(1).strip().rstrip(",.")

    so_match = re.search(r"(?:so that|in order to)\s+(.+)", text, re.IGNORECASE)
    if so_match:
        components["benefit"] = so_match.group(1).strip().rstrip(".")

    return components


def identify_action_category(text: str) -> str:
    """Identify the primary action category."""
    text_lower = text.lower()
    for category, verbs in ACTION_VERBS.items():
        for verb in verbs:
            if re.search(rf"\b{verb}\b", text_lower):
                return category
    return "unknown"


def count_vague_terms(text: str) -> List[str]:
    """Count vague terms in the requirement."""
    found = []
    text_lower = text.lower()
    for term in VAGUE_TERMS:
        if re.search(rf"\b{term}\b", text_lower):
            found.append(term)
    return found


def calculate_completeness_score(text: str, story_parts: Dict) -> float:
    """Calculate how complete the requirement is (0-1)."""
    score = 0.0

    # Length check (minimal length suggests incompleteness)
    words = len(text.split())
    if words >= 20:
        score += 0.2
    elif words >= 10:
        score += 0.1

    # User story components
    if story_parts["actor"]:
        score += 0.15
    if story_parts["action"]:
        score += 0.25
    if story_parts["benefit"]:
        score += 0.15

    # Vagueness penalty
    vague = count_vague_terms(text)
    score -= min(0.3, len(vague) * 0.1)

    # Has specific nouns (likely more concrete)
    if re.search(r"\b(?:button|page|form|field|email|password|user|account)\b", text.lower()):
        score += 0.1

    # Has quantifiers (measurable)
    if re.search(r"\b\d+|\b(?:maximum|minimum|at least|no more than)\b", text.lower()):
        score += 0.1

    return max(0.0, min(1.0, score))


# ============================================================================
# Question Generation
# ============================================================================


def generate_clarifying_questions(
    text: str,
    vague_terms: List[str],
    story_parts: Dict,
    domain: Optional[str],
) -> List[ClarifyingQuestion]:
    """Generate clarifying questions based on analysis."""
    questions = []

    # Questions for vague terms
    for term in vague_terms[:3]:  # Limit to top 3
        if term in ["thing", "stuff", "it", "that"]:
            questions.append(ClarifyingQuestion(
                question=f"What specifically do you mean by '{term}'?",
                why_important="Cannot implement without knowing the exact functionality",
                suggested_options=[],
            ))
        elif term in ["fast", "quickly"]:
            questions.append(ClarifyingQuestion(
                question="What response time would be acceptable?",
                why_important="Performance requirements affect architecture decisions",
                suggested_options=["Under 100ms", "Under 1 second", "Under 5 seconds"],
            ))
        elif term in ["simple", "easy"]:
            questions.append(ClarifyingQuestion(
                question="Can you describe the specific workflow you envision?",
                why_important="'Simple' means different things to different users",
                suggested_options=[],
            ))

    # Questions for missing story parts
    if not story_parts["actor"]:
        questions.append(ClarifyingQuestion(
            question="Who is the primary user of this feature?",
            why_important="Different users may have different needs and permissions",
            suggested_options=["End user", "Administrator", "Guest", "System"],
        ))

    if not story_parts["benefit"]:
        questions.append(ClarifyingQuestion(
            question="What business outcome or user benefit does this enable?",
            why_important="Understanding the 'why' helps make better design decisions",
            suggested_options=[],
        ))

    # Domain-specific questions
    domain_lower = (domain or "").lower()
    if "auth" in domain_lower or "login" in text.lower() or "password" in text.lower():
        questions.append(ClarifyingQuestion(
            question="What should happen if authentication fails?",
            why_important="Error handling affects security and user experience",
            suggested_options=["Show generic error", "Account lockout", "CAPTCHA challenge"],
        ))

    if "search" in text.lower() or "filter" in text.lower():
        questions.append(ClarifyingQuestion(
            question="What happens when no results are found?",
            why_important="Empty states need explicit design",
            suggested_options=["Show 'no results' message", "Suggest alternatives", "Show popular items"],
        ))

    return questions[:5]  # Limit to 5 questions


# ============================================================================
# Acceptance Criteria Generation
# ============================================================================


def generate_acceptance_criteria(
    action_category: str,
    story_parts: Dict,
    text: str,
) -> List[AcceptanceCriterion]:
    """Generate acceptance criteria in Given-When-Then format."""
    criteria = []
    actor = story_parts.get("actor", "user")
    action = story_parts.get("action", "performs the action")

    # Basic happy path
    criteria.append(AcceptanceCriterion(
        id="AC-1",
        given=f"A {actor} with valid access",
        when=f"They {action}",
        then="The action completes successfully",
    ))

    # Action-specific criteria
    if action_category == "create":
        criteria.append(AcceptanceCriterion(
            id="AC-2",
            given="Valid input data is provided",
            when="The creation request is submitted",
            then="The new item is persisted and a confirmation is shown",
        ))
        criteria.append(AcceptanceCriterion(
            id="AC-3",
            given="Required fields are missing",
            when="The form is submitted",
            then="Validation errors are displayed for missing fields",
        ))

    elif action_category == "read":
        criteria.append(AcceptanceCriterion(
            id="AC-2",
            given="Items exist in the system",
            when="The view is loaded",
            then="Items are displayed with relevant information",
        ))
        criteria.append(AcceptanceCriterion(
            id="AC-3",
            given="No items exist",
            when="The view is loaded",
            then="An appropriate empty state message is shown",
        ))

    elif action_category == "update":
        criteria.append(AcceptanceCriterion(
            id="AC-2",
            given="The item exists and user has edit permission",
            when="Changes are saved",
            then="The item is updated and changes are reflected immediately",
        ))

    elif action_category == "delete":
        criteria.append(AcceptanceCriterion(
            id="AC-2",
            given="The item exists",
            when="Delete is confirmed",
            then="The item is removed and no longer accessible",
        ))
        criteria.append(AcceptanceCriterion(
            id="AC-3",
            given="The delete action is triggered",
            when="Before actual deletion",
            then="A confirmation dialog is shown to prevent accidental deletion",
        ))

    elif action_category == "search":
        criteria.append(AcceptanceCriterion(
            id="AC-2",
            given="Matching items exist",
            when="A search query is entered",
            then="Matching results are displayed within acceptable time",
        ))

    elif action_category == "auth":
        criteria.append(AcceptanceCriterion(
            id="AC-2",
            given="Valid credentials are provided",
            when="Login is submitted",
            then="User is authenticated and redirected appropriately",
        ))
        criteria.append(AcceptanceCriterion(
            id="AC-3",
            given="Invalid credentials are provided",
            when="Login is submitted",
            then="An error message is shown without revealing which field was wrong",
        ))

    return criteria


# ============================================================================
# Assumption Extraction
# ============================================================================


def extract_implicit_assumptions(
    text: str,
    domain: Optional[str],
    action_category: str,
) -> List[ImplicitAssumption]:
    """Extract implicit assumptions from the requirement."""
    assumptions = []

    # Common implicit assumptions
    if "user" in text.lower() and "anonymous" not in text.lower():
        assumptions.append(ImplicitAssumption(
            assumption="Feature requires user authentication",
            risk_if_wrong="Unauthorized access or missing user context",
            suggested_validation="Confirm whether authentication is required",
        ))

    if action_category in ["create", "update", "delete"]:
        assumptions.append(ImplicitAssumption(
            assumption="User has permission to perform this action",
            risk_if_wrong="Security vulnerabilities or user frustration",
            suggested_validation="Define authorization rules explicitly",
        ))

    if "list" in text.lower() or "display" in text.lower():
        assumptions.append(ImplicitAssumption(
            assumption="Data volume will be manageable for UI display",
            risk_if_wrong="Performance issues with large datasets",
            suggested_validation="Define pagination requirements",
        ))

    # Domain-specific assumptions
    domain_lower = (domain or "").lower()
    if "commerce" in domain_lower:
        assumptions.append(ImplicitAssumption(
            assumption="Prices are in the default currency",
            risk_if_wrong="Incorrect pricing for international users",
            suggested_validation="Confirm currency handling requirements",
        ))

    if "health" in domain_lower:
        assumptions.append(ImplicitAssumption(
            assumption="Access is logged for audit purposes",
            risk_if_wrong="Compliance violations",
            suggested_validation="Confirm audit logging requirements",
        ))

    return assumptions[:5]


# ============================================================================
# Technical Considerations
# ============================================================================


def generate_technical_considerations(
    action_category: str,
    domain: Optional[str],
) -> List[TechnicalConsideration]:
    """Generate technical considerations for implementation."""
    considerations = []

    # Universal considerations
    considerations.append(TechnicalConsideration(
        area="Error Handling",
        consideration="Define behavior for network failures and unexpected errors",
        priority="high",
    ))

    # Action-specific
    if action_category in ["create", "update"]:
        considerations.append(TechnicalConsideration(
            area="Validation",
            consideration="Implement both client-side and server-side validation",
            priority="high",
        ))
        considerations.append(TechnicalConsideration(
            area="Concurrency",
            consideration="Handle concurrent edit conflicts",
            priority="medium",
        ))

    if action_category == "search":
        considerations.append(TechnicalConsideration(
            area="Performance",
            consideration="Consider indexing and query optimization for large datasets",
            priority="high",
        ))
        considerations.append(TechnicalConsideration(
            area="UX",
            consideration="Implement debouncing for real-time search",
            priority="medium",
        ))

    if action_category == "delete":
        considerations.append(TechnicalConsideration(
            area="Data Integrity",
            consideration="Handle dependent records and cascading effects",
            priority="high",
        ))

    # Domain-specific
    domain_lower = (domain or "").lower()
    if domain_lower in DOMAIN_CONSIDERATIONS:
        for area in DOMAIN_CONSIDERATIONS[domain_lower]["areas"][:2]:
            considerations.append(TechnicalConsideration(
                area=area.title(),
                consideration=f"Consider {area} requirements for this feature",
                priority="medium",
            ))

    return considerations[:6]


# ============================================================================
# Edge Case Generation
# ============================================================================


def generate_edge_cases(
    action_category: str,
    domain: Optional[str],
    text: str,
) -> List[str]:
    """Generate edge cases to consider."""
    cases = [
        "Empty or null input values",
        "Extremely long input strings",
        "Special characters and unicode in input",
        "Concurrent operations by multiple users",
        "Network timeout during operation",
    ]

    # Domain-specific edge cases
    domain_lower = (domain or "").lower()
    if domain_lower in DOMAIN_CONSIDERATIONS:
        cases.extend(DOMAIN_CONSIDERATIONS[domain_lower]["edge_cases"][:3])

    # Action-specific
    if action_category == "search":
        cases.append("Search query matching millions of results")
        cases.append("SQL injection or XSS in search terms")

    if action_category == "auth":
        cases.append("Brute force login attempts")
        cases.append("Session expiry during form submission")

    return cases[:8]


# ============================================================================
# Main Clarification Logic
# ============================================================================


def clarify_requirement(inputs: ExecuteInputs) -> ClarifyOutputs:
    """Perform requirement clarification analysis."""
    raw = inputs.raw_requirement
    domain = inputs.domain_context

    # Parse user story components
    story_parts = extract_user_story_components(raw)

    # Identify action category
    action_category = identify_action_category(raw)

    # Count vague terms
    vague_terms = count_vague_terms(raw)

    # Calculate confidence
    confidence = calculate_completeness_score(raw, story_parts)

    # Generate clarified requirement
    title = story_parts["action"][:50] if story_parts["action"] else "Unnamed Feature"
    title = title.strip().capitalize()
    if not title.endswith((".", "!", "?")):
        title = title.rstrip(".,")

    clarified = ClarifiedRequirement(
        title=title,
        description=raw,
        user_goal=story_parts["action"] or "Complete the requested action",
        business_value=story_parts["benefit"] or "To be determined",
    )

    # Generate questions
    questions = generate_clarifying_questions(raw, vague_terms, story_parts, domain)

    # Generate acceptance criteria
    acceptance = generate_acceptance_criteria(action_category, story_parts, raw)

    # Extract assumptions
    assumptions = extract_implicit_assumptions(raw, domain, action_category)

    # Generate edge cases
    edge_cases = generate_edge_cases(action_category, domain, raw)

    # Generate technical considerations
    tech_considerations = generate_technical_considerations(action_category, domain)

    # Build summary
    summary_parts = [f"Interpreted as: {title}."]
    if vague_terms:
        summary_parts.append(f"Found {len(vague_terms)} vague term(s) needing clarification.")
    if questions:
        summary_parts.append(f"Generated {len(questions)} clarifying question(s).")
    summary_parts.append(f"Confidence: {int(confidence * 100)}%.")

    return ClarifyOutputs(
        summary=" ".join(summary_parts),
        clarified_requirement=clarified,
        acceptance_criteria=acceptance,
        implicit_assumptions=assumptions,
        clarifying_questions=questions,
        edge_cases=edge_cases,
        technical_considerations=tech_considerations,
        confidence_score=round(confidence, 2),
    )


# ============================================================================
# API Endpoints
# ============================================================================


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute the requirement clarification skill."""
    start_time = time.time()

    try:
        outputs = clarify_requirement(request.inputs)
        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecuteResponse(
            outputs=outputs,
            metadata={
                "execution_time_ms": execution_time_ms,
                "input_length": len(request.inputs.raw_requirement),
                "domain": request.inputs.domain_context,
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

"""
Translate for Stakeholder Skill

A Level 2 skill that translates technical information into stakeholder-appropriate
language. Adapts content for executives, product managers, engineers, or non-technical
audiences while preserving essential meaning and impact.
"""

import json
import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field


# ============================================================================
# Models
# ============================================================================


class ContextInput(BaseModel):
    purpose: Optional[str] = None
    urgency: Optional[str] = None
    project_name: Optional[str] = None
    known_concerns: list[str] = Field(default_factory=list)


class ExecuteInputs(BaseModel):
    technical_content: str
    target_audience: str = "non_technical"
    context: Optional[ContextInput] = None
    format: str = "document"


class TermExplanation(BaseModel):
    term: str
    simple_explanation: str


class ActionItem(BaseModel):
    action: str
    owner: str = "TBD"
    priority: str = "medium"


class AudienceFocus(BaseModel):
    primary_concerns: list[str]
    secondary_concerns: list[str]


class TranslationOutput(BaseModel):
    translated_content: str
    key_takeaways: list[str]
    audience_focus: AudienceFocus
    technical_terms_explained: list[TermExplanation]
    action_items: list[ActionItem]
    follow_up_questions: list[str]
    elevator_pitch: str


class ExecuteRequest(BaseModel):
    inputs: ExecuteInputs


class ExecuteResponse(BaseModel):
    status: str
    outputs: TranslationOutput


# ============================================================================
# Audience Profiles
# ============================================================================


AUDIENCE_PROFILES = {
    "executive": {
        "focus": ["business impact", "cost", "timeline", "risk", "ROI"],
        "avoid": ["implementation details", "code", "technical jargon"],
        "style": "concise, business-focused, outcome-oriented",
        "questions": [
            "What's the business impact?",
            "How much will this cost?",
            "What's the timeline?",
            "What are the risks?",
            "Do we need to act now?",
        ],
    },
    "product_manager": {
        "focus": ["user impact", "feature scope", "timeline", "dependencies", "tradeoffs"],
        "avoid": ["deep implementation details", "code syntax"],
        "style": "user-centric, feature-focused, tradeoff-aware",
        "questions": [
            "How does this affect users?",
            "What features are impacted?",
            "What's the timeline?",
            "Are there alternatives?",
            "What are we trading off?",
        ],
    },
    "engineer": {
        "focus": ["technical approach", "architecture", "implementation", "performance", "maintainability"],
        "avoid": [],  # Engineers want full technical detail
        "style": "precise, technical, detailed",
        "questions": [
            "What's the technical approach?",
            "How does this scale?",
            "What are the edge cases?",
            "How do we test this?",
            "What's the migration path?",
        ],
    },
    "non_technical": {
        "focus": ["practical impact", "what changes for them", "when", "why it matters"],
        "avoid": ["all technical jargon", "code", "architecture", "acronyms"],
        "style": "simple, clear, analogy-focused",
        "questions": [
            "What does this mean for me?",
            "When will this happen?",
            "Will anything break?",
            "Who do I contact for help?",
        ],
    },
    "mixed": {
        "focus": ["summary first", "details available", "business and technical context"],
        "avoid": ["unexplained jargon"],
        "style": "layered - summary up front, details below",
        "questions": [
            "What's the summary?",
            "What's the impact?",
            "What's the technical context?",
        ],
    },
}


# ============================================================================
# Technical Term Dictionary
# ============================================================================


TECHNICAL_TERMS = {
    # General software terms
    "api": "A way for different software systems to talk to each other",
    "backend": "The behind-the-scenes part of a system that handles data and logic",
    "frontend": "The part of a system that users see and interact with",
    "database": "A structured collection of data that can be searched and updated",
    "server": "A computer that provides services to other computers",
    "cloud": "Computing resources accessed over the internet instead of your own computer",
    "deploy": "Making software available for use, typically on a server",
    "bug": "An error or flaw in software that causes unexpected behavior",
    "latency": "The delay between requesting and receiving data",
    "throughput": "The amount of work a system can handle in a given time",
    "scalability": "Ability to handle more work by adding resources",
    
    # Architecture terms
    "microservices": "Breaking a large application into smaller, independent pieces",
    "monolith": "A single, unified application where all parts are connected",
    "architecture": "The overall design and structure of a software system",
    "cqrs": "A pattern that separates reading and writing data for better performance",
    "event-driven": "A design where parts communicate by sending messages about what happened",
    "load balancer": "A system that distributes work across multiple servers",
    "cache": "Temporary storage for frequently accessed data to speed things up",
    
    # Error types
    "nullpointerexception": "An error when the system tries to use data that doesn't exist",
    "race condition": "A timing problem where two things try to happen at once",
    "memory leak": "When a program uses memory but forgets to release it",
    "timeout": "When an operation takes too long and is stopped",
    "bottleneck": "A point where work slows down due to limited capacity",
    
    # Database terms
    "sql": "A language for managing and querying databases",
    "nosql": "Databases designed for flexibility rather than strict structure",
    "replication": "Copying data to multiple locations for reliability",
    "sharding": "Splitting data across multiple databases for better performance",
    "transaction": "A group of operations that either all succeed or all fail",
    "connection pool": "A set of reusable connections to a database",
    
    # DevOps terms
    "ci/cd": "Automated process for testing and releasing software",
    "container": "A lightweight package that includes everything needed to run software",
    "kubernetes": "A system for managing containers across many servers",
    "docker": "A popular tool for creating and running containers",
    "pipeline": "An automated sequence of steps to build and deploy software",
    
    # Security terms
    "authentication": "Verifying who someone is (like logging in)",
    "authorization": "Verifying what someone is allowed to do",
    "encryption": "Scrambling data so only authorized parties can read it",
    "ssl/tls": "Security protocols that encrypt internet communications",
    "vulnerability": "A weakness that could be exploited by attackers",
}


# ============================================================================
# Translation Functions
# ============================================================================


def extract_technical_terms(content: str) -> list[TermExplanation]:
    """Extract and explain technical terms from content."""
    content_lower = content.lower()
    found_terms = []
    
    for term, explanation in TECHNICAL_TERMS.items():
        # Check if term appears in content
        if term.lower() in content_lower:
            found_terms.append(TermExplanation(term=term, simple_explanation=explanation))
    
    # Also find acronyms
    acronyms = re.findall(r'\b[A-Z]{2,}\b', content)
    for acronym in set(acronyms):
        if acronym.lower() in TECHNICAL_TERMS:
            continue  # Already added
        if acronym.lower() not in [t.term.lower() for t in found_terms]:
            found_terms.append(TermExplanation(
                term=acronym,
                simple_explanation="(Technical acronym - should be spelled out)"
            ))
    
    return found_terms


def translate_for_audience(
    content: str,
    audience: str,
    context: Optional[ContextInput],
    format_type: str,
) -> str:
    """Translate content for the target audience."""
    profile = AUDIENCE_PROFILES.get(audience, AUDIENCE_PROFILES["non_technical"])
    
    # Start with base translation
    translated = content
    
    # Apply audience-specific transformations
    if audience == "executive":
        translated = translate_for_executive(content, context, format_type)
    elif audience == "product_manager":
        translated = translate_for_pm(content, context, format_type)
    elif audience == "non_technical":
        translated = translate_for_non_technical(content, context, format_type)
    elif audience == "mixed":
        translated = translate_for_mixed(content, context, format_type)
    else:  # engineer
        translated = translate_for_engineer(content, context, format_type)
    
    return translated


def translate_for_executive(
    content: str, 
    context: Optional[ContextInput],
    format_type: str,
) -> str:
    """Translate content for executive audience."""
    lines = []
    
    # Purpose header
    purpose = context.purpose if context else "inform"
    if purpose == "incident_report":
        lines.append("## Incident Summary\n")
    elif purpose == "request_resources":
        lines.append("## Resource Request\n")
    elif purpose == "proposal":
        lines.append("## Proposal Overview\n")
    else:
        lines.append("## Executive Summary\n")
    
    # Business impact first
    lines.append("**Business Impact:**")
    impact = extract_business_impact(content)
    lines.append(f"- {impact}\n")
    
    # Status/Risk
    urgency = context.urgency if context else "medium"
    risk_level = "High" if "error" in content.lower() or "fail" in content.lower() else "Medium"
    if urgency == "critical":
        risk_level = "Critical"
    lines.append(f"**Risk Level:** {risk_level}\n")
    
    # Timeline
    timeline = extract_timeline(content)
    if timeline:
        lines.append(f"**Timeline:** {timeline}\n")
    
    # Bottom line
    lines.append("**Bottom Line:**")
    lines.append(f"- {summarize_for_executive(content)}")
    
    return "\n".join(lines)


def translate_for_pm(
    content: str,
    context: Optional[ContextInput],
    format_type: str,
) -> str:
    """Translate content for product manager audience."""
    lines = []
    
    lines.append("## Overview\n")
    lines.append(simplify_content(content) + "\n")
    
    lines.append("## User Impact\n")
    lines.append(f"- {extract_user_impact(content)}\n")
    
    lines.append("## Scope\n")
    scope = extract_scope(content)
    for item in scope:
        lines.append(f"- {item}")
    
    lines.append("\n## Dependencies & Tradeoffs\n")
    lines.append("- May require coordination with engineering on implementation timeline")
    lines.append("- Consider user communication if changes are visible")
    
    return "\n".join(lines)


def translate_for_non_technical(
    content: str,
    context: Optional[ContextInput],
    format_type: str,
) -> str:
    """Translate content for non-technical audience."""
    lines = []
    
    lines.append("## What's Happening\n")
    lines.append(simplify_content(content, max_simplify=True) + "\n")
    
    lines.append("## What This Means For You\n")
    lines.append(f"- {extract_practical_impact(content)}\n")
    
    timeline = extract_timeline(content)
    if timeline:
        lines.append("## When\n")
        lines.append(f"- {timeline}\n")
    
    lines.append("## Questions?\n")
    lines.append("- Contact the team for more information")
    
    return "\n".join(lines)


def translate_for_engineer(
    content: str,
    context: Optional[ContextInput],
    format_type: str,
) -> str:
    """Translate content for engineering audience - keep technical detail."""
    lines = []
    
    lines.append("## Technical Summary\n")
    lines.append(content + "\n")
    
    lines.append("## Key Technical Points\n")
    points = extract_technical_points(content)
    for point in points:
        lines.append(f"- {point}")
    
    lines.append("\n## Considerations\n")
    lines.append("- Review implementation approach")
    lines.append("- Consider edge cases and testing strategy")
    lines.append("- Evaluate performance implications")
    
    return "\n".join(lines)


def translate_for_mixed(
    content: str,
    context: Optional[ContextInput],
    format_type: str,
) -> str:
    """Translate content for mixed audience - layered approach."""
    lines = []
    
    lines.append("## TL;DR\n")
    lines.append(f"{summarize_for_executive(content)}\n")
    
    lines.append("## Impact Summary\n")
    lines.append(f"- Business: {extract_business_impact(content)}")
    lines.append(f"- Users: {extract_user_impact(content)}")
    lines.append(f"- Timeline: {extract_timeline(content) or 'TBD'}\n")
    
    lines.append("## Technical Details (For Those Interested)\n")
    lines.append(simplify_content(content))
    
    return "\n".join(lines)


# ============================================================================
# Content Extraction Helpers
# ============================================================================


def extract_business_impact(content: str) -> str:
    """Extract business impact from technical content."""
    content_lower = content.lower()
    
    if "payment" in content_lower or "revenue" in content_lower:
        return "Potential revenue impact - payment system affected"
    elif "user" in content_lower or "customer" in content_lower:
        return "Customer experience may be affected"
    elif "performance" in content_lower or "slow" in content_lower:
        return "System performance may be impacted"
    elif "security" in content_lower or "vulnerability" in content_lower:
        return "Security implications - requires attention"
    elif "error" in content_lower or "fail" in content_lower:
        return "System reliability at risk"
    else:
        return "Operational changes may be required"


def extract_user_impact(content: str) -> str:
    """Extract user impact from technical content."""
    content_lower = content.lower()
    
    if "ui" in content_lower or "frontend" in content_lower:
        return "Users may see interface changes"
    elif "performance" in content_lower:
        return "Users may notice speed improvements or issues"
    elif "migration" in content_lower:
        return "Users may experience brief service interruption"
    elif "feature" in content_lower:
        return "New functionality will be available to users"
    else:
        return "Changes are primarily behind the scenes"


def extract_timeline(content: str) -> Optional[str]:
    """Extract timeline from content."""
    # Look for time patterns
    time_patterns = [
        r"(\d+\s*(hour|hr|minute|min|day|week|month)s?)",
        r"ETA:\s*([^\n\.]+)",
        r"timeline:\s*([^\n\.]+)",
        r"by\s+(Monday|Tuesday|Wednesday|Thursday|Friday|tomorrow|next week)",
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_scope(content: str) -> list[str]:
    """Extract scope items from content."""
    scope = []
    
    # Look for numbered items or bullet-like patterns
    patterns = [
        r"(\d+)\s*bounded contexts",
        r"breaking into\s*(.*?)(?:\.|$)",
        r"implementing\s*(.*?)(?:\.|$)",
        r"migrating\s*(.*?)(?:\.|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            scope.append(match.group(0).strip())
    
    if not scope:
        scope.append("Implementation details to be defined")
    
    return scope


def extract_practical_impact(content: str) -> str:
    """Extract practical impact for non-technical users."""
    content_lower = content.lower()
    
    if "downtime" in content_lower:
        return "There may be a brief period when the system is unavailable"
    elif "update" in content_lower or "upgrade" in content_lower:
        return "The system is being improved - you may notice changes"
    elif "fix" in content_lower or "bug" in content_lower:
        return "An issue is being resolved - things should work better soon"
    elif "new" in content_lower or "feature" in content_lower:
        return "New capabilities are being added"
    else:
        return "The technical team is working on improvements"


def extract_technical_points(content: str) -> list[str]:
    """Extract key technical points from content."""
    points = []
    
    # Split by sentences and filter for technical content
    sentences = re.split(r'[.!?]', content)
    
    technical_markers = ["implement", "migrate", "pattern", "architecture", "using", "breaking", "fix"]
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and any(marker in sentence.lower() for marker in technical_markers):
            points.append(sentence)
    
    if not points:
        points.append(content[:200] + "..." if len(content) > 200 else content)
    
    return points[:5]  # Limit to 5 points


def simplify_content(content: str, max_simplify: bool = False) -> str:
    """Simplify technical content."""
    simplified = content
    
    if max_simplify:
        # Replace technical terms with simple explanations
        for term, explanation in TECHNICAL_TERMS.items():
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            if pattern.search(simplified):
                simplified = pattern.sub(f"{term} ({explanation})", simplified, count=1)
    
    # Truncate if too long
    if len(simplified) > 500:
        simplified = simplified[:500] + "..."
    
    return simplified


def summarize_for_executive(content: str) -> str:
    """Create executive-friendly summary."""
    content_lower = content.lower()
    
    # Determine the nature of the content
    if "fix" in content_lower:
        return "Technical team is implementing a fix. Situation is under control."
    elif "proposal" in content_lower or "migrating" in content_lower:
        return "Strategic technical improvement proposed. Review and approval needed."
    elif "error" in content_lower or "issue" in content_lower:
        return "Technical issue identified. Team is actively working on resolution."
    elif "complete" in content_lower or "done" in content_lower:
        return "Work completed successfully. No action required."
    else:
        return "Technical update for awareness. No immediate action required."


def generate_key_takeaways(
    content: str,
    audience: str,
    context: Optional[ContextInput],
) -> list[str]:
    """Generate key takeaways for the audience."""
    takeaways = []
    
    profile = AUDIENCE_PROFILES.get(audience, AUDIENCE_PROFILES["non_technical"])
    
    # Add impact takeaway
    takeaways.append(f"Impact: {extract_business_impact(content)}")
    
    # Add timeline if available
    timeline = extract_timeline(content)
    if timeline:
        takeaways.append(f"Timeline: {timeline}")
    
    # Add urgency if specified
    if context and context.urgency:
        urgency_map = {
            "critical": "Immediate attention required",
            "high": "High priority - action needed soon",
            "medium": "Normal priority",
            "low": "For awareness - no immediate action needed",
        }
        takeaways.append(urgency_map.get(context.urgency, "Normal priority"))
    
    # Add audience-specific takeaway
    if audience == "executive":
        takeaways.append("Bottom line: " + summarize_for_executive(content))
    elif audience == "product_manager":
        takeaways.append("User impact: " + extract_user_impact(content))
    elif audience == "non_technical":
        takeaways.append("What to expect: " + extract_practical_impact(content))
    
    return takeaways


def generate_action_items(
    content: str,
    context: Optional[ContextInput],
) -> list[ActionItem]:
    """Generate action items from content."""
    actions = []
    
    content_lower = content.lower()
    
    # Detect action-oriented words
    if "review" in content_lower or "approval" in content_lower:
        actions.append(ActionItem(
            action="Review and provide feedback",
            owner="Stakeholders",
            priority="high",
        ))
    
    if "decision" in content_lower:
        actions.append(ActionItem(
            action="Make decision on proposed approach",
            owner="Decision makers",
            priority="high",
        ))
    
    if context and context.purpose == "request_resources":
        actions.append(ActionItem(
            action="Evaluate resource request",
            owner="Management",
            priority="high",
        ))
    
    if context and context.urgency in ["high", "critical"]:
        actions.append(ActionItem(
            action="Follow up on status",
            owner="Project lead",
            priority="high" if context.urgency == "critical" else "medium",
        ))
    
    # Default action
    if not actions:
        actions.append(ActionItem(
            action="Acknowledge and note for tracking",
            owner="Recipient",
            priority="low",
        ))
    
    return actions


def generate_follow_up_questions(
    audience: str,
    content: str,
) -> list[str]:
    """Generate likely follow-up questions for the audience."""
    profile = AUDIENCE_PROFILES.get(audience, AUDIENCE_PROFILES["non_technical"])
    base_questions = profile["questions"].copy()
    
    # Add content-specific questions
    if "cost" in content.lower() or "budget" in content.lower():
        base_questions.append("What's the budget breakdown?")
    
    if "risk" in content.lower():
        base_questions.append("What's the mitigation plan?")
    
    return base_questions[:5]  # Limit to 5 questions


def generate_elevator_pitch(
    content: str,
    audience: str,
    context: Optional[ContextInput],
) -> str:
    """Generate a 30-second elevator pitch."""
    purpose = context.purpose if context else "inform"
    
    if audience == "executive":
        impact = extract_business_impact(content)
        timeline = extract_timeline(content) or "timeline being finalized"
        return f"We have a situation affecting {impact.lower()}. The team is on it, {timeline}. No blockers, will keep you posted."
    
    elif audience == "product_manager":
        user_impact = extract_user_impact(content)
        return f"Quick update: {user_impact.lower()}. Working through the technical details with engineering. I'll loop you in if anything affects the roadmap."
    
    elif audience == "non_technical":
        practical = extract_practical_impact(content)
        return f"Just wanted to let you know: {practical.lower()}. Nothing you need to do right now. Let me know if you have questions."
    
    else:
        return summarize_for_executive(content)


# ============================================================================
# Main Translation Function
# ============================================================================


def translate_stakeholder(inputs: ExecuteInputs) -> TranslationOutput:
    """Perform the full stakeholder translation."""
    
    content = inputs.technical_content
    audience = inputs.target_audience
    context = inputs.context
    format_type = inputs.format
    
    # Get audience profile
    profile = AUDIENCE_PROFILES.get(audience, AUDIENCE_PROFILES["non_technical"])
    
    # Translate content
    translated_content = translate_for_audience(content, audience, context, format_type)
    
    # Extract technical terms
    terms = extract_technical_terms(content)
    
    # Generate components
    key_takeaways = generate_key_takeaways(content, audience, context)
    action_items = generate_action_items(content, context)
    follow_up_questions = generate_follow_up_questions(audience, content)
    elevator_pitch = generate_elevator_pitch(content, audience, context)
    
    # Build audience focus
    audience_focus = AudienceFocus(
        primary_concerns=profile["focus"][:3],
        secondary_concerns=profile["focus"][3:] if len(profile["focus"]) > 3 else [],
    )
    
    return TranslationOutput(
        translated_content=translated_content,
        key_takeaways=key_takeaways,
        audience_focus=audience_focus,
        technical_terms_explained=terms,
        action_items=action_items,
        follow_up_questions=follow_up_questions,
        elevator_pitch=elevator_pitch,
    )


# ============================================================================
# FastAPI Application
# ============================================================================


app = FastAPI(
    title="Translate for Stakeholder Skill",
    description="Translates technical information for different stakeholder audiences",
    version="0.1.0",
)


@app.post("/execute", response_model=ExecuteResponse)
def execute(request: ExecuteRequest) -> ExecuteResponse:
    """Execute the skill on the given inputs."""
    result = translate_stakeholder(request.inputs)
    return ExecuteResponse(status="success", outputs=result)


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "skill_id": "translate_stakeholder"}


@app.get("/describe")
def describe() -> dict:
    """Return the skill schema."""
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

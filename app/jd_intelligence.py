import re
from .schemas import StructuredJD

# A small controlled vocabulary for the prototype. In production this would be
# a much larger skills taxonomy (e.g. ESCO, LinkedIn Skills API) or LLM-extracted.
KNOWN_SKILLS = [
    "python", "fastapi", "django", "flask", "java", "spring boot", "javascript",
    "react", "node.js", "postgresql", "mysql", "docker", "kubernetes", "aws",
    "gcp", "azure", "machine learning", "pytorch", "tensorflow", "llm",
    "langchain", "vector database", "faiss", "redis", "rag",
]

SENIORITY_MAP = {
    "intern": "Intern",
    "junior": "Junior",
    "senior": "Senior",
    "lead": "Lead",
    "staff": "Staff",
}


def _extract_skills(text: str, section: str = None):
    lower = text.lower()
    found = [s for s in KNOWN_SKILLS if s in lower]
    return found


def _extract_experience_years(text: str) -> int:
    match = re.search(r"(\d+)\+?\s*(?:years|yrs)", text.lower())
    return int(match.group(1)) if match else 0


def _extract_role(text: str) -> str:
    match = re.search(r"job title:\s*(.+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    first_line = text.strip().split("\n")[0]
    return first_line[:80]


def _extract_location(text: str) -> str:
    match = re.search(r"location:\s*(.+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_education(text: str) -> str:
    match = re.search(r"(bachelor'?s?|master'?s?|b\.?tech|m\.?tech|b\.?e|b\.?sc)[^\n.]*", text, re.IGNORECASE)
    return match.group(0).strip() if match else None


def _extract_seniority(text: str) -> str:
    lower = text.lower()
    for kw, label in SENIORITY_MAP.items():
        if kw in lower:
            return label
    return "Mid-level"


def extract_structured_jd(text: str) -> StructuredJD:
    """Rule-based extraction. Swap this for an LLM call (see README) once you
    wire up an API key -- keep the same StructuredJD output contract."""

    # naive split: treat "nice to have" section separately if present
    lower = text.lower()
    if "nice to have" in lower:
        required_part, nice_part = re.split(r"nice to have", text, flags=re.IGNORECASE, maxsplit=1)
    else:
        required_part, nice_part = text, ""

    required_skills = _extract_skills(required_part)
    nice_skills = [s for s in _extract_skills(nice_part) if s not in required_skills]

    return StructuredJD(
        role=_extract_role(text),
        required_skills=required_skills,
        nice_to_have_skills=nice_skills,
        min_experience_years=_extract_experience_years(text),
        education=_extract_education(text),
        location=_extract_location(text),
        domain=None,
        seniority=_extract_seniority(text),
        raw_text=text,
    )

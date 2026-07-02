import re
from .llm_client import LLMClientError, call_gemini_json, gemini_is_enabled
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
    """Extract a structured JD.

    Uses Gemini when `GEMINI_API_KEY` is available, and falls back to the
    rule-based extractor if the model call fails or is unavailable.
    """

    if gemini_is_enabled():
        prompt = (
            "You are extracting a job description into a strict JSON object.\n\n"
            "Return only valid JSON with exactly these keys:\n"
            "- role: string\n"
            "- required_skills: array of strings\n"
            "- nice_to_have_skills: array of strings\n"
            "- min_experience_years: integer\n"
            "- education: string or null\n"
            "- location: string or null\n"
            "- domain: string or null\n"
            "- seniority: string or null\n\n"
            "Rules:\n"
            "- Infer required skills from the responsibilities and requirements.\n"
            "- Infer nice-to-have skills from optional sections like 'nice to have' or 'preferred'.\n"
            "- Use lowercase skill names when possible.\n"
            "- Keep the output concise and grounded in the text.\n\n"
            f"Job description:\n{text}"
        )

        try:
            extracted = call_gemini_json(prompt)
            return StructuredJD(
                role=str(extracted.get("role", "")).strip() or _extract_role(text),
                required_skills=[str(skill).strip().lower() for skill in extracted.get("required_skills", []) if str(skill).strip()],
                nice_to_have_skills=[str(skill).strip().lower() for skill in extracted.get("nice_to_have_skills", []) if str(skill).strip()],
                min_experience_years=int(extracted.get("min_experience_years", 0) or 0),
                education=extracted.get("education") or None,
                location=extracted.get("location") or None,
                domain=extracted.get("domain") or None,
                seniority=extracted.get("seniority") or None,
                raw_text=text,
            )
        except (LLMClientError, ValueError, TypeError):
            pass

    """Rule-based extraction. Kept as a fallback for offline/demo runs."""

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

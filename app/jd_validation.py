from .schemas import ValidationResult

MIN_WORDS = 30
SKILL_HINTS = ["skill", "experience", "proficien", "knowledge of", "familiarity"]


def validate_jd(text: str) -> ValidationResult:
    issues = []
    suggestions = []
    score = 100

    if not text or not text.strip():
        return ValidationResult(
            is_valid=False, quality_score=0,
            issues=["Empty document"],
            suggestions=["Upload a non-empty job description."]
        )

    word_count = len(text.split())
    if word_count < MIN_WORDS:
        issues.append("Document too short to be a valid JD")
        suggestions.append("Provide a more detailed JD (role, skills, experience, responsibilities).")
        score -= 40

    lower = text.lower()
    if not any(h in lower for h in SKILL_HINTS):
        issues.append("Missing required skills section")
        suggestions.append("Add a clear list of required skills.")
        score -= 25

    if "experience" not in lower and "years" not in lower:
        issues.append("Missing experience requirement")
        suggestions.append("Specify minimum years of experience expected.")
        score -= 15

    # crude "wrong document" heuristic: resumes usually say "objective" or "career objective"
    if "career objective" in lower or "resume" in lower[:200]:
        issues.append("This looks like a resume, not a job description")
        suggestions.append("Please upload the job description document instead.")
        score -= 50

    score = max(score, 0)
    is_valid = score >= 50 and "This looks like a resume, not a job description" not in issues

    return ValidationResult(
        is_valid=is_valid,
        quality_score=score,
        issues=issues,
        suggestions=suggestions,
    )

from .llm_client import LLMClientError, call_gemini_json, gemini_is_enabled
from .schemas import StructuredJD


def generate_explanation(jd: StructuredJD, candidate: dict, ranking_result: dict, potential_result: dict, eligibility_reasons: list) -> dict:
    """Generate a candidate explanation.

    Uses Gemini when available, and falls back to the template-based
    explanation so the output contract stays stable.
    """

    candidate_skills = {s.lower() for s in candidate.get("skills", [])}
    matched_skills = sorted((set(jd.required_skills) | set(jd.nice_to_have_skills)) & candidate_skills)
    missing_skills = sorted(set(jd.required_skills) - candidate_skills)

    if gemini_is_enabled():
        prompt = (
            "You are explaining a candidate ranking result to a recruiter.\n\n"
            "Return only valid JSON with exactly these keys:\n"
            "- why_selected: string\n"
            "- strengths: array of strings\n"
            "- missing_skills: array of strings\n"
            "- eligibility_notes: array of strings\n\n"
            "Write 2-3 concise sentences in why_selected. Keep strengths and missing_skills short.\n\n"
            f"Job description:\n{jd.raw_text}\n\n"
            f"Candidate:\n{candidate}\n\n"
            f"Ranking signals:\n{ranking_result}\n\n"
            f"Future potential signals:\n{potential_result}\n\n"
            f"Eligibility reasons:\n{eligibility_reasons}"
        )

        try:
            explanation = call_gemini_json(prompt)
            return {
                "why_selected": str(explanation.get("why_selected", "")).strip() or (
                    f"Ranked based on a match score of {ranking_result['match_score']}/100 combining skill overlap, experience fit, and JD relevance."
                ),
                "strengths": [str(item).strip() for item in explanation.get("strengths", []) if str(item).strip()] or ["Meets baseline eligibility criteria"],
                "missing_skills": [str(item).strip() for item in explanation.get("missing_skills", []) if str(item).strip()] or missing_skills,
                "eligibility_notes": [str(item).strip() for item in explanation.get("eligibility_notes", []) if str(item).strip()] or eligibility_reasons,
            }
        except (LLMClientError, ValueError, TypeError):
            pass

    strengths = []
    signals = ranking_result["signals"]
    if signals["skill_match"] >= 0.6:
        strengths.append(f"Strong skill overlap ({', '.join(matched_skills) or 'core skills'})")
    if signals["experience_match"] >= 0.8:
        strengths.append("Meets or exceeds experience requirement")
    if signals["semantic_relevance"] >= 0.3:
        strengths.append("Resume content closely aligns with JD context")
    if potential_result["future_potential_score"] >= 60:
        strengths.append("High future potential (recent learning + hackathon activity)")

    why_selected = (
        f"Ranked based on a match score of {ranking_result['match_score']}/100 "
        f"combining skill overlap, experience fit, and JD relevance."
    )

    return {
        "why_selected": why_selected,
        "strengths": strengths or ["Meets baseline eligibility criteria"],
        "missing_skills": missing_skills,
        "eligibility_notes": eligibility_reasons,
    }

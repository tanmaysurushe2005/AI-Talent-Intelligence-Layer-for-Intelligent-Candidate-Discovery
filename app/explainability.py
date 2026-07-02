from .schemas import StructuredJD


def generate_explanation(jd: StructuredJD, candidate: dict, ranking_result: dict, potential_result: dict, eligibility_reasons: list) -> dict:
    """Template-based explanation. Upgrade path: pass this same context into
    an LLM call (Gemini/OpenAI) with a prompt like:
    'Explain in 2-3 sentences why this candidate ranked where they did,
    given these signals: {signals}'. Keep the output shape identical so the
    frontend doesn't need to change.
    """
    candidate_skills = {s.lower() for s in candidate.get("skills", [])}
    matched_skills = sorted((set(jd.required_skills) | set(jd.nice_to_have_skills)) & candidate_skills)
    missing_skills = sorted(set(jd.required_skills) - candidate_skills)

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

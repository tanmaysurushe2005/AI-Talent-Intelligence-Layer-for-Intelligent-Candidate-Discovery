from .schemas import StructuredJD

WEIGHTS = {
    "skill_match": 0.35,
    "experience_match": 0.20,
    "semantic_relevance": 0.25,
    "domain_match": 0.10,
    "certification_match": 0.10,
}


def _skill_match_score(jd: StructuredJD, candidate: dict) -> float:
    all_jd_skills = set(jd.required_skills) | set(jd.nice_to_have_skills)
    if not all_jd_skills:
        return 0.5
    candidate_skills = {s.lower() for s in candidate.get("skills", [])}
    overlap = all_jd_skills & candidate_skills
    return len(overlap) / len(all_jd_skills)


def _experience_score(jd: StructuredJD, candidate: dict) -> float:
    if jd.min_experience_years == 0:
        return 0.7
    exp = candidate.get("experience_years", 0)
    if exp >= jd.min_experience_years:
        # slight bonus for being close to requirement, cap benefit of way-over-qualified
        return min(1.0, 0.8 + 0.05 * min(exp - jd.min_experience_years, 4))
    return max(0.0, exp / jd.min_experience_years)


def _domain_score(jd: StructuredJD, candidate: dict) -> float:
    if not jd.domain or not candidate.get("domain"):
        return 0.5
    return 1.0 if jd.domain.lower() == candidate["domain"].lower() else 0.2


def _certification_score(jd: StructuredJD, candidate: dict) -> float:
    certs = candidate.get("certifications", [])
    if not certs:
        return 0.3
    relevant = [c for c in certs if any(s in c.lower() for s in jd.required_skills + jd.nice_to_have_skills)]
    return 1.0 if relevant else 0.5


def compute_match_score(jd: StructuredJD, candidate: dict, semantic_similarity: float) -> dict:
    signals = {
        "skill_match": _skill_match_score(jd, candidate),
        "experience_match": _experience_score(jd, candidate),
        "semantic_relevance": semantic_similarity,
        "domain_match": _domain_score(jd, candidate),
        "certification_match": _certification_score(jd, candidate),
    }
    weighted = sum(signals[k] * WEIGHTS[k] for k in signals)
    return {"signals": signals, "match_score": round(weighted * 100, 1)}

from .jd_validation import validate_jd
from .jd_intelligence import extract_structured_jd
from .eligibility import check_eligibility
from .retrieval import semantic_retrieve
from .ranking import compute_match_score
from .future_potential import compute_future_potential
from .confidence import compute_confidence
from .explainability import generate_explanation


def run_pipeline(jd_text: str, candidates: list, top_k: int = 10) -> dict:
    # Feature 1
    validation = validate_jd(jd_text)
    if not validation.is_valid:
        return {"validation": validation.dict(), "results": []}

    # Feature 2
    structured_jd = extract_structured_jd(jd_text)

    # Feature 3 -- filter out hard-ineligible candidates before the expensive steps
    eligibility_map = {}
    survivors = []
    for c in candidates:
        elig = check_eligibility(structured_jd, c)
        eligibility_map[c["id"]] = elig
        if elig.status != "Ineligible":
            survivors.append(c)

    # Feature 4
    retrieved = semantic_retrieve(jd_text, survivors, top_k=top_k)

    results = []
    for candidate, sim_score in retrieved:
        # Feature 5
        ranking_result = compute_match_score(structured_jd, candidate, sim_score)
        # Feature 6
        potential_result = compute_future_potential(candidate)
        # Feature 8
        confidence = compute_confidence(candidate)
        # Feature 7
        elig = eligibility_map[candidate["id"]]
        explanation = generate_explanation(structured_jd, candidate, ranking_result, potential_result, elig.reasons)

        final_score = round(0.7 * ranking_result["match_score"] + 0.3 * potential_result["future_potential_score"], 1)

        results.append({
            "candidate_id": candidate["id"],
            "name": candidate["name"],
            "match_score": ranking_result["match_score"],
            "future_potential_score": potential_result["future_potential_score"],
            "confidence_score": confidence,
            "final_score": final_score,
            "eligibility_status": elig.status,
            "signals": {**ranking_result["signals"], **potential_result["signals"]},
            "explanation": explanation,
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)

    return {
        "validation": validation.dict(),
        "structured_jd": structured_jd.dict(),
        "results": results,
    }

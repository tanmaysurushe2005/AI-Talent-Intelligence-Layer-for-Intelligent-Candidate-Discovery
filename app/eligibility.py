from .schemas import StructuredJD, EligibilityResult


def check_eligibility(jd: StructuredJD, candidate: dict) -> EligibilityResult:
    reasons = []
    hard_fail = False
    soft_fail = False

    candidate_skills = [s.lower() for s in candidate.get("skills", [])]
    matched_required = [s for s in jd.required_skills if s in candidate_skills]
    missing_required = [s for s in jd.required_skills if s not in candidate_skills]

    if jd.required_skills:
        match_ratio = len(matched_required) / len(jd.required_skills)
        if match_ratio == 0:
            hard_fail = True
            reasons.append("Matches none of the mandatory skills")
        elif match_ratio < 0.5:
            soft_fail = True
            reasons.append(f"Only matches {len(matched_required)}/{len(jd.required_skills)} mandatory skills")
        elif missing_required:
            reasons.append(f"Missing: {', '.join(missing_required)}")

    if jd.min_experience_years and candidate.get("experience_years", 0) < jd.min_experience_years:
        gap = jd.min_experience_years - candidate.get("experience_years", 0)
        if gap >= 2:
            hard_fail = True
            reasons.append(f"{gap} years short of required experience")
        else:
            soft_fail = True
            reasons.append(f"{gap} year(s) short of required experience")

    if not candidate.get("work_authorized", True):
        hard_fail = True
        reasons.append("Not authorized to work in required location")

    if jd.location and candidate.get("location") and jd.location.lower() != "remote":
        if candidate["location"].lower() != jd.location.lower() and candidate["location"].lower() != "remote":
            soft_fail = True
            reasons.append(f"Located in {candidate['location']}, JD prefers {jd.location}")

    if hard_fail:
        status = "Ineligible"
    elif soft_fail:
        status = "Borderline"
    else:
        status = "Eligible"
        if not reasons:
            reasons.append("Meets all mandatory criteria")

    return EligibilityResult(candidate_id=candidate["id"], status=status, reasons=reasons)

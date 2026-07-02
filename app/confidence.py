FIELDS_CHECKED = [
    "skills", "experience_years", "education", "projects",
    "certifications", "recent_learning", "summary",
]


def compute_confidence(candidate: dict) -> float:
    present = 0
    for field in FIELDS_CHECKED:
        val = candidate.get(field)
        if val not in (None, "", [], 0):
            present += 1
    completeness = present / len(FIELDS_CHECKED)
    return round(completeness * 100, 1)

CURRENT_YEAR = 2026


def _skill_freshness(candidate: dict) -> float:
    recent = candidate.get("recent_learning", [])
    if not recent:
        return 0.2
    # crude: more recent learning items -> fresher skillset
    return min(1.0, 0.3 + 0.2 * len(recent))


def _learning_velocity(candidate: dict) -> float:
    recent = candidate.get("recent_learning", [])
    exp = max(candidate.get("experience_years", 1), 1)
    # learning items per year of experience -- rewards fast learners regardless of tenure
    velocity = len(recent) / exp
    return min(1.0, velocity / 2)


def _career_progression(candidate: dict) -> float:
    # proxy: experience relative to project count/complexity signals (very rough for a prototype)
    projects = len(candidate.get("projects", []))
    exp = max(candidate.get("experience_years", 1), 1)
    return min(1.0, (projects / exp) / 1.5)


def _recency_score(candidate: dict) -> float:
    gap = CURRENT_YEAR - candidate.get("last_active_year", CURRENT_YEAR - 3)
    if gap <= 0:
        return 1.0
    return max(0.0, 1.0 - 0.25 * gap)


def _hackathon_score(candidate: dict) -> float:
    count = candidate.get("hackathons", 0)
    return min(1.0, count / 4)


def compute_future_potential(candidate: dict) -> dict:
    signals = {
        "skill_freshness": _skill_freshness(candidate),
        "learning_velocity": _learning_velocity(candidate),
        "career_progression": _career_progression(candidate),
        "recency": _recency_score(candidate),
        "hackathon_activity": _hackathon_score(candidate),
    }
    score = sum(signals.values()) / len(signals)
    return {"signals": signals, "future_potential_score": round(score * 100, 1)}

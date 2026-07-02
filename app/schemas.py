from pydantic import BaseModel
from typing import List, Optional


class StructuredJD(BaseModel):
    role: str
    required_skills: List[str]
    nice_to_have_skills: List[str] = []
    min_experience_years: int = 0
    education: Optional[str] = None
    location: Optional[str] = None
    domain: Optional[str] = None
    seniority: Optional[str] = None
    raw_text: str


class ValidationResult(BaseModel):
    is_valid: bool
    quality_score: int  # 0-100
    issues: List[str] = []
    suggestions: List[str] = []


class EligibilityResult(BaseModel):
    candidate_id: str
    status: str  # Eligible / Borderline / Ineligible
    reasons: List[str]


class RankedCandidate(BaseModel):
    candidate_id: str
    name: str
    match_score: float
    confidence_score: float
    future_potential_score: float
    final_score: float
    eligibility_status: str
    explanation: dict

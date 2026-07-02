# 🧠 AI Talent Intelligence Layer — Intelligent Candidate Discovery

> An AI-powered recruitment intelligence system that goes far beyond keyword matching. It reads a job description, understands what the role actually needs, and then finds, ranks, and explains the best candidates from your talent pool — all in seconds.

---

## 📖 Table of Contents

- [What Is This Project?](#-what-is-this-project)
- [Why Does This Exist?](#-why-does-this-exist)
- [Key Features at a Glance](#-key-features-at-a-glance)
- [System Architecture](#-system-architecture)
- [How the Pipeline Works (Step by Step)](#-how-the-pipeline-works-step-by-step)
- [Deep Dive: All 8 Features Explained](#-deep-dive-all-8-features-explained)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [Sample Data](#-sample-data)
- [Candidate Data Format](#-candidate-data-format)
- [Scoring and Ranking Explained](#-scoring-and-ranking-explained)
- [Optional Gemini AI Setup](#-optional-gemini-ai-setup)
- [Demo Walkthrough](#-demo-walkthrough)
- [Known Limitations](#-known-limitations)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 What Is This Project?

**AI Talent Intelligence Layer** is a complete end-to-end recruitment intelligence prototype that automates the process of matching candidates to job descriptions. 

In traditional hiring, a recruiter reads a job description (JD), then manually scans through hundreds of resumes to find good matches. This is slow, inconsistent, and biased toward keyword matches.

**This system replaces that manual process with an 8-stage intelligent pipeline:**

1. It **validates** whether the uploaded document is actually a proper job description
2. It **extracts** structured information from the JD (skills, experience, role, etc.)
3. It **filters out** clearly ineligible candidates (wrong domain, missing key skills, not authorized)
4. It **semantically searches** to find candidates whose experience actually matches the JD — not just keyword overlap
5. It **scores candidates** across multiple signals (skills, experience, certifications, domain fit)
6. It **evaluates future potential** (learning velocity, recent activity, career progression)
7. It **generates human-readable explanations** for why each candidate was ranked where they are
8. It **assigns confidence scores** based on how complete each candidate's profile data is

The result is a **ranked shortlist** with detailed explanations that a recruiter can immediately act on.

---

## 💡 Why Does This Exist?

| Traditional Hiring | With This System |
|---|---|
| Recruiter manually reads 100+ resumes | System processes entire talent pool in seconds |
| Keyword matching misses good candidates | Semantic understanding finds relevant matches even without exact keywords |
| No explanation for why someone was shortlisted | Every ranking comes with a clear explanation |
| Ignores growth potential of junior candidates | Future potential engine rewards fast learners |
| Same output regardless of JD quality | Validates the JD first and suggests improvements |
| Inconsistent — depends on recruiter's mood and time | Consistent, reproducible scoring across all candidates |

---

## ✨ Key Features at a Glance

| # | Feature | What It Does | Module |
|:-:|---------|-------------|--------|
| 1 | **JD Validation** | Checks if the uploaded document is a real, high-quality job description | `app/jd_validation.py` |
| 2 | **JD Intelligence** | Extracts structured data — role, skills, experience, location, seniority — from raw JD text | `app/jd_intelligence.py` |
| 3 | **Rule-Based Eligibility** | Filters out candidates who clearly don't meet hard requirements (experience, work authorization, skills) | `app/eligibility.py` |
| 4 | **Semantic Retrieval** | Uses AI embeddings to find candidates whose background genuinely matches the JD (not just keywords) | `app/retrieval.py` |
| 5 | **Multi-Signal Ranking** | Combines 5 different scoring signals with configurable weights to produce a match score | `app/ranking.py` |
| 6 | **Future Potential Engine** | Evaluates candidates' growth trajectory — recent learning, hackathon activity, career progression | `app/future_potential.py` |
| 7 | **Explainability** | Generates recruiter-friendly explanations for every ranking decision | `app/explainability.py` |
| 8 | **Confidence Score** | Measures how complete/reliable a candidate's profile data is | `app/confidence.py` |

---

## 🏗 System Architecture

Below is a high-level view of how all the components fit together:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACES                                    │
│                                                                             │
│    ┌──────────────────────┐         ┌──────────────────────────────┐        │
│    │   Streamlit Web UI   │         │     FastAPI REST API         │        │
│    │  (frontend/          │         │   (app/main.py)              │        │
│    │   streamlit_app.py)  │         │                              │        │
│    │                      │         │  GET  /candidates            │        │
│    │  • Paste/edit JD     │         │  POST /rank      (file)      │        │
│    │  • View rankings     │         │  POST /rank_text (JSON)      │        │
│    │  • Score breakdowns  │         │  GET  /docs      (Swagger)   │        │
│    │  • Export JSON/CSV   │         │                              │        │
│    └──────────┬───────────┘         └──────────────┬───────────────┘        │
│               │                                    │                        │
│               └─────────────┬──────────────────────┘                        │
│                             ▼                                               │
│                   ┌─────────────────┐                                       │
│                   │   PIPELINE      │                                       │
│                   │ (app/pipeline.py)│                                      │
│                   └────────┬────────┘                                       │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────────────────┐
          │     8-STAGE INTELLIGENCE PIPELINE                │
          │                                                  │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 1: JD Validation                 │    │
          │   │  ─────────────────────────              │    │
          │   │  • Checks word count ≥ 30               │    │
          │   │  • Looks for skills section              │    │
          │   │  • Verifies experience mentioned         │    │
          │   │  • Detects if resume uploaded by mistake  │    │
          │   │  • Returns quality score (0-100)         │    │
          │   │  • Stops pipeline if score < 50          │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 2: JD Intelligence               │    │
          │   │  ────────────────────────                │    │
          │   │  Extracts structured fields:             │    │
          │   │  • Role title                            │    │
          │   │  • Required skills (list)                │    │
          │   │  • Nice-to-have skills (list)            │    │
          │   │  • Minimum experience (years)            │    │
          │   │  • Education requirement                 │    │
          │   │  • Location preference                   │    │
          │   │  • Domain / industry                     │    │
          │   │  • Seniority level                       │    │
          │   │                                          │    │
          │   │  🤖 Uses Gemini if API key set           │    │
          │   │  📋 Falls back to regex/rules offline    │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 3: Eligibility Filter             │    │
          │   │  ───────────────────────                 │    │
          │   │  Hard filters (→ Ineligible):            │    │
          │   │  • 0% required skill match               │    │
          │   │  • 2+ years short on experience          │    │
          │   │  • Not work-authorized                   │    │
          │   │                                          │    │
          │   │  Soft filters (→ Borderline):            │    │
          │   │  • < 50% required skills                 │    │
          │   │  • 1 year short on experience            │    │
          │   │  • Location mismatch                     │    │
          │   │                                          │    │
          │   │  ✅ Ineligible candidates removed before │    │
          │   │     expensive retrieval step              │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 4: Semantic Retrieval             │    │
          │   │  ──────────────────────                  │    │
          │   │  Converts JD + candidate profiles to     │    │
          │   │  vector embeddings, then finds closest   │    │
          │   │  matches via cosine similarity            │    │
          │   │                                          │    │
          │   │  Primary: sentence-transformers           │    │
          │   │    (all-MiniLM-L6-v2, ~90MB model)       │    │
          │   │  Fallback: TF-IDF (scikit-learn)         │    │
          │   │                                          │    │
          │   │  Returns top-K candidates ranked by      │    │
          │   │  semantic similarity to JD               │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 5: Multi-Signal Ranking           │    │
          │   │  ────────────────────────                 │    │
          │   │  Computes a weighted match score:         │    │
          │   │                                          │    │
          │   │  Signal              Weight               │    │
          │   │  ──────              ──────               │    │
          │   │  Skill match         35%                  │    │
          │   │  Semantic relevance  25%                  │    │
          │   │  Experience match    20%                  │    │
          │   │  Domain match        10%                  │    │
          │   │  Certification match 10%                  │    │
          │   │                                          │    │
          │   │  Output: match_score (0-100)             │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 6: Future Potential Engine         │    │
          │   │  ───────────────────────────              │    │
          │   │  Evaluates growth trajectory via:         │    │
          │   │  • Skill freshness (recent learning)     │    │
          │   │  • Learning velocity (items per year)    │    │
          │   │  • Career progression (projects/exp)     │    │
          │   │  • Recency (last active year)            │    │
          │   │  • Hackathon activity                    │    │
          │   │                                          │    │
          │   │  Output: future_potential_score (0-100)  │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 7: Explainability                 │    │
          │   │  ──────────────────                      │    │
          │   │  Generates human-readable explanation:    │    │
          │   │  • why_selected (2-3 sentences)          │    │
          │   │  • strengths (list)                      │    │
          │   │  • missing_skills (list)                 │    │
          │   │  • eligibility_notes (list)              │    │
          │   │                                          │    │
          │   │  🤖 Uses Gemini for narratives if avail  │    │
          │   │  📋 Falls back to template-based output  │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │   ┌─────────────────────────────────────────┐    │
          │   │  STAGE 8: Confidence Score               │    │
          │   │  ────────────────────                    │    │
          │   │  Checks data completeness of profile:    │    │
          │   │  • skills ✓/✗                            │    │
          │   │  • experience_years ✓/✗                  │    │
          │   │  • education ✓/✗                         │    │
          │   │  • projects ✓/✗                          │    │
          │   │  • certifications ✓/✗                    │    │
          │   │  • recent_learning ✓/✗                   │    │
          │   │  • summary ✓/✗                           │    │
          │   │                                          │    │
          │   │  Output: confidence_score (0-100%)       │    │
          │   └──────────────┬──────────────────────────┘    │
          │                  ▼                                │
          │            FINAL SCORE                            │
          │   ┌─────────────────────────────────────────┐    │
          │   │  final_score = 0.7 × match_score        │    │
          │   │              + 0.3 × future_potential    │    │
          │   │                                          │    │
          │   │  Candidates sorted by final_score (desc) │    │
          │   └─────────────────────────────────────────┘    │
          └──────────────────────────────────────────────────┘
                             │
                             ▼
          ┌──────────────────────────────────────────────────┐
          │                  OUTPUT                           │
          │                                                  │
          │  Ranked list of candidates, each containing:     │
          │  • name, candidate_id                            │
          │  • match_score, future_potential_score            │
          │  • confidence_score, final_score                 │
          │  • eligibility_status (Eligible/Borderline)      │
          │  • signals breakdown (10 individual signals)     │
          │  • explanation (why selected, strengths, gaps)   │
          │                                                  │
          │  Available as: JSON response, CSV download,      │
          │  or interactive Streamlit dashboard               │
          └──────────────────────────────────────────────────┘
```

### Architecture Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Offline-First** | Every component works without internet. AI features (Gemini) are optional enhancements, not dependencies. |
| **Graceful Degradation** | If the sentence-transformer model can't download, TF-IDF kicks in. If Gemini fails, rule-based logic takes over. |
| **Modular Pipeline** | Each of the 8 features is a standalone module. You can modify or replace any single stage without touching the others. |
| **Dual Interface** | Same pipeline powers both a Streamlit UI (for demos) and a FastAPI REST API (for integrations). |
| **Explainable AI** | Every score comes with a full breakdown — no black-box rankings. |

---

## 🔄 How the Pipeline Works (Step by Step)

Here's what happens from the moment you paste a job description to seeing the ranked results:

### Step 1 — You provide a Job Description
You paste a JD into the Streamlit UI (or send it via API). Example:
```
Job Title: Backend Engineer (Python)
Requirements: 2+ years experience, Python, FastAPI, PostgreSQL, Docker, AWS...
```

### Step 2 — The JD Gets Validated (Feature 1)
The system checks:
- Is it long enough (≥ 30 words)?
- Does it mention required skills?
- Does it mention experience requirements?
- Is it actually a JD and not a resume?

If the quality score falls below 50, the pipeline **stops** and tells you what's wrong.

### Step 3 — Structured Data Is Extracted (Feature 2)
The raw JD text is parsed into structured fields:
```json
{
  "role": "Backend Engineer (Python)",
  "required_skills": ["python", "fastapi", "postgresql", "docker", "aws"],
  "nice_to_have_skills": ["llm", "vector database"],
  "min_experience_years": 2,
  "education": "Bachelor's degree in Computer Science",
  "location": "Pune",
  "seniority": "Mid-level"
}
```
If you have a Gemini API key, this uses Google's AI for better extraction. Otherwise, regex and keyword matching handle it.

### Step 4 — Ineligible Candidates Are Filtered (Feature 3)
Before doing any expensive computation, the system removes clearly unqualified candidates:
- **Ineligible** (hard fail): no matching skills at all, 2+ years short on experience, not work-authorized
- **Borderline** (soft fail): partial skill match, slightly short on experience, location mismatch
- **Eligible**: meets all mandatory criteria

Only Eligible and Borderline candidates proceed to the next stages.

### Step 5 — Semantic Search Finds Relevant Candidates (Feature 4)
Each remaining candidate's profile (summary + skills + projects + domain) is converted into a vector embedding. The JD is also embedded. Cosine similarity finds the candidates whose profiles are closest in meaning to the JD.

This is powerful because it understands context:
- A candidate who "built scalable APIs with FastAPI" will match a JD asking for "backend API development" even without exact keyword overlap.

### Step 6 — Multi-Signal Scoring (Feature 5)
Each candidate receives a score based on 5 weighted signals:
- **Skill Match (35%)** — What % of JD skills does the candidate have?
- **Semantic Relevance (25%)** — How similar is their profile to the JD (from Step 5)?
- **Experience Match (20%)** — Do they meet the experience requirement?
- **Domain Match (10%)** — Are they in the same industry/domain?
- **Certification Match (10%)** — Do they have relevant certifications?

### Step 7 — Future Potential Assessment (Feature 6)
Even if a candidate doesn't perfectly match today, they might be a high-potential hire. This engine evaluates:
- **Skill Freshness** — Have they learned new things recently?
- **Learning Velocity** — How many new skills per year of experience?
- **Career Progression** — Projects relative to experience
- **Recency** — When were they last active?
- **Hackathon Activity** — Signals initiative and speed

### Step 8 — Final Score and Explanation (Features 7 & 8)
```
Final Score = (0.7 × Match Score) + (0.3 × Future Potential Score)
```

Each candidate also gets:
- A **confidence score** (how complete their profile data is)
- A **human-readable explanation** covering why they were selected, their strengths, missing skills, and eligibility notes

Candidates are sorted by final score and displayed as a ranked shortlist.

---

## 🔍 Deep Dive: All 8 Features Explained

### Feature 1: JD Validation (`app/jd_validation.py`)

**Purpose:** Catch bad inputs before the pipeline wastes time processing them.

**How it works:**
- Starts with a quality score of 100
- Deducts points for issues:
  - Document too short (< 30 words): **-40 points**
  - No skills section detected: **-25 points**
  - No experience requirement: **-15 points**
  - Document looks like a resume: **-50 points**
- If final score < 50 → **pipeline stops** with actionable suggestions

**Example output:**
```json
{
  "is_valid": true,
  "quality_score": 100,
  "issues": [],
  "suggestions": []
}
```

---

### Feature 2: JD Intelligence (`app/jd_intelligence.py`)

**Purpose:** Convert unstructured JD text into a machine-readable format.

**Two modes:**
1. **Gemini Mode** (when `GEMINI_API_KEY` is set): Sends the JD to Google's Gemini AI model, which returns a structured JSON with role, skills, experience, etc.
2. **Offline Mode** (default): Uses regex patterns and a hardcoded skills vocabulary to extract the same fields.

**Skills vocabulary:** 24 common tech skills are recognized (Python, FastAPI, Django, React, AWS, Docker, Kubernetes, machine learning, etc.). This would be replaced with a larger taxonomy (like LinkedIn Skills or ESCO) in production.

---

### Feature 3: Rule-Based Eligibility (`app/eligibility.py`)

**Purpose:** Fast pre-filtering to remove clearly unqualified candidates.

**Classification rules:**

| Check | Hard Fail (Ineligible) | Soft Fail (Borderline) |
|-------|----------------------|----------------------|
| Skill match | 0% of required skills | < 50% of required skills |
| Experience | 2+ years short | 1 year short |
| Work authorization | Not authorized | — |
| Location | — | Different city (and JD isn't "Remote") |

Ineligible candidates are **removed from the pool** before semantic retrieval, saving computation.

---

### Feature 4: Semantic Retrieval (`app/retrieval.py`)

**Purpose:** Find the most contextually relevant candidates using AI embeddings.

**How it works:**
1. Each candidate's text (summary + skills + projects + domain) is concatenated into a single string
2. The JD and all candidate strings are encoded into dense vectors
3. Cosine similarity finds the closest matches
4. Returns the top-K most similar candidates

**Embedding model:** `all-MiniLM-L6-v2` from sentence-transformers (~90MB, downloads once, then cached)

**Fallback:** If the model can't be loaded (offline, blocked), TF-IDF vectorization from scikit-learn is used automatically. You'll see a console message: `[retrieval] sentence-transformers unavailable; falling back to TF-IDF`.

---

### Feature 5: Multi-Signal Ranking (`app/ranking.py`)

**Purpose:** Produce a holistic match score by blending multiple evaluation criteria.

**Signal weights:**
```
Skill Match:          35%  — % overlap between JD skills and candidate skills
Semantic Relevance:   25%  — cosine similarity from Feature 4
Experience Match:     20%  — how well candidate meets experience requirement
Domain Match:         10%  — same industry/domain?
Certification Match:  10%  — relevant certifications present?
```

**Output:** `match_score` from 0 to 100.

---

### Feature 6: Future Potential Engine (`app/future_potential.py`)

**Purpose:** Identify high-growth candidates who may not be a perfect match today but are investing heavily in relevant skills.

**Five signals evaluated:**
| Signal | What It Measures | Example |
|--------|-----------------|---------|
| Skill Freshness | Recent learning items | "LangChain (2025)" counts |
| Learning Velocity | Learning items ÷ years of experience | Fresh grad with 3 items = high velocity |
| Career Progression | Projects ÷ experience years | More projects per year = faster progression |
| Recency | Years since last active | Active in 2026 = full score |
| Hackathon Activity | Number of hackathons | 4+ hackathons = maximum score |

**Output:** `future_potential_score` from 0 to 100.

---

### Feature 7: Explainability (`app/explainability.py`)

**Purpose:** Every ranking decision should be transparent and understandable.

**Output format:**
```json
{
  "why_selected": "Ranked based on a match score of 78.5/100 combining skill overlap, experience fit, and JD relevance.",
  "strengths": ["Strong skill overlap (python, fastapi, postgresql)", "Meets or exceeds experience requirement"],
  "missing_skills": ["docker"],
  "eligibility_notes": ["Missing: docker"]
}
```

With Gemini enabled, the explanations become more natural and recruiter-friendly.

---

### Feature 8: Confidence Score (`app/confidence.py`)

**Purpose:** Flag candidates whose rankings might be unreliable due to incomplete data.

**Checks 7 profile fields:**
- `skills`, `experience_years`, `education`, `projects`, `certifications`, `recent_learning`, `summary`

**Formula:** `confidence = (fields_present ÷ 7) × 100`

A candidate with all 7 fields filled = 100% confidence. Missing data = lower confidence, so the recruiter knows to verify.

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | FastAPI 0.115 | REST API serving the pipeline |
| **Web Server** | Uvicorn 0.30 | ASGI server for FastAPI |
| **Frontend UI** | Streamlit 1.38 | Interactive demo dashboard |
| **Embeddings** | sentence-transformers 5.6 | Semantic search via `all-MiniLM-L6-v2` |
| **ML Utilities** | scikit-learn 1.5 | TF-IDF fallback + cosine similarity |
| **Data Validation** | Pydantic 2.9 | Schema validation for JD, candidates, results |
| **File Uploads** | python-multipart 0.0.9 | Multipart form handling in FastAPI |
| **AI (Optional)** | Google Gemini API | Enhanced JD extraction + explanations |
| **Language** | Python 3.13 | Tested and verified on Python 3.13 |

---

## 📁 Project Structure

```
talent_intel/
│
├── app/                          # Core backend (the intelligence layer)
│   ├── main.py                   # FastAPI application — defines API endpoints
│   ├── pipeline.py               # Orchestrates all 8 features in sequence
│   ├── schemas.py                # Pydantic data models (StructuredJD, ValidationResult, etc.)
│   ├── jd_validation.py          # Feature 1 — JD quality validation
│   ├── jd_intelligence.py        # Feature 2 — JD parsing and extraction
│   ├── eligibility.py            # Feature 3 — Rule-based candidate filtering
│   ├── retrieval.py              # Feature 4 — Semantic search with embeddings
│   ├── ranking.py                # Feature 5 — Multi-signal match scoring
│   ├── future_potential.py       # Feature 6 — Growth/potential evaluation
│   ├── explainability.py         # Feature 7 — Human-readable explanations
│   ├── confidence.py             # Feature 8 — Profile completeness scoring
│   └── llm_client.py             # Gemini API client (shared by Features 2 & 7)
│
├── frontend/                     # User interface
│   └── streamlit_app.py          # Streamlit web dashboard
│
├── data/                         # Sample data for testing
│   ├── sample_resumes.json       # 18 synthetic candidate profiles
│   └── sample_jd.txt             # Sample job description
│
├── scripts/                      # Utility scripts
│   └── generate_dataset.py       # Script to regenerate/modify the candidate pool
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13** (recommended; other 3.x versions may work)
- **pip** (Python package manager)
- **Internet access** for first run only (to download the ~90MB embedding model)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/tanmaysurushe2005/AI-Talent-Intelligence-Layer-for-Intelligent-Candidate-Discovery.git
cd talent_intel

# 2. Create a virtual environment (recommended)
python -m venv .venv

# 3. Activate the virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

**First run note:** The first time you run the app, the `all-MiniLM-L6-v2` model (~90MB) will download from Hugging Face. After that, it's cached locally and everything works offline.

---

## ▶ Running the Application

### Option A: Streamlit Dashboard (Recommended for Demos)

```bash
streamlit run frontend/streamlit_app.py
```

This opens a browser window with:
- A text area to paste/edit a job description
- A slider to set how many candidates to shortlist
- A "Run" button to execute the pipeline
- A candidate pool overview table
- Ranked results with score breakdowns, explanations, and export buttons

### Option B: FastAPI REST API (For Integrations)

```bash
uvicorn app.main:app --reload
```

This starts a REST API at `http://localhost:8000` with interactive Swagger docs at `http://localhost:8000/docs`.

---

## 📡 API Reference

### `GET /`
Health check endpoint.
```json
{"status": "ok", "message": "AI Talent Intelligence Layer prototype API"}
```

### `GET /candidates`
Returns the full candidate pool from `data/sample_resumes.json`.

### `POST /rank_text`
Rank candidates against a JD provided as JSON.

**Request:**
```json
{
  "jd_text": "Job Title: Backend Engineer...",
  "top_k": 5
}
```

**Response:**
```json
{
  "validation": {
    "is_valid": true,
    "quality_score": 100,
    "issues": [],
    "suggestions": []
  },
  "structured_jd": {
    "role": "Backend Engineer (Python)",
    "required_skills": ["python", "fastapi", "postgresql", "docker", "aws"],
    "nice_to_have_skills": ["llm", "vector database"],
    "min_experience_years": 2,
    "education": "Bachelor's degree in Computer Science",
    "location": "Pune",
    "seniority": "Mid-level"
  },
  "results": [
    {
      "candidate_id": "R014",
      "name": "Siddharth Rao",
      "match_score": 85.2,
      "future_potential_score": 78.0,
      "confidence_score": 100.0,
      "final_score": 83.0,
      "eligibility_status": "Eligible",
      "signals": { ... },
      "explanation": {
        "why_selected": "...",
        "strengths": ["..."],
        "missing_skills": [],
        "eligibility_notes": ["Meets all mandatory criteria"]
      }
    }
  ]
}
```

### `POST /rank`
Same as `/rank_text`, but accepts the JD as a **file upload** (multipart form).

**Parameters:**
- `jd_file` (file): The job description document
- `top_k` (int, default 10): Number of candidates to return

---

## 📊 Sample Data

### Candidate Pool (18 profiles)

The included dataset (`data/sample_resumes.json`) contains 18 carefully designed synthetic candidates that test different scenarios:

| Candidate | Scenario Being Tested |
|-----------|----------------------|
| Aditi Sharma | Strong match — all required skills, right location |
| Rohan Mehta | Wrong language stack (Java, not Python), stale activity |
| Sneha Iyer | AI specialist — adjacent but not direct backend fit |
| Karan Verma | Junior dev — low experience but high learning velocity |
| Priya Nair | Frontend dev — completely wrong domain |
| Vikram Rao | Senior backend — strong but uses GCP instead of AWS |
| Ananya Deshpande | Career changer — transitioning to FastAPI from Flask |
| Farhan Sheikh | Embedded systems — total domain mismatch |
| Meera Krishnan | Well-rounded senior — strong all-around fit |
| Arjun Kapoor | Stale senior — 8 years experience but inactive since 2021 |
| Ishita Bansal | Fresh grad — zero experience but extreme learning velocity |
| Devansh Patil | Skills match but **not work-authorized** (should be filtered) |
| Neha Joshi | Data scientist — adjacent domain, not backend |
| Siddharth Rao | **Near-perfect match** — has required + nice-to-have skills |
| Tanvi Oak | Frontend dev — eligibility filter test case |
| Yash Kulkarni | Mid-tier match — MySQL instead of PostgreSQL |
| Ritika Chawla | Go backend dev — wrong language, right domain |
| Om Ghosh | Overqualified — principal engineer, 10 years exp |

### Sample Job Description

The included JD (`data/sample_jd.txt`) describes a **Backend Engineer (Python)** role requiring Python, FastAPI, PostgreSQL, Docker, AWS — with LLM/vector DB experience as nice-to-have.

---

## 📋 Candidate Data Format

Each candidate in `sample_resumes.json` follows this schema:

```json
{
  "id": "R001",
  "name": "Aditi Sharma",
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
  "experience_years": 3,
  "education": "B.Tech Computer Science",
  "location": "Pune",
  "work_authorized": true,
  "domain": "Backend Engineering",
  "certifications": ["AWS Certified Developer"],
  "projects": [
    "Built a scalable order-processing microservice handling 10k req/min",
    "Led migration from monolith to FastAPI microservices"
  ],
  "recent_learning": ["LangChain (2025)", "Kubernetes (2025)"],
  "hackathons": 2,
  "last_active_year": 2026,
  "summary": "Backend engineer with 3 years building scalable APIs and cloud infra."
}
```

| Field | Type | Used By |
|-------|------|---------|
| `id` | string | Unique identifier |
| `name` | string | Display name |
| `skills` | string[] | Eligibility, Ranking, Retrieval |
| `experience_years` | int | Eligibility, Ranking, Future Potential |
| `education` | string | Confidence Score |
| `location` | string | Eligibility |
| `work_authorized` | bool | Eligibility (hard filter) |
| `domain` | string | Ranking, Retrieval |
| `certifications` | string[] | Ranking, Confidence Score |
| `projects` | string[] | Retrieval, Future Potential, Confidence |
| `recent_learning` | string[] | Future Potential |
| `hackathons` | int | Future Potential |
| `last_active_year` | int | Future Potential |
| `summary` | string | Retrieval, Confidence Score |

To use your own data, create a JSON file with the same structure and place it at `data/sample_resumes.json`.

---

## 🧮 Scoring and Ranking Explained

### Match Score (0–100)

Calculated as a weighted sum of 5 signals:

```
match_score = (0.35 × skill_match)
            + (0.25 × semantic_relevance)
            + (0.20 × experience_match)
            + (0.10 × domain_match)
            + (0.10 × certification_match)
```

Each signal is a value between 0.0 and 1.0. The result is scaled to 0–100.

### Future Potential Score (0–100)

Simple average of 5 growth signals:

```
future_potential = mean(skill_freshness, learning_velocity,
                        career_progression, recency, hackathon_activity)
```

### Final Score (0–100)

```
final_score = (0.7 × match_score) + (0.3 × future_potential_score)
```

The **70/30 split** means current fit matters more, but high-potential candidates still get a meaningful boost.

### Confidence Score (0–100%)

```
confidence = (number of non-empty fields ÷ 7) × 100
```

A confidence of 57% means only 4 out of 7 profile fields have data — the ranking for that candidate is less reliable.


## 🎬 Demo Walkthrough

### Quick Demo (2 minutes)

1. **Start the app:**
   ```bash
   streamlit run frontend/streamlit_app.py
   ```
2. **Keep the default JD** (Backend Engineer, Python) or paste your own
3. **Click "Run Talent Intelligence Pipeline"**
4. **Show the results:**
   - Point out the #1 ranked candidate and their explanation
   - Expand the "Score breakdown" to show the 10 individual signals
   - Open the "Structured JD" expander to show what was extracted
   - Use the download buttons (JSON/CSV) to export results


## 🗺 Future Roadmap

1. **Vector Database Integration** — Replace brute-force cosine similarity with FAISS or Chroma for pools of 1,000+ candidates
2. **Learning-to-Rank** — Train a model on real hiring outcomes to learn optimal signal weights
3. **Resume Parsing** — Accept PDF/DOCX resumes and auto-extract candidate profiles
4. **Multi-JD Comparison** — Rank the same candidate pool against multiple JDs simultaneously
5. **Bias Detection** — Add fairness checks to flag potential bias in rankings
6. **Feedback Loop** — Let recruiters rate recommendations to improve the system over time
7. **Production Deployment** — Dockerize, add CI/CD, monitoring, and authentication




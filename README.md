# AI Talent Intelligence Layer — Prototype

Working prototype of all 8 features from the project doc, built to run **fully offline** with
no API key required, so you have something demoable today. Optional Gemini support is wired in
for JD Intelligence and Explainability if you set an API key.

## Progress so far

- Feature 4 now uses sentence-transformer embeddings with an automatic TF-IDF fallback.
- The sample dataset was expanded from 5 to 18 candidates so the ranking path is exercised on
   stronger matches, near-misses, and edge cases.
- Feature 2 and Feature 7 can now use Gemini when `GEMINI_API_KEY` is present, while keeping the
   original offline rule-based fallback.

## What's implemented

| # | Feature | How it's done here |
|---|---------|--------------------|
| 1 | JD Validation | Rule-based (`app/jd_validation.py`) |
| 2 | JD Intelligence | Regex/keyword extraction with optional Gemini JSON output (`app/jd_intelligence.py`) |
| 3 | Rule-Based Eligibility | Hard/soft filters (`app/eligibility.py`) |
| 4 | Semantic Retrieval | Sentence-transformer embeddings with TF-IDF fallback (`app/retrieval.py`) |
| 5 | Multi-Signal Ranking | Weighted signal blend (`app/ranking.py`) |
| 6 | Future Potential Engine | Recency/learning-velocity heuristics (`app/future_potential.py`) |
| 7 | Explainability | Template-based with optional Gemini narrative output (`app/explainability.py`) |
| 8 | Confidence Score | Data completeness check (`app/confidence.py`) |

`app/pipeline.py` wires all 8 together in the order from the architecture diagram in your doc.

## Run it (2 options)

### Option A — Streamlit demo (fastest, recommended first)
```bash
pip install -r requirements.txt
streamlit run frontend/streamlit_app.py
```
Opens a browser UI: paste/edit a JD, click "Run", see the ranked shortlist with explanations.

### Option B — FastAPI backend (for when Person 1's frontend needs an API)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then:
- `GET /candidates` — see the sample candidate pool
- `POST /rank_text` with `{"jd_text": "..."}` — get ranked results as JSON
- `POST /rank` — same, but as a multipart file upload
- Interactive docs at `http://localhost:8000/docs`

## Sample data
- `data/sample_resumes.json` — 5 synthetic candidates (intentionally includes one strong match,
  one stale senior, one fast-learning junior, one AI specialist, one irrelevant frontend dev —
  good for demoing that ranking isn't just keyword count)
- `data/sample_jd.txt` — matching JD to test against

Swap these for your real dataset once Person 2 has one ready — same JSON shape.

## Update: real embeddings (done, with fallback)

`retrieval.py` now tries `sentence-transformers` (`all-MiniLM-L6-v2`) first. On your first run
with internet access it downloads the model (~90MB, one-time, then cached locally). If the
download fails for any reason (offline, firewall), it automatically falls back to TF-IDF for
that session instead of crashing — you'll see a `[retrieval] sentence-transformers unavailable...`
message in the console if that happens. Once the model is cached, everything runs offline again.

Dataset also expanded from 5 to 18 candidates (`scripts/generate_dataset.py`) with deliberate
edge cases: a not-work-authorized strong match, a wrong-language-stack senior, an overqualified
principal engineer, a zero-experience-but-high-velocity fresher, a stale 8-year senior, and a
near-perfect match with the "nice to have" LLM/RAG skills — good for sanity-checking that ranking
and eligibility behave sensibly, not just that the pipeline runs.

## Remaining upgrade paths

1. **Vector DB (FAISS/Chroma)**: only worth adding once your real candidate pool is large
   (50+); at current scale brute-force cosine similarity is already instant.
2. **Prompt quality and guardrails**: tighten the Gemini prompts, add stronger JSON validation,
   and tune the fallback thresholds if you want more consistent demo output.
3. **Ranking calibration**: the weights in `ranking.py` are still hand-picked, so the next
   meaningful improvement is testing and tuning them against a larger dataset.

## Optional Gemini setup

Set `GEMINI_API_KEY` in your environment to enable Gemini for:

- `app/jd_intelligence.py` — JD extraction into structured JSON
- `app/explainability.py` — recruiter-facing ranking explanations

If Gemini is unavailable or returns an error, both modules fall back to the current rule-based
paths automatically, so the prototype still runs offline.

## Known rough edges (expected for a v0 prototype)
- Skill vocabulary in `jd_intelligence.py` is a small hardcoded list — fine for demo, needs a
  real taxonomy or LLM extraction for production.
- Domain matching is exact-string-match only.
- Weights in `ranking.py` (`WEIGHTS` dict) are hand-picked, not learned — Feature 15's
  "Learning-to-Rank" future scope item would replace these with a trained model.

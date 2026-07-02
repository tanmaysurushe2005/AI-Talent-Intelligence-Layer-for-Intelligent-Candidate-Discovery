# AI Talent Intelligence Layer — Prototype

Working prototype of all 8 features from the project doc, built to run **fully offline** with
no API key required, so you have something demoable today. Upgrade paths to real
embeddings/LLMs are noted inline in the code (search for "Upgrade path").

## What's implemented

| # | Feature | How it's done here |
|---|---------|--------------------|
| 1 | JD Validation | Rule-based (`app/jd_validation.py`) |
| 2 | JD Intelligence | Regex/keyword extraction (`app/jd_intelligence.py`) |
| 3 | Rule-Based Eligibility | Hard/soft filters (`app/eligibility.py`) |
| 4 | Semantic Retrieval | TF-IDF + cosine similarity (`app/retrieval.py`) |
| 5 | Multi-Signal Ranking | Weighted signal blend (`app/ranking.py`) |
| 6 | Future Potential Engine | Recency/learning-velocity heuristics (`app/future_potential.py`) |
| 7 | Explainability | Template-based, signal-driven (`app/explainability.py`) |
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
2. **LLM-based JD Intelligence**: replace the regex extraction in `jd_intelligence.py` with a
   Gemini/OpenAI call that returns the same `StructuredJD` JSON shape. Gemini has a free tier
   (Google AI Studio) — good fit for the "low-cost AI architecture" principle in your doc, since
   you'd only call the LLM here and in explainability, exactly as planned.
3. **LLM-based Explainability**: replace the templates in `explainability.py` with a prompt that
   takes the same `ranking_result` / `potential_result` signals and asks for a 2-3 sentence
   natural-language explanation. Keep the output dict shape (`why_selected`, `strengths`,
   `missing_skills`) so the frontend doesn't need changes.

## Known rough edges (expected for a v0 prototype)
- Skill vocabulary in `jd_intelligence.py` is a small hardcoded list — fine for demo, needs a
  real taxonomy or LLM extraction for production.
- Domain matching is exact-string-match only.
- Weights in `ranking.py` (`WEIGHTS` dict) are hand-picked, not learned — Feature 15's
  "Learning-to-Rank" future scope item would replace these with a trained model.

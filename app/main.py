import json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .pipeline import run_pipeline

app = FastAPI(title="AI Talent Intelligence Layer - Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_candidates():
    with open(DATA_DIR / "sample_resumes.json") as f:
        return json.load(f)


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Talent Intelligence Layer prototype API"}


@app.get("/candidates")
def get_candidates():
    return load_candidates()


@app.post("/rank")
async def rank_candidates(jd_file: UploadFile = File(...), top_k: int = 10):
    jd_text = (await jd_file.read()).decode("utf-8", errors="ignore")
    candidates = load_candidates()
    result = run_pipeline(jd_text, candidates, top_k=top_k)
    return result


@app.post("/rank_text")
async def rank_candidates_text(payload: dict):
    """Convenience endpoint: pass {"jd_text": "..."} as JSON instead of a file upload."""
    jd_text = payload.get("jd_text", "")
    candidates = load_candidates()
    result = run_pipeline(jd_text, candidates, top_k=payload.get("top_k", 10))
    return result

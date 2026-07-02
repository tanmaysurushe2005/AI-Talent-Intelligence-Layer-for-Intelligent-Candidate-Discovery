"""Semantic talent retrieval.

Tries real sentence embeddings first (sentence-transformers, all-MiniLM-L6-v2).
On first run this downloads the model from Hugging Face -- if that's not
reachable (offline, blocked network, no model cached yet) it falls back to
TF-IDF automatically so the app never hard-fails. Once the model download
succeeds once, it's cached locally and subsequent runs are fast and fully
offline.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_model = None
_sbert_available = True  # flips to False permanently in this process if loading fails


def _candidate_text(candidate: dict) -> str:
    parts = [
        candidate.get("summary", ""),
        " ".join(candidate.get("skills", [])),
        " ".join(candidate.get("projects", [])),
        candidate.get("domain", ""),
    ]
    return " ".join(parts)


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _tfidf_retrieve(jd_text: str, candidates: list, top_k: int):
    docs = [jd_text] + [_candidate_text(c) for c in candidates]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs)
    sims = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
    scored = list(zip(candidates, sims))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def _sbert_retrieve(jd_text: str, candidates: list, top_k: int):
    model = _get_model()
    docs = [_candidate_text(c) for c in candidates]
    jd_vec = model.encode([jd_text])
    cand_vecs = model.encode(docs)
    sims = cosine_similarity(jd_vec, cand_vecs)[0]
    scored = list(zip(candidates, sims))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def semantic_retrieve(jd_text: str, candidates: list, top_k: int = 10):
    global _sbert_available
    if _sbert_available:
        try:
            return _sbert_retrieve(jd_text, candidates, top_k)
        except Exception as e:
            print(f"[retrieval] sentence-transformers unavailable ({e}); "
                  f"falling back to TF-IDF for this session.")
            _sbert_available = False
    return _tfidf_retrieve(jd_text, candidates, top_k)

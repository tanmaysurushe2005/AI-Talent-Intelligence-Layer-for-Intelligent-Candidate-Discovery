import json
import csv
import io
import os
import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.pipeline import run_pipeline

st.set_page_config(page_title="AI Talent Intelligence Layer", layout="wide")
st.title("AI Talent Intelligence Layer — Prototype")
st.caption("Rules → TF-IDF retrieval → multi-signal ranking → future potential → explainability. No LLM required to run this demo.")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "sample_resumes.json") as f:
    candidates = json.load(f)

default_jd = (DATA_DIR / "sample_jd.txt").read_text()


def _build_csv_download(rows: list) -> str:
    buffer = io.StringIO()
    fieldnames = [
        "candidate_id",
        "name",
        "match_score",
        "future_potential_score",
        "confidence_score",
        "final_score",
        "eligibility_status",
        "why_selected",
        "strengths",
        "missing_skills",
        "eligibility_notes",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        explanation = row.get("explanation", {}) or {}
        writer.writerow(
            {
                "candidate_id": row.get("candidate_id", ""),
                "name": row.get("name", ""),
                "match_score": row.get("match_score", ""),
                "future_potential_score": row.get("future_potential_score", ""),
                "confidence_score": row.get("confidence_score", ""),
                "final_score": row.get("final_score", ""),
                "eligibility_status": row.get("eligibility_status", ""),
                "why_selected": explanation.get("why_selected", ""),
                "strengths": " | ".join(explanation.get("strengths", []) or []),
                "missing_skills": " | ".join(explanation.get("missing_skills", []) or []),
                "eligibility_notes": " | ".join(explanation.get("eligibility_notes", []) or []),
            }
        )
    return buffer.getvalue()


def _render_score_breakdown(signals: dict):
    breakdown_rows = [
        ("Skill match", signals.get("skill_match", 0.0)),
        ("Experience fit", signals.get("experience_match", 0.0)),
        ("Semantic relevance", signals.get("semantic_relevance", 0.0)),
        ("Domain match", signals.get("domain_match", 0.0)),
        ("Certification match", signals.get("certification_match", 0.0)),
        ("Skill freshness", signals.get("skill_freshness", 0.0)),
        ("Learning velocity", signals.get("learning_velocity", 0.0)),
        ("Career progression", signals.get("career_progression", 0.0)),
        ("Recency", signals.get("recency", 0.0)),
        ("Hackathon activity", signals.get("hackathon_activity", 0.0)),
    ]

    left, right = st.columns(2)
    for index, (label, value) in enumerate(breakdown_rows):
        column = left if index < 5 else right
        column.write(f"{label}: {value:.2f}")
        column.progress(min(max(value, 0.0), 1.0))

col1, col2 = st.columns([1, 1])
with col1:
    jd_text = st.text_area("Paste / edit Job Description", value=default_jd, height=350)
    top_k = st.slider("Number of candidates to shortlist", 1, len(candidates), 5)
    run = st.button("Run Talent Intelligence Pipeline", type="primary")

with col2:
    st.subheader(f"Candidate Pool ({len(candidates)})")
    st.dataframe(
        [{"name": c["name"], "skills": ", ".join(c["skills"]), "exp": c["experience_years"]} for c in candidates],
        use_container_width=True,
        hide_index=True,
    )

if run:
    result = run_pipeline(jd_text, candidates, top_k=top_k)

    st.divider()
    validation = result["validation"]
    if not validation["is_valid"]:
        st.error(f"JD failed validation (quality score: {validation['quality_score']}/100)")
        for issue in validation["issues"]:
            st.write(f"- {issue}")
        for s in validation["suggestions"]:
            st.info(s)
    else:
        st.success(f"JD Quality Score: {validation['quality_score']}/100")

        structured_jd = result["structured_jd"]
        with st.expander("Structured JD (extracted)", expanded=True):
            if os.getenv("GEMINI_API_KEY"):
                st.caption("Gemini-backed extraction enabled for this run.")
            else:
                st.caption("Offline rule-based extraction used for this run.")
            jd_summary = st.columns(3)
            jd_summary[0].metric("Role", structured_jd.get("role", ""))
            jd_summary[1].metric("Min experience", f"{structured_jd.get('min_experience_years', 0)} years")
            jd_summary[2].metric("Seniority", structured_jd.get("seniority") or "Mid-level")

            details_left, details_right = st.columns(2)
            details_left.write(f"**Required skills:** {', '.join(structured_jd.get('required_skills', []) or ['None'])}")
            details_left.write(f"**Nice to have:** {', '.join(structured_jd.get('nice_to_have_skills', []) or ['None'])}")
            details_right.write(f"**Education:** {structured_jd.get('education') or 'Not specified'}")
            details_right.write(f"**Location:** {structured_jd.get('location') or 'Not specified'}")
            details_right.write(f"**Domain:** {structured_jd.get('domain') or 'Not specified'}")

            st.json(structured_jd)

        if result["results"]:
            export_col1, export_col2 = st.columns(2)
            export_payload = json.dumps(result, indent=2)
            export_csv = _build_csv_download(result["results"])
            export_col1.download_button(
                "Download ranked results (JSON)",
                data=export_payload,
                file_name="ranked_results.json",
                mime="application/json",
            )
            export_col2.download_button(
                "Download ranked results (CSV)",
                data=export_csv,
                file_name="ranked_results.csv",
                mime="text/csv",
            )

        st.subheader("Ranked Candidates")
        for rank, r in enumerate(result["results"], start=1):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.markdown(f"**#{rank} {r['name']}**  \n`{r['eligibility_status']}`")
                c2.metric("Match", f"{r['match_score']}")
                c3.metric("Future Potential", f"{r['future_potential_score']}")
                c4.metric("Confidence", f"{r['confidence_score']}%")

                exp = r["explanation"]
                st.write(f"**Why:** {exp['why_selected']}")
                if exp["strengths"]:
                    st.write("**Strengths:** " + "; ".join(exp["strengths"]))
                if exp["missing_skills"]:
                    st.write("**Missing skills:** " + ", ".join(exp["missing_skills"]))
                if exp["eligibility_notes"]:
                    st.caption("Eligibility notes: " + "; ".join(exp["eligibility_notes"]))

                with st.expander("Score breakdown"):
                    _render_score_breakdown(r["signals"])

        if not result["results"]:
            st.warning("No eligible candidates found in the pool for this JD.")

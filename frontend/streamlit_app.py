import json
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

        with st.expander("Structured JD (extracted)"):
            st.json(result["structured_jd"])

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

        if not result["results"]:
            st.warning("No eligible candidates found in the pool for this JD.")

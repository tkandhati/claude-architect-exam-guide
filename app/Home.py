import streamlit as st
from datetime import datetime
from utils.storage import get_overall_readiness, get_last_activity, get_category_summary
from utils.claude_client import is_api_configured
from utils.prompts import EXAM_CATEGORIES

st.set_page_config(
    page_title="Claude Architect Exam Prep",
    page_icon="🏛️",
    layout="wide",
)

# Sidebar API status
with st.sidebar:
    if is_api_configured():
        st.success("🔑 API Connected")
    else:
        st.warning("⚠️ API Key Missing")
    st.caption("Add key to `.streamlit/secrets.toml`")

st.title("🏛️ Claude Certified Architect – Foundations")
st.subheader("Exam Preparation App")
st.markdown(
    "An interactive study companion for the **Claude Certified Architect – Foundations** certification. "
    "Practice with AI-generated questions, get gotcha explanations, and track your progress."
)

st.divider()

# Overall readiness
readiness = get_overall_readiness()
last_activity = get_last_activity()
summary = get_category_summary()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Overall Readiness", f"{readiness:.1f}%", help="Average score across all attempts")
with col2:
    total_attempts = sum(v["attempts"] for v in summary.values()) if summary else 0
    st.metric("Total Attempts", total_attempts)
with col3:
    if last_activity:
        dt = datetime.fromisoformat(last_activity)
        st.metric("Last Activity", dt.strftime("%b %d, %Y"))
    else:
        st.metric("Last Activity", "No activity yet")

if readiness > 0:
    color = "green" if readiness >= 75 else "orange" if readiness >= 50 else "red"
    st.markdown(f"**Readiness status:** :{color}[{'Ready ✓' if readiness >= 75 else 'Getting there…' if readiness >= 50 else 'Needs work'}]")

st.divider()

# Navigation cards
st.subheader("Navigate to")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("### 🎯 Gotcha Topics")
    st.markdown("Explore tricky concepts per category. Ask Claude to explain any topic in depth.")
    st.page_link("pages/1_Gotcha_Topics.py", label="Open Gotcha Topics →")

with c2:
    st.markdown("### ⚡ Quick Test")
    st.markdown("Generate a fresh quiz for any category. 5, 10, or 15 questions.")
    st.page_link("pages/2_Quick_Test.py", label="Open Quick Test →")

with c3:
    st.markdown("### 🏆 Full Simulation")
    st.markdown("60-question timed exam across all 5 official domains. 120 min. Pass mark: 75% (≈ 720/1000).")
    st.page_link("pages/3_Full_Simulation.py", label="Open Simulation →")

with c4:
    st.markdown("### 📊 Progress & Insights")
    st.markdown("Charts, heatmaps, and a personalized 7-day study plan.")
    st.page_link("pages/4_Progress_Insights.py", label="Open Insights →")

st.divider()

# Category readiness breakdown
if summary:
    st.subheader("Category Readiness")
    cols = st.columns(len(EXAM_CATEGORIES))
    for i, cat in enumerate(EXAM_CATEGORIES):
        with cols[i]:
            if cat in summary:
                pct = summary[cat]["avg_pct"]
                color = "🟢" if pct >= 75 else "🟡" if pct >= 50 else "🔴"
                st.metric(color + " " + cat.split("&")[0].strip(), f"{pct:.0f}%")
            else:
                st.metric("⚪ " + cat.split("&")[0].strip(), "—")
else:
    st.info("Take your first quiz to see category readiness here.")

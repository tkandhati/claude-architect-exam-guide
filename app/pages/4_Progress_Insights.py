import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
from utils.storage import load_results, get_category_summary
from utils.prompts import EXAM_CATEGORIES, STUDY_PLAN_PROMPT, SYSTEM_PROMPT_STUDY_PLAN
from utils.claude_client import get_claude_response, is_api_configured

st.set_page_config(page_title="Progress & Insights", page_icon="📊", layout="wide")

with st.sidebar:
    if is_api_configured():
        st.success("🔑 API Connected")
    else:
        st.warning("⚠️ API Key Missing")

st.title("📊 Progress & Insights")

results = load_results()
summary = get_category_summary()

if not results:
    st.info("No quiz results yet. Take a Quick Test or Full Simulation to see your progress here.")
    st.stop()

# Overall metrics
overall_pct = sum(r["pct"] for r in results) / len(results)
total_attempts = len(results)
categories_covered = len(summary)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Overall Avg Score", f"{overall_pct:.1f}%")
with col2:
    st.metric("Total Attempts", total_attempts)
with col3:
    st.metric("Categories Practiced", f"{categories_covered}/7")

st.divider()

# Score trend over time per category
st.subheader("Score Trend Over Time")

# Build dataframe from results
df_rows = []
for r in results:
    df_rows.append({
        "timestamp": r.get("timestamp", ""),
        "category": r.get("category", "Unknown"),
        "pct": r.get("pct", 0),
        "mode": r.get("mode", "quick"),
    })
df = pd.DataFrame(df_rows)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

if not df.empty:
    # Filter out "Full Simulation" for per-category chart
    df_filtered = df[df["category"] != "Full Simulation"]
    if not df_filtered.empty:
        fig = px.line(
            df_filtered,
            x="timestamp",
            y="pct",
            color="category",
            markers=True,
            title="Score % by Category Over Time",
            labels={"pct": "Score %", "timestamp": "Date", "category": "Category"},
        )
        fig.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Pass mark (75%)")
        fig.update_layout(yaxis_range=[0, 105])
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Heatmap: category vs attempt number
st.subheader("Attempt Heatmap by Category")

heatmap_data = {}
for cat in EXAM_CATEGORIES:
    cat_results = [r for r in results if r.get("category") == cat]
    heatmap_data[cat] = {f"Attempt {i+1}": r.get("pct", 0) for i, r in enumerate(cat_results)}

if heatmap_data:
    heatmap_df = pd.DataFrame(heatmap_data).T.fillna(None)
    if not heatmap_df.empty and not heatmap_df.columns.empty:
        fig_heat = px.imshow(
            heatmap_df.astype(float),
            labels={"x": "Attempt", "y": "Category", "color": "Score %"},
            color_continuous_scale=[[0, "red"], [0.5, "orange"], [0.75, "yellowgreen"], [1, "green"]],
            zmin=0,
            zmax=100,
            aspect="auto",
            title="Score Heatmap (by Category and Attempt)",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# Weakest categories
st.subheader("Category Performance")

cat_display = []
for cat in EXAM_CATEGORIES:
    if cat in summary:
        cat_display.append({
            "Category": cat,
            "Avg Score": f"{summary[cat]['avg_pct']:.1f}%",
            "Attempts": summary[cat]["attempts"],
            "Last Score": f"{summary[cat]['last_pct']:.1f}%",
        })
    else:
        cat_display.append({
            "Category": cat,
            "Avg Score": "—",
            "Attempts": 0,
            "Last Score": "—",
        })

cat_df = pd.DataFrame(cat_display)

# Identify weakest 2 categories
weak_cats = sorted(
    [cat for cat in EXAM_CATEGORIES if cat in summary],
    key=lambda c: summary[c]["avg_pct"]
)[:2]

def highlight_weak(row):
    if row["Category"] in weak_cats:
        return ["background-color: #ffcccc"] * len(row)
    return [""] * len(row)

st.dataframe(
    cat_df.style.apply(highlight_weak, axis=1),
    use_container_width=True,
    hide_index=True,
)

if weak_cats:
    st.markdown(f"🔴 **Weakest categories:** {', '.join(weak_cats)}")

st.divider()

# Study plan
st.subheader("AI-Powered Study Plan")
col_a, col_b = st.columns(2)

with col_a:
    if st.button("Generate 7-Day Study Plan", type="primary"):
        scores_data = {
            cat: {
                "avg_pct": summary[cat]["avg_pct"],
                "attempts": summary[cat]["attempts"],
            }
            if cat in summary
            else {"avg_pct": 0, "attempts": 0}
            for cat in EXAM_CATEGORIES
        }
        prompt = STUDY_PLAN_PROMPT.format(scores_json=json.dumps(scores_data, indent=2))

        st.markdown("**Your personalized 7-day study plan:**")
        plan_placeholder = st.empty()
        full_plan = ""

        with st.spinner("Claude is building your study plan..."):
            stream_ctx = get_claude_response(prompt, system_prompt=SYSTEM_PROMPT_STUDY_PLAN, stream=True)

        with stream_ctx as stream:
            for text in stream.text_stream:
                full_plan += text
                plan_placeholder.markdown(full_plan + "▌")
        plan_placeholder.markdown(full_plan)

with col_b:
    if weak_cats:
        if st.button(f"Practice Questions for Weakest Category", use_container_width=True):
            st.session_state["preselect_category"] = weak_cats[0]
            st.switch_page("pages/2_Quick_Test.py")
    else:
        st.info("Take more quizzes to unlock weak area practice.")

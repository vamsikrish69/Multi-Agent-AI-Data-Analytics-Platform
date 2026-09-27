import uuid

import streamlit as st

from ai_data_agent.agents.graph import build_graph
from ai_data_agent.agents.state import AgentState

st.set_page_config(page_title="AI Data Agent", page_icon="🚕")

st.title("🚕 AI Data Agent")
st.caption("Ask a question about the mobility dataset, or paste ETL code for review.")

if "graph_app" not in st.session_state:
    st.session_state.graph_app = build_graph()

question = st.text_area("Your question or code:", height=120, placeholder="e.g. How many rides were completed?")

col1, col2 = st.columns([1, 3])
with col1:
    submit = st.button("Submit", type="primary")

if submit and question.strip():
    with st.spinner("Thinking... this may take a little while on local models."):
        initial_state = AgentState(
            user_question=question,
            correlation_id=str(uuid.uuid4()),
        )
        result = st.session_state.graph_app.invoke(initial_state)

    st.markdown("### Answer")
    st.write(result["final_answer"])

    with st.expander("Details"):
        st.write(f"**Route:** {result['route']}")
        if result.get("validated_sql"):
            st.write("**SQL used:**")
            st.code(result["validated_sql"], language="sql")
        if result.get("query_result") is not None:
            st.write("**Raw result:**")
            st.write(result["query_result"])
        st.write(f"**Retry count:** {result['retry_count']}")
        if result.get("judge_feedback"):
            st.write(f"**Judge feedback:** {result['judge_feedback']}")

elif submit:
    st.warning("Please enter a question or some code first.")

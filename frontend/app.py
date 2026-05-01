import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Bug Predictor", layout="wide", page_icon="🛡️")


st.title("🛡️ AI GitHub Bug Predictor")
st.markdown("Analyze any Python repository using advanced Machine Learning (CodeBERT + PyTorch) to find potential bugs before they happen.")


if "repo_data" not in st.session_state:
    st.session_state.repo_data = None


st.markdown("### 🔍 Enter Repository")
repo_url = st.text_input("", placeholder="e.g., https://github.com/tiangolo/fastapi")

if st.button("🚀 Analyze Codebase", type="primary"):
    if repo_url:
        with st.spinner(f"Cloning {repo_url} and running PyTorch analysis..."):
            try:
                response = requests.post("http://127.0.0.1:8000/analyze", json={"url": repo_url})
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "error":
                        st.error(data["message"])
                    else:
                        # SAVE THE DATA TO MEMORY!
                        st.session_state.repo_data = data
                else:
                    st.error("Backend Error occurred.")
            except Exception as e:
                st.error("Could not connect to FastAPI. Is the backend server running?")

# --- 4. Display Results (Only if we have data in memory) ---
if st.session_state.repo_data:
    st.success("✅ Analysis Complete!")
    data = st.session_state.repo_data
    df = pd.DataFrame(data["predictions"]).sort_values(by="bug_probability", ascending=False)
    
    # --- Educational Guide Section ---
    st.markdown("---")
    st.markdown("### 📖 How to read this report")
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    with col_leg1:
        st.error("**🔴 Dark Red (High Risk):**\nThe AI is highly confident this file contains complex or risky patterns. Review this first.")
    with col_leg2:
        st.warning("**🟠 Orange (Medium Risk):**\nThe code is moderately complex. Worth a look, but likely safe.")
    with col_leg3:
        st.success("**⚪ White (Low Risk):**\nClean, standard code. The AI found no suspicious patterns.")
        
    st.markdown("> **Metrics Guide:** \n> **Bug Probability:** The AI's confidence score (0-100%) that a bug exists.  \n> **LOC (Lines of Code):** The physical size of the file. Larger files often hide more bugs.")
    st.markdown("---")
    
    # --- Data Visualization Section ---
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("#### 📄 Risk Ranking Table")
        st.dataframe(
            df.style.background_gradient(cmap='Reds', subset=['bug_probability'])
            .format({"bug_probability": "{:.2f}%", "loc": "{:.0f}"}),
            use_container_width=True,
            height=350
        )
        
        # --- AI Code Reviewer Section ---
        st.markdown("### 🤖 Ask LLM for a Fix")
        st.markdown("Select a high-risk file to send to the LangGraph AI Reviewer.")
        
        risky_files = df["file"].tolist()
        selected_file = st.selectbox("Select File:", risky_files)
        
        # Notice we use a unique key for this button so it doesn't conflict
        if st.button("Fix this file", type="secondary", key="llm_btn"):
            with st.spinner("LangGraph Agent is reviewing the code via Hugging Face...") :
                raw_code = data["raw_files"].get(selected_file, "")
                
                try:
                    llm_response = requests.post(
                        "http://127.0.0.1:8000/review", 
                        json={"file_name": selected_file, "code_snippet": raw_code}
                    )
                    
                    if llm_response.status_code == 200:
                        result_data = llm_response.json()
                        st.info("💡 **LLM Fix & Explanation:**")
                        st.code(result_data["analysis"], language="python")
                    else:
                        st.error(f"LLM Review failed. Status Code: {llm_response.status_code}")
                except Exception as e:
                    st.error("Failed to connect to the backend for the LLM review.")
                
    with col2:
        st.markdown("#### 📊 Repository Risk Heatmap")
        fig = px.bar(
            df.head(20), 
            x="bug_probability", 
            y="file", 
            color="bug_probability", 
            color_continuous_scale="Reds", 
            orientation='h',
            labels={'bug_probability': 'AI Risk Score (%)', 'file': 'File Name'}
        )
        fig.update_layout(
            yaxis={'categoryorder':'total ascending'}, 
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
import os
import streamlit as st
import requests

# FastAPI Backend URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/tutor")

st.set_page_config(page_title="Shona HBC Assistant", page_icon="📚", layout="centered")

st.title("📚 Shona SBP Assistant")
st.markdown("Mubatsiri wezvemapurojekiti eHeritage-Based Curriculum (HBC).")

# Sidebar Configuration
with st.sidebar:
    st.header("Zvirongwa Zvemudzidzi (Settings)")
    student_level = st.selectbox(
        "Nhanho Yechikoro (Level):",
        ["Primary (Giredhi 6-7)", "ZJC-O-Level (Form 1-4)", "A-Level (Form 5-6)"]
    )
    
    project_stage = st.slider(
        "SBP Stage (1-6):",
        min_value=1,
        max_value=6,
        value=1,
        help="1: Dambudziko, 2: Tsvakiridzo, 3: Mazano, 4: Gadziriro, 5: Mharidzo, 6: Ongororo"
    )
    
    st.markdown("---")
    if st.button("Dzima Hurukuro (Clear Chat)"):
        st.session_state.messages = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Bvunza mubvunzo wako we project pano..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare payload for FastAPI
    payload = {
        "query": prompt,
        "student_level": student_level,
        "project_stage": int(project_stage)
    }

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Tichitsvaga mhinduro..."):
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    bot_reply = data.get("response", "Hapana mhinduro yawonekwa.")
                    st.markdown(bot_reply)
                    
                    if data.get("retrieved_context_used"):
                        st.caption("*(Mhinduro iyi inobva mumagwaro eHBC projects)*")
                        
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                else:
                    st.error(f"Kukanganisa kweServer: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Hatina kukwanisa kubata server. Iva nechokwadi kuti FastAPI iri kushanda.")
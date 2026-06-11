import streamlit as st
from agent import generate_triage_response

st.set_page_config(
    page_title="HELP AI Platform",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 HELP: Humanitarian Emergency Liaison Platform")
st.subheader("Elite Autonomous AI Emergency Triage & Dispatch Console")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Incident Ingest Portal")

    user_input = st.text_area(
        "Describe the emergency crisis context in detail (Include specific locations for live routing):",
        height=150,
        placeholder="Example: I found an injured stray dog on the road in Andheri West, Mumbai. It is bleeding from its hind leg..."
    )

    st.markdown("### 🎙️ Multimodal Inputs")
    uploaded_image = st.file_uploader("Upload Crisis Scene Documentation (Images)", type=["jpg", "jpeg", "png"])
    uploaded_audio = st.file_uploader("Upload Audio Reports / Ambient Sound Captures", type=["wav", "mp3"])

    submit_btn = st.button("🚨 INITIATE EMERGENCY TRIAGE", use_container_width=True)

with col2:
    st.header("📡 Live Triage & Routing Matrix")

    if submit_btn:
        if not user_input.strip():
            st.error("System Warning: Input context cannot be empty during a crisis declaration.")
        else:
            with st.spinner("Processing crisis stream... Grounding live dispatch data..."):
                triage_matrix = generate_triage_response(user_input)
                st.markdown("### Operational Instructions")
                st.markdown(triage_matrix)
    else:
        st.info("System Status: Standby. Awaiting incident payload ingest from portal.")
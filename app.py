import streamlit as st
from agent import process_triage_request

# Page Configuration for a wider, modern look
st.set_page_config(page_title="HELP AI Network", page_icon="🚨", layout="wide")

st.title("🚨 HELP: Autonomous Emergency AI Agent")
st.markdown("**Omni-Modal Telemetry Interface**: Submit text, photos, or live audio to trigger the AI triage protocol.")

# --- UI LAYOUT: 3 COLUMNS FOR INPUTS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📝 1. Text Context")
    user_text = st.text_area("Describe the situation & location:", height=150,
                             placeholder="e.g., Found a stray dog injured on SV Road, Bandra...")

with col2:
    st.subheader("📸 2. Visual Telemetry")
    uploaded_image = st.file_uploader("Upload an image of the emergency", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Visual Locked", use_container_width=True)

with col3:
    st.subheader("🎙️ 3. Live Audio Dispatch")
    # THE MAGIC WIDGET: Native Streamlit microphone recorder!
    recorded_audio = st.audio_input("Record a live situation report")
    if recorded_audio:
        st.success("Audio captured successfully.")

# --- ACTION BUTTON ---
st.divider()
submit_button = st.button("🔴 INITIATE AI TRIAGE SEQUENCE", use_container_width=True, type="primary")

if submit_button:
    # Ensure at least one input exists before hitting the API
    if not user_text and not uploaded_image and not recorded_audio:
        st.error("⚠️ Please provide at least one form of input (Text, Image, or Audio) before initiating.")
    else:
        with st.spinner("🧠 HELP Core is analyzing multimodal telemetry and pinging local networks..."):

            # Extract bytes from the UI elements if they exist
            img_bytes = uploaded_image.getvalue() if uploaded_image else None
            audio_bytes = recorded_audio.getvalue() if recorded_audio else None

            # Call our refactored backend!
            result = process_triage_request(
                text_prompt=user_text,
                image_bytes=img_bytes,
                audio_bytes=audio_bytes
            )

            # --- RENDER RESULTS ---
            if result.get("success"):
                st.success("✅ Triage Matrix Generated")

                # Show exactly what the AI searched on Google
                if result.get("queries"):
                    with st.expander("🌐 View Live Web Grounding Queries"):
                        for q in result["queries"]:
                            st.markdown(f"- `{q}`")

                # Display the 5-Stage Output
                st.markdown("### 📋 Official Action Protocol")
                st.markdown(result["report"])
            else:
                st.error(f"❌ Core Error: {result.get('error')}")
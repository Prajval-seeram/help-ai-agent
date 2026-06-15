import streamlit as st
import os
from legacy.ui import render_header
from legacy.location import get_auto_location
from legacy.agent import run_triage_pipeline

render_header()

# Ensure uploads directory exists for the temporary buffer
if not os.path.exists("uploads"):
    os.makedirs("uploads")

st.info("Ensure you are in a safe location before initiating triage.", icon="ℹ️")

# Fetch location silently and display to user
user_location = get_auto_location()
st.success(f"📍 Auto-Detected Incident Location: {user_location}")

# Input fields
user_prompt = st.text_area("Describe the emergency situation (Text/Audio context):",
                           height=130,
                           placeholder="E.g., I just found a stray dog on the side of the road...")

col1, col2 = st.columns(2)
with col1:
    uploaded_image = st.file_uploader("Upload Image Evidence", type=["png", "jpg", "jpeg"])
with col2:
    uploaded_audio = st.file_uploader("Upload Audio Evidence", type=["mp3", "wav", "m4a"])

if st.button("🔴 INITIATE AI TRIAGE", use_container_width=True):
    if not user_prompt and not uploaded_image and not uploaded_audio:
        st.warning("Please provide text, image, or audio context to initiate triage.")
    else:
        with st.spinner("=== HELP AI Platform: Processing Multimodal Data ==="):
            img_path = None
            audio_path = None

            # Write files to local buffer so the Google Files API can read them safely
            if uploaded_image:
                img_path = os.path.join("uploads", uploaded_image.name)
                with open(img_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())

            if uploaded_audio:
                audio_path = os.path.join("uploads", uploaded_audio.name)
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())

            # Execute AI Pipeline
            triage_output = run_triage_pipeline(
                user_prompt=user_prompt,
                location_data=user_location,
                image_path=img_path,
                audio_path=audio_path
            )

            # Clean up local buffers immediately
            if img_path and os.path.exists(img_path):
                os.remove(img_path)
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

            st.markdown("### === SYSTEM TRIAGE REASONING MATRIX ===")
            st.markdown(triage_output)
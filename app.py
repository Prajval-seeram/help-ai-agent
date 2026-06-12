import streamlit as st
from agent import process_triage_request, _normalize_bytes, _guess_mime

st.set_page_config(page_title="HELP AI Network", page_icon="🚨", layout="wide")

st.title("🚨 HELP: Emergency Triage Assistant")
st.markdown(
    "Upload text, image, or audio. If the image is too graphic and the model refuses it, add a short manual description and keep going."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📝 Text Context")
    user_text = st.text_area(
        "Describe the situation and location:",
        height=160,
        placeholder="Example: I found a dog lying near the road with blood on its leg.",
    )

with col2:
    st.subheader("📸 Image")
    uploaded_image = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp"],
    )
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded image", use_container_width=True)

with col3:
    st.subheader("🎙️ Audio")
    recorded_audio = st.audio_input("Record a short audio note")
    if recorded_audio is not None:
        st.success("Audio captured.")

st.markdown("### Optional fallback for graphic or blocked images")
manual_image_notes = st.text_area(
    "If the image is too graphic or the image step fails, type a short plain description here:",
    height=100,
    placeholder="Example: brown dog, visible wound on head, lying still, near roadside",
)

st.divider()

submit = st.button("🔴 RUN TRIAGE", use_container_width=True, type="primary")

if submit:
    if not user_text and not uploaded_image and not recorded_audio and not manual_image_notes.strip():
        st.error("Please provide at least one input.")
    else:
        with st.spinner("Analyzing..."):
            image_bytes = None
            image_mime = None
            audio_bytes = None
            audio_mime = None

            if uploaded_image is not None:
                image_bytes = _normalize_bytes(uploaded_image)
                image_mime = uploaded_image.type or _guess_mime(uploaded_image.name, "image/jpeg")

            if recorded_audio is not None:
                audio_bytes = _normalize_bytes(recorded_audio)
                audio_mime = getattr(recorded_audio, "type", None) or _guess_mime(
                    getattr(recorded_audio, "name", None),
                    "audio/wav",
                )

            result = process_triage_request(
                text_input=user_text,
                image_bytes=image_bytes,
                image_mime_type=image_mime,
                audio_bytes=audio_bytes,
                audio_mime_type=audio_mime,
                manual_image_notes=manual_image_notes,
            )

            if result.get("success"):
                st.success("Triage complete.")

                left, right = st.columns(2)

                with left:
                    st.subheader("Image Observation")
                    st.json(result.get("image_observation", {}))

                with right:
                    st.subheader("Report")
                    st.markdown(result.get("report", "No report text returned."))
            else:
                st.error(result.get("error", "Unknown error"))
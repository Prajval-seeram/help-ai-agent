import streamlit as st
from agent import process_triage_request, _normalize_bytes, _guess_mime

st.set_page_config(page_title="HELP AI Network", page_icon="🚨", layout="wide")

st.title("🚨 HELP: Autonomous Emergency AI Agent")
st.markdown(
    "**Omni-Modal Telemetry Interface**: Submit text, photos, or live audio to trigger the AI triage protocol."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📝 1. Text Context")
    user_text = st.text_area(
        "Describe the situation & location:",
        height=150,
        placeholder="e.g., Found a stray dog injured on SV Road, Bandra...",
    )

with col2:
    st.subheader("📸 2. Visual Telemetry")
    uploaded_image = st.file_uploader(
        "Upload an image of the emergency",
        type=["jpg", "jpeg", "png", "webp"],
    )
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Visual Locked", use_container_width=True)

with col3:
    st.subheader("🎙️ 3. Live Audio Dispatch")
    recorded_audio = st.audio_input("Record a live situation report")
    if recorded_audio is not None:
        st.success("Audio captured successfully.")

st.divider()

submit_button = st.button(
    "🔴 INITIATE AI TRIAGE SEQUENCE",
    use_container_width=True,
    type="primary",
)

if submit_button:
    if not user_text and not uploaded_image and not recorded_audio:
        st.error("⚠️ Provide at least one input: text, image, or audio.")
    else:
        with st.spinner("🧠 HELP Core is analyzing multimodal telemetry..."):
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
            )

            if result.get("success"):
                st.success("✅ Triage Matrix Generated")

                if result.get("queries"):
                    with st.expander("🌐 View Live Web Grounding Queries"):
                        for q in result["queries"]:
                            st.markdown(f"- `{q}`")

                st.markdown("### 📋 Official Action Protocol")
                st.markdown(result["report"])
            else:
                st.error(f"❌ Core Error: {result.get('error')}")
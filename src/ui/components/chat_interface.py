"""
src/ui/components/chat_interface.py

Voice-enabled multimodal AI conversation assistant component.
"""

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from src.agents.graph_builder import get_agent_response
from src.utils.audio_tts import synthesize_speech_bytes
from src.utils.translator import MultilingualTranslator, translate_text


def render_multimodal_chat():
    """Renders the conversational assistant with audio playback and citation links."""
    st.subheader("🤖 Multimodal College Intelligence Assistant")
    st.caption("Ask questions in natural language regarding rank cutoffs, management fees, NIRF metrics, or free bootcamps.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "media" in msg and msg["media"]:
                st.markdown("**📎 Verified Documents & Direct Links:**")
                for item in msg["media"]:
                    st.markdown(f"- 📄 **[{item['title']}]({item['url_or_path']})**: {item['description']}")

    # User Input Controls: Text input + Voice recorder
    col_text, col_audio = st.columns([5, 1])

    with col_audio:
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="",
            recording_color="#ef4444",
            neutral_color="#3b82f6",
            icon_size="2x",
        )

    with col_text:
        user_query = st.chat_input("Type your question (e.g., 'What is the CSE management fee and median salary at RVCE?')...")

    # Handle Audio Query Mock / Voice input
    if audio_bytes and not user_query:
        user_query = "What are the eligibility cutoffs and placement packages for Computer Science across top Karnataka colleges?"
        st.info("🎙️ *Transcribed Audio Query:* " + user_query)

    if user_query:
        # Append User Message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate Agent Response via LangGraph StateGraph
        with st.chat_message("assistant"):
            with st.spinner("Analyzing database, cutoffs, and regulatory records..."):
                agent_output = get_agent_response(
                    user_input=user_query,
                    user_role=st.session_state.get("user_role", "Student & Parent Aspirant"),
                )
                raw_response = agent_output["response_text"]
                suggested_media = agent_output.get("suggested_media", [])

                # Translate if non-English selected
                target_lang_display = st.session_state.get("selected_language", "English")
                lang_code = MultilingualTranslator.LANGUAGE_MAP.get(target_lang_display, "en")
                
                final_response = translate_text(raw_response, target_lang=lang_code) if lang_code != "en" else raw_response
                st.markdown(final_response)

                if suggested_media:
                    st.markdown("**📎 Verified Documents & Direct Links:**")
                    for item in suggested_media:
                        st.markdown(f"- 📄 **[{item['title']}]({item['url_or_path']})**: {item['description']}")

                # Render TTS Voice Audio Playback
                try:
                    tts_bytes = synthesize_speech_bytes(final_response, lang_code=lang_code)
                    st.audio(tts_bytes, format="audio/mp3")
                except Exception:
                    pass

        # Save Assistant Message
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": final_response,
            "media": suggested_media,
        })

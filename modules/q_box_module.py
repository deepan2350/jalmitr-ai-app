import streamlit as st
import openai
import os
from gtts import gTTS
import base64
import tempfile
import speech_recognition as sr

openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")

def speak_text(text, lang="hi"):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio_bytes = open(fp.name, "rb").read()
        b64 = base64.b64encode(audio_bytes).decode()
        st.markdown(
            f'<audio controls autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True,
        )

def recognize_voice(lang="hi-IN"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now")
        try:
            audio = r.listen(source, timeout=5)
            text = r.recognize_google(audio, language=lang)
            st.success(f"🗣️ You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio")
        except sr.RequestError:
            st.error("⚠️ Voice recognition error")
    return ""

def ask_ai(question):
    if not openai.api_key:
        st.error("❌ OpenAI API key missing.")
        return ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"AI Error: {e}")
        return ""

def run():
    st.title("🤖 Q Box - JalMitr AI Chatbot")
    st.markdown("Paani se related sawal puchhiye — likh kar ya bol kar! AI aapko jawab dega voice + text me.")

    lang_choice = st.selectbox("🗣️ Choose Language", ["hi", "en"])
    input_mode = st.radio("🎛️ Select Input Mode", ["⌨️ Type", "🎤 Voice"])

    user_query = ""

    if input_mode == "⌨️ Type":
        user_query = st.text_input("Aapka sawaal:")
    else:
        if st.button("🎙️ Bolna shuru karo"):
            user_query = recognize_voice(lang="hi-IN" if lang_choice == "hi" else "en-IN")

    if user_query:
        with st.spinner("🤖 Soch raha hai..."):
            reply = ask_ai(user_query)
            st.success(reply)
            st.markdown("🔊 **Voice Output:**")
            speak_text(reply, lang=lang_choice)


import streamlit as st
import openai
import os
import time
from gtts import gTTS
import tempfile
import base64
import speech_recognition as sr

# Step 1: Chat history initialize
if "qbox_chat" not in st.session_state:
    st.session_state.qbox_chat = []

# Step 2: Title & Description
st.title("🤖 Q Box - JalMitr AI Chatbot")
st.markdown("Paani se related koi bhi sawal AI se poochhiye. Type ya bolo – dono chalega!")

# Step 3: OpenAI Key Setup (you can also set this in secrets if deploying)
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-xxxxxx"  # ⚠️ Replace with your key

# Step 4: User Input (Text)
user_input = st.text_input("✍️ Aapka sawaal yahan likhiye:")

# Step 5: Voice Input
def recognize_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Bolna shuru kijiye...")
        audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio, language="hi-IN")
        st.success(f"🔊 Aapne kaha: {text}")
        return text
    except sr.UnknownValueError:
        st.error("😕 Samajh nahi aaya. Phir se boliye.")
    except sr.RequestError:
        st.error("🌐 Network issue aayi hai.")
    return ""

if st.button("🎙️ Voice se poochho"):
    voice_q = recognize_voice()
    if voice_q:
        user_input = voice_q

# Step 6: Generate AI Response
def ask_gpt(q):
    if not q:
        return ""
    st.session_state.qbox_chat.append({"role": "user", "content": q})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=st.session_state.qbox_chat
        )
        reply = response.choices[0].message.content
        st.session_state.qbox_chat.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return ""

if user_input:
    response = ask_gpt(user_input)
    if response:
        st.markdown("🧠 **AI ka jawab:**")
        st.success(response)

        # Step 7: Voice Output
        tts = gTTS(text=response, lang="hi")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            audio_bytes = open(fp.name, "rb").read()
            b64 = base64.b64encode(audio_bytes).decode()
            st.markdown(
                f'<audio controls autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
                unsafe_allow_html=True,
            )


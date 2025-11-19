import streamlit as st
import requests
from datetime import datetime

# --- Page Setup ---
st.set_page_config(page_title="Nebras Medical Chatbot", layout="centered")

# --- Backend API URL ---
API_URL = "http://127.0.0.1:8000/chat"

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Predefined casual responses ---
def get_predefined_reply(user_input: str):
    text = user_input.lower().strip()
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    farewells = ["bye", "goodbye", "see you", "later"]
    thanks = ["thanks", "thank you", "thx"]
    smalltalk = ["how are you", "what's up", "how's it going"]

    if text in greetings:
        return "Hello! How can I help you with your medical question today?"
    elif text in farewells:
        return "Goodbye! Stay healthy."
    elif text in thanks:
        return "You're welcome! Feel free to ask more medical questions."
    elif text in smalltalk:
        return "I'm here to help with health-related questions!"
    return None

# --- CSS---
st.markdown("""
<style>
@keyframes gradientBG {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}
html, body, .main {
    background: linear-gradient(120deg,#061826,#092432,#0b3140,#07324a,#03151a);
    background-size: 400% 400%;
    animation: gradientBG 18s ease infinite;
    color: #e6eef6;
    font-family: 'Inter', sans-serif;
}
.chat-wrap {
    max-width: 820px;
    margin: 20px auto;
    padding: 20px;
    border-radius: 16px;
    background: rgba(255,255,255,0.03);
    box-shadow: 0 8px 30px rgba(2,6,23,0.6);
    border: 1px solid rgba(255,255,255,0.04);
}
.chat-container {
    height: 62vh;
    overflow-y: auto;
    padding: 18px;
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.03);
}
.msg-row { display:flex; gap:10px; margin-bottom:12px; }
.bubble-bot {
    padding:12px 14px;
    border-radius:16px 16px 16px 4px;
    background: linear-gradient(135deg,#115979,#2196F3);
    color:white;
    font-size:14px;
    line-height:1.35;
    box-shadow:0 6px 18px rgba(6,30,52,0.5);
}
.bubble-user {
    padding:12px 14px;
    border-radius:16px 16px 4px 16px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.04);
    color: #e6eef6;
    font-size:14px;
    line-height:1.35;
    box-shadow: 0 6px 16px rgba(2,6,23,0.45);
    margin-left:auto;
}
.avatar { width:40px; height:40px; border-radius:50%; }
.meta { font-size:11px; color: rgba(230,238,246,0.65); margin-top:6px; }
.floating-input {
    position: sticky;
    bottom: 8px;
    display:flex;
    justify-content:center;
    z-index:999;
}
.input-decor {
    width:100%;
    max-width:820px;
    background: rgba(2,6,23,0.45);
    border-radius:14px;
    padding:10px 12px;
    display:flex;
    gap:8px;
    align-items:center;
    border: 1px solid rgba(255,255,255,0.03);
    box-shadow: 0 12px 30px rgba(2,6,23,0.5);
    backdrop-filter: blur(6px);
}
.input-left {
    display:flex;
    align-items:center;
    gap:10px;
    padding-left:6px;
}
.send-hint {
    font-size:12px;
    color:#cfeeff;
    opacity:0.9;
}
@media (max-width: 640px) {
    .chat-wrap { margin: 8px; padding: 12px; border-radius: 12px; }
    .chat-container { height: 58vh; min-height: 280px; padding: 12px; }
    .bubble-bot, .bubble-user { font-size: 13px; padding:10px 12px; }
}
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown(
    """
    <div class="chat-wrap">
        <h1 class="title" style="margin-bottom:4px;">Nebras Medical Chatbot🧬</h1>
        <p class="subheader">
            Your AI medical assistant — short, factual answers. Always confirm critical info with a doctor.
        </p>
    """,
    unsafe_allow_html=True,
)

# Using a placeholder to render chat
chat_placeholder = st.empty()

# --- Chat rendering ---
def render_chat():
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-row">
                <div class="bubble-user">{msg['text']}<div class="meta">{msg['time']}</div></div>
                <img class="avatar" src="https://img.icons8.com/?size=100&id=ScJCfhkd77yD&format=png&color=000000">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row">
                <img class="avatar" src="https://img.icons8.com/?size=100&id=b2rw9AoJdaQb&format=png&color=000000">
                <div class="bubble-bot">{msg['text']}<div class="meta">{msg['time']}</div></div>
            </div>
            """, unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.header("🩺 About Nebras")
    st.write("Nebras Chatbot is an AI medical assistant built using a fine-tuned Transformer model for medical tasks. Provides short, factual information.")
    st.markdown("---")
    st.info("🚨 Always verify critical medical information with a certified doctor.")
    st.markdown("**Tips**")
    st.markdown("- Ask one medical question at a time.")
    st.markdown("- Avoid sharing personal identifying details.")

# --- Capture user input ---
user_input = st.chat_input("Type your medical question here...")
if user_input:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state["messages"].append({"role":"user","text":user_input,"time":now})

    bot_reply = get_predefined_reply(user_input)
    if bot_reply is None:
        st.session_state["messages"].append({"role":"bot","text":"Nebras is thinking…","time":""})
        try:
            response = requests.post(API_URL, json={"question":user_input}, timeout=150)
            bot_reply = response.json().get("response","No reply.")
        except:
            bot_reply = "Backend not reachable."
        st.session_state["messages"].pop()
        st.session_state["messages"].append({"role":"bot","text":bot_reply,"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
    else:
        st.session_state["messages"].append({"role":"bot","text":bot_reply,"time":now})
    render_chat()

# --- Footer ---
st.markdown("""
<div style="text-align:center;color:#9fbadf;font-size:12px;margin-top:6px;">
    Nebras Chatbot • © 2025
</div>
""", unsafe_allow_html=True)

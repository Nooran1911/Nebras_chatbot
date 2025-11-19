import streamlit as st
import requests

# --- Page Setup ---
st.set_page_config(page_title="Nebras Medical Chatbot", layout="centered")

# --- Backend API URL ---
API_URL = "http://127.0.0.1:8000/chat"  # Change if deployed

# --- First-time Model Loading Message ---
if "model_loaded" not in st.session_state:
    st.session_state["model_loaded"] = True

# --- Initialize Chat Session ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Predefined Casual Responses ---
def get_predefined_reply(user_input: str) -> str:
    text = user_input.lower().strip()
    
    greetings = ["hi", "hi nebras", "hello", "hey", "good morning", "good evening"]
    farewells = ["bye", "goodbye", "see you", "later"]
    thanks = ["thanks", "thank you", "thx"]
    smalltalk = ["how are you", "how's it going", "what's up"]

    if text in greetings:
        return "Hello! How can I help you with your medical question today?"
    elif text in farewells:
        return "Goodbye! Stay healthy."
    elif text in thanks:
        return "You're welcome! Feel free to ask more medical questions."
    elif text in smalltalk:
        return "I'm just a medical assistant, but I'm here to help with health questions!"
    
    return None  # return None if not a predefined response

# --- Custom Dark Theme & Scrollable Chatbox ---
st.markdown(
    """
    <style>
    body {background-color: #0e1117; color: #f5f5f5;}
    .main {background-color: #0e1117;}
    h1 {color: #4FC3F7; text-align:center; margin-bottom:5px;}
    .subheader {color:#9ca3af; text-align:center; margin-bottom:20px;}
    .chat-container {height:500px; overflow-y:auto; background-color:#1e1e1e; padding:15px; border-radius:10px; border:1px solid #333; margin-bottom:10px;}
    .chat-bubble {margin-bottom:10px; padding:10px 14px; border-radius:10px; max-width:90%; word-wrap:break-word;}
    .user-msg {background-color:#2b4c7e; color:white; text-align:right; margin-left:auto;}
    .bot-msg {background-color:#333333; color:#e5e5e5; text-align:left; margin-right:auto;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown("<h1>Nebras Medical Chatbot🧬</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Your AI-powered medical assistant, Ask any medical-related question below.</p>", unsafe_allow_html=True)

# --- Chat Rendering Function ---
chat_placeholder = st.empty()
def render_chat():
    chat_html = "<div class='chat-container' id='chatbox'>"
    for msg in st.session_state["messages"]:
        role_class = "user-msg" if msg["role"] == "user" else "bot-msg"
        chat_html += f"<div class='chat-bubble {role_class}'>{msg['text']}</div>"
    chat_html += """
    <script>
        var chatDiv = document.getElementById('chatbox');
        chatDiv.scrollTop = chatDiv.scrollHeight;
    </script>
    </div>
    """
    chat_placeholder.markdown(chat_html, unsafe_allow_html=True)

render_chat()

# === SIDEBAR INFO ===
with st.sidebar:
    st.header("🩺 About Nebras")
    st.write(
        "Nebras Chatbot is an AI medical assistant built using a fine-tuned Transformer model for medical and clinical domain tasks. "
        "It provides short, and factual medical informations."
    )
    st.markdown("---")
    st.info("🚨 Always verify critical medical information with a certified doctor.")

# --- User Input Box ---
user_input = st.chat_input("Type your medical question here...")

if user_input:
    st.session_state["messages"].append({"role": "user", "text": user_input})
    render_chat()

    # --- Check for Predefined Responses ---
    bot_reply = get_predefined_reply(user_input)

    if bot_reply is None:
        # Call backend API if no predefined response
        with st.spinner("Nebras is thinking..."):
            try:
                response = requests.post(API_URL, json={"question": user_input}, timeout=250)
                if response.status_code == 200:
                    bot_reply = response.json().get("response", "No reply from model.")
                else:
                    bot_reply = f"Error: {response.status_code}"
            except requests.exceptions.Timeout:
                bot_reply = "The model took too long to respond."
            except Exception as e:
                bot_reply = f"Could not reach backend: {e}"

    st.session_state["messages"].append({"role": "bot", "text": bot_reply})
    render_chat()

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#6B7280;'>• Nebras Chatbot🧬 © 2025</p>",
    unsafe_allow_html=True
)
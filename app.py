import streamlit as st
from datetime import datetime
from core.chat_handler import ChatHandler

try:
    with open("data/system_instruction.txt", "r", encoding="utf-8") as f:
       system_instructions_preset = f.read()
except FileNotFoundError:
    system_instructions_preset = """You are an exceptionally helpful and friendly chatbot. 
Your purpose is to provide concise and accurate information as requested by the user. 
You should only use the available tools to answer these types of questions. 
If a question is outside of your capabilities, politely inform the user that you are unable to help with that request.
"""

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")
model_choice = st.sidebar.selectbox("Select Gemini Model", ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],index=2)
system_instructions = st.sidebar.text_area("System Instructions", system_instructions_preset,height=600)

if st.sidebar.button("🔄 Reset Chat"):
    st.session_state.chat_handler = ChatHandler(
        system_instructions=system_instructions,
        model_choice=model_choice,
    )
    st.session_state.messages = []  # clear chat history
    st.session_state.last_instruction = system_instructions
    st.session_state.last_model = model_choice
    st.rerun()

# Initialize session state
if "chat_handler" not in st.session_state:
    st.session_state.chat_handler = ChatHandler(system_instructions=system_instructions,model_choice=model_choice)
    st.session_state.messages = []


# Page config
st.set_page_config(page_title="Gemini Chatbot", page_icon="💬", layout="wide", menu_items={
        'Get Help': 'https://martinmoreau.tech/help',
        'Report a bug': "https://martinmoreau.tech/bug",
        'About': "This is an *extremely* cool app!"
    })

# Hide "Deploy" and "Report a bug" from the 3-dots menu
# CSS for full page, header, chat bubbles, and input
st.markdown(
    """
    <style>
    /* Page background */
    body {
        background-color: #F3F4F6;
    }
    div[data-testid="stAppDeployButton"] {
        display: none !important;
    }
    /* Chat container card */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 100%;
        max-height: 100%;
        overflow-y: auto;
        padding: 20px;
        border-radius: 15px;
        background-color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    /* User bubble */
    .user-bubble {
        align-self: flex-end;
        background-color: #8219ac;
        color: white;
        padding: 10px 15px;
        border-radius: 20px 20px 0 20px;
        max-width: 70%;
        word-wrap: break-word;
    }
    /* Gemini bubble */
    .gemini-bubble {
        align-self: flex-start;
        background-color: #594ef3;
        color: white;
        padding: 10px 15px;
        border-radius: 20px 20px 20px 0;
        max-width: 70%;
        word-wrap: break-word;
    }
    /* Timestamp */
    .timestamp {
        font-size: 0.7em;
        color: #f5f5f5;
        margin-top: 2px;
    }
    /* Input box */
    div.stTextInput > label {
        font-weight: bold;
        color: #1E3A8A;
    }
    div.stTextInput > div > input {
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App title
st.markdown('<h1 style="color:#1E3A8A;">💬 Gemini Chatbot</h1>', unsafe_allow_html=True)

# Build chat HTML
chat_html = '<div class="chat-container">'
for msg in st.session_state.messages:
    timestamp = datetime.now().strftime("%H:%M")
    if msg["role"] == "user":
        chat_html += f'<div class="user-bubble">{msg["text"]}<div class="timestamp">{timestamp}</div></div>'
    else:
        chat_html += f'<div class="gemini-bubble">{msg["text"]}<div class="timestamp">{timestamp}</div></div>'
chat_html += '</div>'

# Render all messages
st.markdown(chat_html, unsafe_allow_html=True)

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...")
    submitted = st.form_submit_button("Send")

# The input and form handling part remains the same
if submitted and user_input.strip():
    # 1. Append and display the user message immediately
    st.session_state.messages.append({"role": "user", "text": user_input})

    # 2. Add a temporary "typing..." message for the user to see
    st.session_state.messages.append({"role": "gemini", "text": "...", "status": "typing"})

    # 3. Rerun to show the user's message and the "typing" indicator
    st.rerun()

# This part runs after the first rerun and the app state is updated
if st.session_state.messages and st.session_state.messages[-1].get("status") == "typing":
    # Get the user's latest message (the one right before the "typing" message)
    user_message = st.session_state.messages[-2]["text"]

    # Call the API to get the real response
    response = st.session_state.chat_handler.handle_user_message(user_message)

    # Replace the "typing" message with the final response
    st.session_state.messages[-1] = {"role": "gemini", "text": response}

    # Rerun again to display the final Gemini response
    st.rerun()
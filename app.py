import streamlit as st
from datetime import datetime
from core.chat_handler import ChatHandler

# Load system instructions preset
try:
    with open("data/system_instruction.txt", "r", encoding="utf-8") as f:
        system_instructions_preset = f.read()
except FileNotFoundError:
    system_instructions_preset = """You are an exceptionally helpful and friendly chatbot. 
Your purpose is to provide concise and accurate information as requested by the user. 
If a question is outside of your capabilities, politely inform the user that you are unable to help with that request.
"""

# Sidebar config
st.sidebar.header("⚙️ Configuration")
model_choice = st.sidebar.selectbox(
    "Select Gemini Model",
    ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
    index=2,
)
system_instructions = st.sidebar.text_area(
    "System Instructions", system_instructions_preset, height=400
)

if st.sidebar.button("🔄 Reset Chat"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.chat_handler = ChatHandler(
        system_instructions=system_instructions,
        model_choice=model_choice
    )
    st.session_state.messages = []
    st.rerun()

# Page config
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="💬",
    layout="wide",
    menu_items={
        'Get Help': 'https://martinmoreau.tech/help',
        'Report a bug': "https://martinmoreau.tech/bug",
        'About': "This is an *extremely* cool app!"
    }
)

# Session init
if "chat_handler" not in st.session_state:
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.chat_handler = ChatHandler(
        system_instructions=system_instructions,
        model_choice=model_choice
    )
    st.session_state.messages = []

# Title
st.title("💬 Gemini Chatbot")

# Show conversation (simple layout)
for msg in st.session_state.messages:
    timestamp = datetime.now().strftime("%H:%M")
    if msg["role"] == "user":
        st.markdown(f"**🧑 You [{timestamp}]:** {msg['text']}")
    else:
        st.markdown(f"**🤖 Gemini [{timestamp}]:** {msg['text']}")

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    # Save user message
    st.session_state.messages.append({"role": "user", "text": user_input})

    # Show spinner while fetching Gemini response
    with st.spinner("🤖 Gemini is thinking..."):
        response = st.session_state.chat_handler.handle_user_message(user_input)

    # Save Gemini's reply
    st.session_state.messages.append({"role": "gemini", "text": response})
    st.rerun()
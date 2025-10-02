import streamlit as st
from datetime import datetime
from core.chat_handler import ChatHandler



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

hide_streamlit_style = """
    <style>
    div[data-testid="stAppDeployButton"] {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Session init
if "chat_handler" not in st.session_state:
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.chat_handler = ChatHandler()
    st.session_state.messages = []

# Title
st.title("💬 Gemini Chatbot")

# Show conversation
for msg in st.session_state.messages:
    timestamp = datetime.now().strftime("%H:%M")
    if msg["role"] == "user":
        st.markdown(f"**🧑 You [{timestamp}]:** {msg['text']}")
    else:
        st.markdown(f"**🤖 Gemini [{timestamp}]:** {msg['text']}")

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...")
    # Place Send and Reset side by side
    col1, col2, col3 = st.columns([1, 4, 1])  # wider input area, smaller reset button
    with col1:
        submitted = st.form_submit_button("✅ Send")
    with col3:
        reset_clicked = st.form_submit_button("🔄 Reset Chat", help="Clear the conversation")

if reset_clicked:
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.chat_handler = ChatHandler()
    st.session_state.messages = []
    st.rerun()

if submitted and user_input.strip():
    # 1. Save user message
    st.session_state.messages.append({"role": "user", "text": user_input})
    
    # 2. Add "typing..." placeholder
    st.session_state.messages.append({"role": "gemini", "text": "⏳ Gemini is thinking..."})
    st.rerun()

# Check for "typing..." placeholder and replace with actual response
if st.session_state.messages and st.session_state.messages[-1]["text"] == "⏳ Gemini is thinking...":
    user_message = st.session_state.messages[-2]["text"]

    # Show spinner while fetching response
    with st.spinner("🤖 Gemini is thinking..."):
        response = st.session_state.chat_handler.handle_user_message(user_message)

    # Replace placeholder with real response
    st.session_state.messages[-1] = {"role": "gemini", "text": response}
    st.rerun()

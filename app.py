#  app.py
import streamlit as st
from core.chat_handler import ChatHandler

# Page config
st.set_page_config(
    page_title="Gemini + MCP Chatbot",
    page_icon="💬",
    layout="wide",
    menu_items={
        'Get Help': 'https://martinmoreau.tech/help',
        'Report a bug': "https://martinmoreau.tech/bug",
        'About': "This is an *extremely* cool app!"
    }
)
st.title("💬 Gemini + MCP Chatbot")
hide_streamlit_style = """
    <style>
    div[data-testid="stAppDeployButton"] {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Reset button ---
if st.sidebar.button("🔄 Reset Chat"):
    st.session_state.clear()
    st.rerun()

if "chat_handler" not in st.session_state:
    st.session_state.chat_handler = ChatHandler()
    st.session_state.messages = []

chat_handler = st.session_state.chat_handler

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = chat_handler.handle_user_message(user_input)

    if response:  # no approval needed
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

# Approval UI
if chat_handler.pending_tools:
    tool_name, tool_args, _ = chat_handler.pending_tools[0]
    st.sidebar.warning(f"⚠️ Tool '{tool_name}' requires approval")
    st.sidebar.json(tool_args)

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Approve"):
        response = chat_handler.continue_after_approval(True)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    if col2.button("Deny"):
        response = chat_handler.continue_after_approval(False)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

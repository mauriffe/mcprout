from core.chat_handler import ChatHandler

def main():
    # ANSI color codes
    USER_COLOR = "\033[94m"    # Blue
    GEMINI_COLOR = "\033[92m"  # Green
    RESET = "\033[0m"          # Reset to default

    # Initialize the chat handler with tools
    chat_handler = ChatHandler(system_instructions="",model_choice="gemini-2.5-flash-lite")
    print("Welcome to the chat with Gemini.")
    print("Type 'exit' to end the conversation.")
    while True:
        user_input = input(f"{USER_COLOR}You: {RESET}")
        if user_input.lower() == 'exit':
            break

        response_text = chat_handler.handle_user_message(user_input)
        print(f"{GEMINI_COLOR}Gemini: {response_text}{RESET}")

if __name__ == "__main__":
    main()
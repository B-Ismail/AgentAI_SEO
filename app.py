import streamlit as st
import os
from session_utils import get_session_state
from agent_manager import create_agent


# Sidebar for API Key
st.sidebar.header("Configuration")
#openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
openai_api_key = os.getenv("OPENAI_API_KEY")
# Check API Key Status
if openai_api_key:
    st.sidebar.success("OpenAI API Key provided. Agent will be initialized.")
else:
    st.sidebar.warning("Please provide your OpenAI API Key to enable the assistant.")

# Initialize session state
session_state = get_session_state()

# Initialize the agent if not already done
if openai_api_key and not session_state['agent']:
    session_state['agent'] = create_agent(openai_api_key)

agent = session_state['agent']

# Main UI
st.title("SEO Assistant")

# Ensure user input is properly managed
if 'last_input' not in st.session_state:
    st.session_state.last_input = ''

def handle_input():
    st.session_state.last_input = st.session_state.current_input
    st.session_state.current_input = ''

st.text_area(
    "Enter your query (Shift+Enter for new line, Submit to send):",
    key="current_input",
    height=100,
    on_change=handle_input,
    placeholder="Type your query here..."
)

if st.button("Submit"):
    user_input = st.session_state.last_input.strip()
    if not user_input:
        st.warning("Input is empty. Please enter a valid query.")
    elif not agent:
        st.error("Agent not initialized. Please provide an OpenAI API key.")
    else:
        # Append user input to chat history
        session_state['chat_history'].append({"role": "user", "content": user_input})

        # Process input with agent
        try:
            result = agent.run({"input": user_input})
            session_state['chat_history'].append({"role": "assistant", "content": result})
            st.write(result)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Clear Conversation
if st.button("Clear Conversation"):
    session_state['chat_history'] = []
    st.session_state.last_input = ''
    st.rerun()

# Display Chat History
st.subheader("Conversation History")
conversation_html = """
<div style="max-height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
"""

# Add messages to the container
for i, msg in enumerate(reversed(session_state['chat_history'])):
    if msg["role"] == "user":
        conversation_html += f"<p><strong style='color: #007bff;'>You:</strong> {msg['content']}</p>"
    else:
        conversation_html += f"<p><strong style='color: #28a745;'>AI Agent:</strong> {msg['content']}</p>"
    if i < len(session_state['chat_history']) - 1:
        conversation_html += "<hr style='border: none; border-top: 1px solid #ccc; margin: 10px 0;'>"

conversation_html += "</div>"
st.markdown(conversation_html, unsafe_allow_html=True)

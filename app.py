import logging
import time
import streamlit as st
import os
from session_utils import get_session_state
from agent_manager import create_agent, get_agent_with_session


# Sidebar for API Key
st.sidebar.header("Configuration .env file")
#openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
openai_api_key = os.getenv("OPENAI_API_KEY")
# Check API Key Status
if openai_api_key:
    st.sidebar.success("OpenAI API Key provided. Agent will be initialized.")
else:
    st.sidebar.warning("Please provide your OpenAI API Key to enable the assistant.")
# Retrieve RapidAPI Key and Sender Email from environment variables
rapidapi_key = os.getenv("RAPIDAPI_KEY")
sender_email = os.getenv("SENDER_EMAIL")

# Check RapidAPI Key Status
if rapidapi_key:
    st.sidebar.success("RapidAPI Key is provided. External API calls are enabled.")
else:
    st.sidebar.warning("Please provide your RapidAPI Key to enable API calls.")

# Check Sender Email Status
if sender_email:
    st.sidebar.success(f"The sender's Email is configured.")
else:
    st.sidebar.warning("Please provide a Sender Email to enable email functionality.")
# Initialize session state
session_state = get_session_state()

# Initialize the agent if not already done
if openai_api_key and not session_state['agent']:
    print("Initializing agent...")
    session_state['agent'] = get_agent_with_session(openai_api_key,session_state)

if "agent" not in st.session_state or st.session_state["agent"] is None:
    st.session_state["agent"] = create_agent(os.getenv("OPENAI_API_KEY"))   
agent = st.session_state["agent"]
# Main UI
st.title("SEO Assistant")

# Ensure last_input and last_seo_data exist in session_state
if "last_input" not in st.session_state:
    st.session_state["last_input"] = ""
if "last_seo_data" not in st.session_state:
    st.session_state["last_seo_data"] = None

def handle_input():
    st.session_state.last_input = st.session_state.current_input
    st.session_state.current_input = ''

st.text_area(
    "Enter your query (Enter for new line, Submit to send):",
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
        session_state['chat_history'].append({"role": "user", "content": user_input})

        try:
            start_time = time.time()
            result = agent.run({"input": user_input})  # Run the agent with user input
            print(f"LLM took {time.time() - start_time} seconds to respond")
            
            # Ensure result is structured for tools like send_email_summary
            if isinstance(result, dict) and "action" in result and "action_input" in result:
                action_input = result["action_input"]

                # Combine subject and body if needed for the structured tool
                if result["action"] == "send_email_summary" and isinstance(action_input, dict):
                    action_input = {
                        "content": f"Subject: {action_input.get('subject', '')}\n\n{action_input.get('body', '')}"
                    }
                    # Update result to pass a single string for send_email_summary
                    result["action_input"] = action_input

            print(result)  # Debug the structured result
            session_state['chat_history'].append({"role": "AI agent", "content": result})
            st.write(result)
        except Exception as e:
            logging.error(f"An error occurred in app: {e}")



# Show download button only if SEO data exists
if "last_seo_data" in st.session_state and st.session_state["last_seo_data"] is not None:
    with open("seo_data.txt", "rb") as file:
        st.download_button("Download SEO Data", file, file_name="seo_data.txt", mime="text/plain")

# Clear Conversation
if st.button("Clear Conversation"):
    st.session_state['chat_history'] = []
    st.session_state['last_input'] = ''
    st.session_state['last_seo_data'] = None  # Reset last_seo_data
    st.rerun()  # Rerun to refresh the UI

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
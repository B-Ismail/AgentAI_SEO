import re
import smtplib
import os
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from fetch_seo_data import fetch_seo_data

# Load environment variables
load_dotenv()

# Configure logging
#logging.basicConfig(level=logging.INFO, filename='email_log.txt', filemode='a', format='%(asctime)s - %(message)s')

# Extracts all email addresses from the input text
def get_first_email(input_text: str) -> str:
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    matches = re.findall(email_pattern, input_text)
    return matches[0] if matches else None

# Extract domain from user input
def extract_domain_from_input(user_input: str) -> str:
    pattern = r"https?://[a-zA-Z0-9./-]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, user_input)
    return match.group(0) if match else ""

# Extract SEO data from user input
def extract_seo_data(user_input: str) -> dict:
    domain = extract_domain_from_input(user_input)
    return {"domain": domain} if domain else {}

# Retrieve user input from session state
def get_user_input_from_session(session_state):
    return session_state.get('last_input', '').strip()

# Retrieve the agent instance from session state
def get_agent_from_session(session_state):
    return session_state.get('agent', None)

# Retrieve any additional variables from session state
def get_variable_from_session(session_state, variable_name):
    return session_state.get(variable_name, None)

# Generate email content
def generate_email_content(agent, seo_data):
    subject = f"SEO Analysis Summary for {seo_data.get('domain', 'Unknown Domain')}"
    body = agent.run({
        "input": f"Summarize the following SEO data: {seo_data}"
    })
    return subject, body

# Send emails using SMTP
def send_email(user_input, session_state):
    """
    Sends emails dynamically, ensuring the website for SEO data is extracted from chat history.
    """
    try:
        # Extract recipient email from user input or last user message
        recipient_email = get_first_email(user_input)
        if not recipient_email:
            last_user_message = session_state["chat_history"][-1]["content"] if session_state.get("chat_history") else ""
            recipient_email = get_first_email(last_user_message)
            logging.info(f"Recipient email from chat history: {recipient_email}")

        if not recipient_email:
            return "No valid email addresses found in the input text or chat history. Please provide a valid email address."

        # Retrieve the agent dynamically from session_state
        agent = get_agent_from_session(session_state)
        if not agent:
            raise ValueError("Agent is not initialized in session state.")

        # Extract the website URL for SEO data from chat history
        website_url = None
        for msg in reversed(session_state.get("chat_history", [])):
            if "http" in msg["content"]:  # Find the first message with a URL
                website_url = extract_domain_from_input(msg["content"])
                break

        if not website_url:
            return "No website URL found in chat history to fetch SEO data."

        # Retrieve or fetch SEO data
        if "last_seo_data" not in session_state or session_state["last_seo_data"].get("domain") != website_url:
            logging.info(f"Fetching SEO data for URL: {website_url}")
            session_state["last_seo_data"] = fetch_seo_data(website_url)
        seo_data = session_state["last_seo_data"]

        # Validate SEO data
        if not seo_data or "error" in seo_data:
            return f"Failed to fetch valid SEO data: {seo_data.get('error', 'Unknown error')}"

        # Generate email content using the SEO data
        subject = f"SEO Analysis for {seo_data.get('domain', 'Unknown Domain')}"
        body = (
            f"Here is the summary of SEO data:\n\n"
            f"Title: {seo_data.get('title', 'No title found')}\n"
            f"Description: {seo_data.get('description', 'No description found')}\n"
            f"Visits: {seo_data.get('visits', 0)}\n\n"
            f"Similar Sites:\n" +
            "\n".join([f"- {site['domain']}: {site['title']}" for site in seo_data.get('similar_sites', [])])
        )

        # Add user input as additional content
        body += f"\n\nMessage from Agent_SEO"

        # Retrieve sender email and password
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        if not sender_email or not sender_password:
            raise ValueError("Sender email or password not set in environment variables.")

        # Connect to SMTP and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)

            # Create and send the email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail(sender_email, recipient_email, msg.as_string())
            logging.info(f"Email sent to {recipient_email}")

        return f"Email successfully sent to {recipient_email}"

    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Failed to send email: {e}"
    except ValueError as e:
        logging.error(f"Value error occurred: {e}")
        return str(e)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return f"An unexpected error occurred: {e}"

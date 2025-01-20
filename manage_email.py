import re
import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from fetch_seo_data import fetch_seo_data

# Load environment variables
load_dotenv()

# Configure logging
#logging.basicConfig(level=logging.INFO, filename='email_log.txt', filemode='a', format='%(asctime)s - %(message)s')

# Extracts the first email address from the input text
def get_first_email(input_text: str) -> str:
    """
    Extracts the first valid email address from the input text.
    """
    # Regular expression to match valid email addresses
    email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    # Find all matches
    matches = re.findall(email_pattern, input_text)
    # Return the first match or an empty string
    return matches[0] if matches else ""

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


# Send emails using SMTP
def extract_recipient_email(user_input, session_state):
    """
    Extracts the recipient email from user input or chat history.
    """
    recipient_email = get_first_email(user_input)
    if not recipient_email and session_state.get("chat_history"):
        # Try extracting from the last user message in chat history
        last_user_message = session_state["chat_history"][-1]["content"]
        recipient_email = get_first_email(last_user_message)
        logging.info(f"Recipient email from chat history: {recipient_email}")
    return recipient_email


def extract_website_url_from_chat(session_state):
    """
    Extracts the website URL from the chat history.
    """
    for msg in reversed(session_state.get("chat_history", [])):
        if "http" in msg["content"]:  # Find the first message with a URL
            return extract_domain_from_input(msg["content"])
    return None


def fetch_and_validate_seo_data(website_url, session_state):
    """
    Fetches SEO data for the website URL and validates it.
    """
    if "last_seo_data" not in session_state or session_state["last_seo_data"].get("domain") != website_url:
        logging.info(f"Fetching SEO data for URL: {website_url}")
        session_state["last_seo_data"] = fetch_seo_data(website_url)

    seo_data = session_state["last_seo_data"]
    if not seo_data or "error" in seo_data:
        return None, f"Failed to fetch valid SEO data: {seo_data.get('error', 'Unknown error')}"
    return seo_data, None


def generate_email_content(seo_data):
    """
    Generates the email subject and body using the SEO data.
    """
    subject = f"SEO Analysis for {seo_data.get('domain', 'Unknown Domain')}"
    tags = ", ".join(seo_data.get('tags', [])) if seo_data.get('tags') else "No tags found"
    body = (
        f"Here is the summary of SEO data:\n\n"
        f"Title: {seo_data.get('title', 'No title found')}\n"
        f"Description: {seo_data.get('description', 'No description found')}\n"
        f"Visits: {seo_data.get('visits', 0)}\n"
        f"Key Words: {tags}\n"
        f"Response Time: {seo_data.get('response_time', 0):.2f} seconds\n"
        f"Similar Sites:\n" +
        "\n".join([f"- {site['domain']}: {site['title']}" for site in seo_data.get('similar_sites', [])[:6]])
    )
    body += f"\n\nMessage from Agent_SEO"
    return subject, body


def send_smtp_email(subject, body, recipient_email):
    """
    Sends the email using SMTP.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    if not sender_email or not sender_password:
        raise ValueError("Sender email or password not set in environment variables.")

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(sender_email, recipient_email, msg.as_string())
        logging.info(f"Email sent to {recipient_email}")


def fetch_and_validate_seo_data(website_url, session_state):
    """
    Fetches SEO data for the website URL and validates it.
    """
    logging.debug(f"Fetching SEO data for: {website_url}")
    if "last_seo_data" not in session_state or session_state["last_seo_data"] is None:
        session_state["last_seo_data"] = fetch_seo_data(website_url)
        logging.debug(f"Fetched SEO data: {session_state['last_seo_data']}")

    seo_data = session_state.get("last_seo_data")
    if not seo_data:
        logging.error("SEO data is None.")
        return None, "Failed to fetch SEO data: No data returned."

    if "error" in seo_data:
        logging.error(f"SEO data contains error: {seo_data.get('error')}")
        return None, f"Failed to fetch valid SEO data: {seo_data.get('error', 'Unknown error')}"

    return seo_data, None


def send_email(user_input, session_state,):
    """
    Main function to send an email with SEO analysis data.
    """
    try:
        # Extract recipient email
        recipient_email = extract_recipient_email(user_input, session_state)
        print(f"Recipient email: {recipient_email}")
        if not recipient_email:
            return "No valid email addresses found in the input text or chat history."

        # Extract website URL
        website_url = extract_website_url_from_chat(session_state)
        print(f"Website URL: {website_url}")
        if not website_url:
            return "No website URL found in chat history to fetch SEO data."

        # Fetch and validate SEO data
        seo_data, error = fetch_and_validate_seo_data(website_url, session_state)
        if error:
            return error

        print(f"Validated SEO data: {seo_data}")

        # Generate email content
        subject, body = generate_email_content(seo_data)

        # Send the email
        send_smtp_email(subject, body, recipient_email)

        return f"Email successfully sent to {recipient_email}"

    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Failed to send email: {e}"
    except ValueError as e:
        logging.error(f"Value error occurred: {e}")
        return str(e)
    except Exception as e:
        logging.error(f"Unexpected error in send_email: {e}")
        return f"An unexpected error occurred: {e}"


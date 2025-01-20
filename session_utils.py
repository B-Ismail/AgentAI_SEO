import streamlit as st


def get_session_state():
    """
    Retrieves or initializes the session state variables.

    Returns:
        dict: A dictionary-like object for managing session variables.
    """
    default_state = {
        'chat_history': [],  # Stores the history of user and agent interactions
        'user_input': " ",   # Stores the latest user input
        'agent': None,       # Holds the LLM agent instance
        'last_seo_data': None  # Stores the most recent SEO data
    }
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value
    return st.session_state

import streamlit as st

def get_session_state():
    """
    Retrieves or initializes the session state variables.

    Returns:
        dict: A dictionary-like object for managing session variables.
    """
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = " "
    if 'agent' not in st.session_state:
        st.session_state['agent'] = None

    return st.session_state

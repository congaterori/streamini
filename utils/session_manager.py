import os
import pickle
import streamlit as st
import os
import streamlit as st

from utils.model_utils import create_model

def SESSION_DIRECTORY():
    SESSION_DIR = "session/assistant/"
    # Additional logic to handle the session directory can be added here
    return SESSION_DIR

SESSION_DIR = "session/assistant/"

def save_chat_session(filename, messages, model, chat_session_history):
    """Saves the current chat session to a pickle file."""
    try:
        with open(os.path.join(SESSION_DIR, filename), "wb") as f:
            pickle.dump(
                {
                    "messages": messages,
                    "model": model,
                    "chat_session_history": chat_session_history,
                },
                f,
            )
        st.sidebar.success(f"Chat session '{filename}' saved successfully!")
    except Exception as e:
        st.sidebar.error(f"Failed to save session: {e}")

def load_chat_session(filename, system_prompt):  # Add system_prompt as argument
    """Loads a saved chat session from a pickle file."""
    try:
        with open(os.path.join(SESSION_DIR, filename), "rb") as f:
            saved_data = pickle.load(f)
        st.session_state.messages = saved_data["messages"]
        st.session_state.current_model = saved_data["model"]
        st.session_state.chat_session = create_model(
            st.session_state.current_model, system_prompt  # Pass system_prompt
        ).start_chat(history=saved_data["chat_session_history"])
        st.sidebar.success(f"Chat session '{filename}' loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Failed to load session: {e}")

def display_session_management_controls(
    session_name, saved_sessions, last_session_index, system_prompt  # Add system_prompt
):
    """Displays the session management controls in the sidebar."""


    """
    # Button to save the current session
    if st.sidebar.button("Save Chat Session"):
        if session_name:
            save_chat_session(
                session_name + ".pkl",
                st.session_state.messages,
                st.session_state.current_model,
                st.session_state.chat_session.history,
            )
        else:
            st.sidebar.error("Please enter a session name before saving.")
    """
    
    # Dropdown to select a session to load
    # selected_session = st.sidebar.selectbox(
        # "Load a saved session:", saved_sessions, index=last_session_index)

    """
    # Button to load the selected session
    if st.sidebar.button("Load Chat Session"):
        if selected_session:
            load_chat_session(selected_session, system_prompt)  # Pass system_prompt
        else:
            st.sidebar.error("Please select a session to load.")
    """

    # Button to delete the selected session (with red warning text)
    # st.sidebar.markdown(
        # """<h1 style="color:red">Delete selected session:</h1>""",
        # unsafe_allow_html=True,)
    
    """
    if st.sidebar.button("Delete Session"):
        if selected_session:
            os.remove(os.path.join(SESSION_DIR, selected_session))
            st.sidebar.success("Session deleted successfully.")
        else:
            st.sidebar.error("Please select a session to delete.")
    """
import os
import streamlit as st
from PIL import Image
import google.generativeai as genai

from utils.config_manager import load_config, update_config
from utils.session_manager import (
    display_session_management_controls,
)
from utils.model_utils import (
    create_model,
    display_chat_message,
    handle_text_message,
    handle_image_upload,
    handle_document_upload,
)
# Set up Streamlit page configuration
st.set_page_config(layout="wide")

SESSION_DIR = "session/assistant/"

# Load configuration from YAML file
config = load_config()

# Load assistant image
assistant_image = Image.open("images/assistant.png")

# System prompt for specific models
system_prompt = config["system_prompt"]

# API Keys
api_key = config["api_key"]
api_keys = config["api_keys"]

# Models
model = config["model"]
models = config["models"]

st.write(
    """<h1 class="glowing-text" style="color: #f073f0;">Streamini ✨ [DEMO]</h1>""",
    unsafe_allow_html=True,
)

# Expander for notes and information
with st.expander("Note"):
    note = f"""
    - **Refresh the page after changing the Model or API key.** <br>
    - Current Model: <code>{model}</code> <br>
    """
    st.markdown(note, unsafe_allow_html=True)

# Sidebar: Title, image, and controls
st.sidebar.image(assistant_image, use_column_width=True)

# CSS for glowing 'None' in API key selection
st.markdown(
    """
    <style>
        .red-glow {{
            color: #ff3333;
            text-shadow: 0 0 5px #ff3333, 0 0 10px #ff3333, 0 0 15px #ff3333;
            font-weight: bold;
        }}
        @keyframes glow {{
        0% {{
            text-shadow: 0 0 5px #f073f0;
        }}
        50% {{
            text-shadow: 0 0 20px #f073f0, 0 0 30px #f073f0;
        }}
        100% {{
            text-shadow: 0 0 5px #f073f0;
        }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# API Key Management
st.sidebar.markdown(
    """> <h1 style="color: #f249f2;">Configure API Key and Model</h1>""",
    unsafe_allow_html=True,
)
selected_api_key = st.sidebar.selectbox(
    "Select API Key:", api_keys, index=api_keys.index(api_key)
)

# Input box for entering a new API key if "None" is selected
if selected_api_key == "None":
    new_api_key = st.sidebar.text_input("Enter a new API Key:", type="password")
    if new_api_key:
        api_key = new_api_key
        # update_config("api_key", api_key)
        # api_key = selected_api_key  # Reset to the selected key

# Update the API key if the selection changes
if selected_api_key != api_key:
    update_config("api_key", selected_api_key)
    api_key = selected_api_key

# Configure Google Generative AI with the selected API key
# genai.configure(api_key=api_key)
genai.configure(api_key=new_api_key)

# Model Selection
selected_model = st.sidebar.selectbox(
    "Select the model:", models, index=models.index(model)
)

# Update the model if the selection changes
if selected_model != model:
    update_config("model", selected_model)
    model = selected_model

# Initialize chat history if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create directory for saving sessions if it doesn't exist
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)



# Sidebar: Session management controls
# st.sidebar.write("---")
# st.sidebar.markdown(
    # """> <h1 style="color: #f249f2;">Session Management</h1>""",
    # unsafe_allow_html=True,)



session_name = '' # st.sidebar.text_input("Enter session name to save:", value="last_session")

# List available saved sessions
saved_sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith(".pkl")]

# Find the index of 'last_session.pkl' for default selection
last_session_index = (
    saved_sessions.index("last_session.pkl") if "last_session.pkl" in saved_sessions else None
)

# Display session management controls
display_session_management_controls(session_name, saved_sessions, last_session_index, system_prompt)

# Initialize or reset the chat session if needed
if "chat_session" not in st.session_state or st.session_state.get(
    "current_model"
) != selected_model:
    st.session_state.chat_session = create_model(selected_model, system_prompt).start_chat(
        history=[]
    )
    st.session_state.current_model = selected_model

# Display chat messages from history
for message in st.session_state.messages:
    display_chat_message(message["role"], message)

# User input for text messages
user_message = st.chat_input("Type your message here...")

# Process user input (text or image)
with st.spinner("Waiting for response..."):
    # Handle text messages
    if user_message:
        handle_text_message(user_message, st.session_state.chat_session)

    # Handle image uploads with comments
    st.sidebar.write("---")
    st.sidebar.markdown(
        """> <h1 style="color: #f249f2;">Upload Images</h1>""", unsafe_allow_html=True
    )
    uploaded_image = st.sidebar.file_uploader(
        "Choose an image...", type=["jpg", "jpeg", "png", "webp", "heic", "heif"]
    )
    image_comment = st.sidebar.text_area("Add a comment for the image (required):")
    send_image_button = st.sidebar.button("Send Image")

    if send_image_button:
        handle_image_upload(uploaded_image, image_comment, st.session_state.chat_session)

    # Handle document uploads with comments
    st.sidebar.write("---")
    st.sidebar.markdown(
        """> <h1 style="color: #f249f2;">Upload Documents</h1>""", unsafe_allow_html=True
    )
    uploaded_document = st.sidebar.file_uploader(
        "Choose a document...",
        type=[
    "xml", "py", "txt", "html", "js", "css", "ps1", 
    "json", "md", "yml", "yaml", "ts", "tsx", "c", "cpp", 
    "h", "hpp", "java", "cs", "php", "pl", "rb", "sh", 
    "bat", "ini", "log", "toml", "rs", "go", "r", "jl", 
    "lua", "swift", "sql", "asm", "vb", "vbs", "jsx", 
    "svelte", "vue", "scss", "less", "tex", "rmd", "m", 
    "scala", "erl", "hs", "f90", "pas", "groovy", "pdf"
                ],
    )
    document_comment = st.sidebar.text_area("Add a comment for the document (required):")
    send_document_button = st.sidebar.button("Send Document")

    if send_document_button:
        handle_document_upload(
            uploaded_document, document_comment, st.session_state.chat_session
        )

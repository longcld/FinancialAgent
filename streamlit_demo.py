from dotenv import load_dotenv
load_dotenv(".env")

import streamlit as st
from io import StringIO
import pymupdf4llm
from logger import logger
import os
from pathlib import Path
import json
import requests
import sseclient

from config import configs

from uuid import uuid4

thinking_template = """
<div style="background-color: #e6f2ff; padding: 10px; border-radius: 5px; font-style: italic; color: #333; border-left: 4px solid #4b9afa;">
    {thinking_content}
</div>
"""

# Define a spinner class that can be controlled programmatically
class ControlledSpinner:
    def __init__(self, text="In progress..."):
        self.text = text
        self._spinner = None

    def _start(self):
        with st.spinner(self.text):
            yield

    def start(self):
        self._spinner = iter(self._start())
        next(self._spinner)  # Start the spinner

    def stop(self):
        if self._spinner:
            next(self._spinner, None) 

st.set_page_config(page_title="VPBank Agent Demo", page_icon=":bank:", layout="wide")
st.title("VPBank Agent Demo :bank:")

def get_response(message):
    """
    Send a message to the FastAPI backend and get a response stream.
    """
    url = "http://localhost:8000/api/v1/chat/ainvoke"
    headers={
        "Content-Type": "application/json",
        "X-API-Key": configs.fastapi_keys[0],
    }
    request = {
        "user_id": st.session_state.request_info.get("user_id"),
        "session_id": st.session_state.request_info.get("session_id"),
        "message": message,
        "params": {}
    }

    logger.debug(f"Sending request to {url} with data: {json.dumps(request, indent=2, ensure_ascii=False)}")

    # Use a stream request to get SSE events
    return requests.post(url, json=request, headers=headers, stream=True)

# Sidebar text input
user_name = st.sidebar.text_input("Enter your name:")

# Initialize session state
if "request_info" not in st.session_state:
    if not user_name.strip():
        st.sidebar.warning("Please enter your name to continue.")
        st.stop()
    st.session_state.request_info = {
        "user_id": user_name,
        "session_id": str(uuid4()),  # Generate a new session ID for each run
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

    # Check if upload directory exists, if not create it
    if not os.path.exists(f"{configs.upload_dir}/{st.session_state.request_info['user_id']}"):
        os.makedirs(f"{configs.upload_dir}/{st.session_state.request_info['user_id']}")

if "file_content" not in st.session_state:
    st.session_state.file_content = ""

# Allow multiple file upload
uploaded_files = st.sidebar.file_uploader(
    "Upload text or PDF files (max 1 MB each)",
    type=["txt", "pdf"],
    accept_multiple_files=True
)

status_placeholder = st.sidebar.empty()

# Process files
if uploaded_files:
    existed_files = []
    to_process_files = []
    for uploaded_file in uploaded_files:
        if uploaded_file.size > 4_048_576:
            status_placeholder.error(
                f"❌ File '{uploaded_file.name}' is too large ({uploaded_file.size / 4024:.2f} KB). MAX ALLOWED SIZE IS 4 MB. Please upload smaller files!!!"
            )
            continue
        file_path = str(Path(configs.upload_dir) / st.session_state.request_info['user_id'] / uploaded_file.name)
        # Check if the file is already uploaded
        if os.path.exists(file_path):
            status_placeholder.info(f"File {uploaded_file.name} already exists. Skipping upload.")
            existed_files.append(uploaded_file.name)
        # File not uploaded
        else:
            status_placeholder.info("⏳ Processing files...")
            # Save file bytes
            logger.debug(f"Saving file: {file_path}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            to_process_files.append(uploaded_file.name)

    if to_process_files:
        status_placeholder.info(f"⏳ Processing files: {to_process_files}")

        msg = f"""user just uploaded these new files:
            - Existed files, no need to process:\n{'\n'.join(existed_files)}
            - Need to process:\n{'\n'.join(to_process_files)}
            Only giving status of processing files, no need to return any content."""
        
        # Create SSE client
        client = sseclient.SSEClient(get_response(msg))

        with st.chat_message("assistant"):
            response_container = st.empty()
            response = ""

            response_container.markdown("⏳ Processing upload files... This may take a while depending on the file size and content. Please be patient...")
            # Process events
            for event in client.events():
                data = json.loads(event.data)
                token = data.get("content", "")
                if token:
                    response += token
                    response_container.markdown(response)
        status_placeholder.success("Files processed successfully!")

        

# Display chat history
with st.container():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])

# User input
if user_msg := st.chat_input("Ask a question about the files..."):
    st.chat_message("user").markdown(user_msg)
    # if not st.session_state.file_content.strip():
    #     st.warning("Please upload at least one file first.")
    # else:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_msg})
    
    # Truncate context if needed
    # context = st.session_state.file_content[:4000]

    # Create SSE client
    client = sseclient.SSEClient(get_response(user_msg))
    
    with st.chat_message("assistant"):
        
        thinking_spinner = ControlledSpinner("Thinking...")
        thinking_container = st.empty()
        response_container = st.empty()

        response = ""
        thinking_content = "THINKING...\n\n"
        # Process events
        for event in client.events():
            data = json.loads(event.data)
            token = data.get("content", "")
            if token:
                if data.get("type") == "think":
                    thinking_content += token

                    thinking_spinner.start()
                    thinking_container.write(
                        thinking_content,
                        # unsafe_allow_html=True,
                    )
                else:
                    thinking_spinner.stop()
                    thinking_container.empty()
                    response += token
                    response_container.markdown(response)
    
    # Append assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

from typing import Annotated
import os
import glob
from pathlib import Path

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from logger import logger
from utils import get_user_id
from config import configs
from graph.file_controler.preprocess import process_pdf

@tool
def get_uploaded_files(
    config: RunnableConfig
):
    """
    Get the list of uploaded files.
    """
    
    # Ensure the processed directory exists
    uploaded_dir = Path(configs.upload_dir) / get_user_id(config) / "processed"
    logger.debug(f"Getting uploaded files from directory: {uploaded_dir}")
    if not os.path.exists(uploaded_dir):
        logger.debug(f"Processed directory {uploaded_dir} does not exist.")
        return "No files uploaded yet."
    
    # List all files in the processed directory
    processed_files = glob.glob(f"{uploaded_dir}/*")
    logger.debug(f"Found {len(processed_files)} processed files in {uploaded_dir}.")
    
    uploaded_files = []
    for file_path in processed_files:
        file_name = os.path.basename(file_path)
        # if os.path.isfile(file_path):
        #     with open(file_path, "r", encoding="utf-8") as f:
        #         content = f.read()
        uploaded_files.append(file_name)
    logger.debug(f"Found {len(uploaded_files)} uploaded files.")
    return uploaded_files

@tool
def process_file(
    file_name: Annotated[str, "File path to process the unprocessed uploaded file from"],
    config: RunnableConfig
) -> Annotated[str, "Path of the saved document file."]:
    """
    Process the new uploaded file and save it to the processed directory.
    **Only use this tool when user upload a new file and need to process it.**
    """

    logger.debug(f"Processing file: {file_name}")

    raw_dir = Path(configs.upload_dir) / get_user_id(config)
    processed_dir = raw_dir / "processed"
    file_path = raw_dir / file_name

    if not processed_dir.exists():
        processed_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created processed directory: {processed_dir}")
    
    processed_text = process_pdf(str(file_path))
    if not processed_text:
        raise ValueError(f"Could not extract any text from the file: {file_path}")
    
    # Save the processed text to a file
    processed_file_path = processed_dir / file_name

    logger.debug(f"Saving processed file to: {processed_file_path}")
    with open(processed_file_path, "w", encoding="utf-8") as f:
        f.write(processed_text)

    return f"Tài liệu {file_name} đã được xử lý và lưu lại thành công trên hệ thống!"


tools = [
    process_file,
    # get_uploaded_files
]
from typing import Annotated
import os
import glob
from pathlib import Path

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from logger import logger
from utils import get_user_id
from config import configs

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
def read_file(
    file_name: Annotated[str, "File path to read the file from."],
    config: RunnableConfig
) -> str:
    """
    Get the content of a specific uploaded file by its filepath.
    """

    file_path = Path(configs.upload_dir) / get_user_id(config) / "processed" / file_name
    logger.debug(f"Getting content for file: {file_path}")

    if not file_path.exists():
        raise ValueError(f"File {file_path} does not exist.")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content.strip()


tools = [
    get_uploaded_files,
    read_file
]
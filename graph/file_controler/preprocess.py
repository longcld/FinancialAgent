from logger import logger
import os
import glob
import pymupdf
import pymupdf4llm
from langchain_openai import ChatOpenAI
import base64
from natsort import natsorted

logger.debug("Initializing OCR model...")
ocr_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
)

def llm_summary(text):
    """
    Summarize the given text using LLM.
    """

    summary_prompt = """You are a summarization expert. Given a chunk of text, summarize it in only ONE sentence in Vietnamese."""

    messages = [
        {
            "role": "system",
            "content": summary_prompt
        },
        {
            "role": "user",
            "content": text
        }
    ]
    
    response = ocr_model.invoke(messages)
    return response.content

def llm_ocr(image_path, is_summary=False):
    """
    Extract text from an image using OCR.
    """

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    # Getting the Base64 string
    base64_image = encode_image(image_path)

    if is_summary:
        ocr_prompt = """You are an OCR expert. Given an image, only extract the main content from it and briefly summarize it in only ONE sentence in Vietnamese."""
    else:
        ocr_prompt = """You are an OCR expert. Given an image, extract the text from it into a markdown format in Vietnamese."""

    messages = [
        {
            "role": "system",
            "content": ocr_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    response = ocr_model.invoke(messages)
    return response.content


def process_pdf(filename, st_placeholder=None):
    """
    Read a PDF file and extract text from it.
    """

    # Check if the file is a scanned document
    is_scan_file = True
    extracted_text = ""
    for i in range(1, 3):
        extracted_text = pymupdf4llm.to_markdown(
            doc=filename,
            pages=[i]
        )
        if extracted_text:
            is_scan_file = False
            break
    
    extracted_text = ""
    if is_scan_file:
        logger.debug(f"Cannot extract any text from file: {filename}, trying to extract images...")
        image_path = f"{filename.split(".")[0]}_images"

        # Create image path if it does not exist
        if os.path.exists(image_path) and os.path.isdir(image_path):
            logger.debug(f"Image path {image_path} already exists")
            # Get *-full.png file
            image_files = natsorted(glob.glob(f"{image_path}/*-full.png"))
            if not image_files:
                logger.debug(f"No images found in {image_path}, extracting images...")
                pymupdf4llm.to_markdown(
                    doc=filename,
                    write_images=True,
                    image_path=image_path,
                )
                image_files = natsorted(glob.glob(f"{image_path}/*-full.png"))
        else:
            logger.debug(f"Creating image path {image_path}")
            os.makedirs(image_path, exist_ok=True)
            logger.debug(f"Extracting images from {filename} to {image_path}")
            pymupdf4llm.to_markdown(
                doc=filename,
                write_images=True,
                image_path=image_path,
            )
            image_files = natsorted(glob.glob(f"{image_path}/*-full.png"))
        
        logger.debug("Start OCR on images with LLM...")
        # summary = ""
        # if len(image_files) > 3:
            # Only OCR and summarize the main content
            # for i in range(len(image_files)):
            #     if st_placeholder:
            #         st_placeholder.info(f"Processing page {i+1}/{len(image_files)}...")
            #     logger.debug(f"Processing image {i+1}/{len(image_files)}: {image_files[i]}")
            #     summary_text = llm_ocr(image_files[i], is_summary=True)
            #     summary += f"Page {i+1}:\n{summary_text}\n\n"
        # else:
        # OCR all images
        # logger.debug("Less than 3 images found, extracting all text...")
        for i in range(len(image_files)):
            logger.debug(f"Processing image {i+1}/{len(image_files)}: {image_files[i]}")
            llm_extracted_text = llm_ocr(image_files[i])
            extracted_text += f"Page {i+1}:\n{llm_extracted_text}\n\n"
    else:
        pages = pymupdf4llm.to_markdown(
            doc=filename,
            page_chunks=True
        )

        for i, page in enumerate(pages):
            if st_placeholder:
                st_placeholder.info(f"Processing page {i+1}/{len(pages)}...")
            logger.debug(f"Processing page {i+1}/{len(pages)}: {page['text']}")
            extracted_text += f"Page {i+1}:\n{page['text'].strip()}\n\n"

        # processed_folders = f"{filename.split('.')[0]}_processed"
        # # Create processed folder if it does not exist
        # if not os.path.exists(processed_folders):
        #     os.makedirs(processed_folders, exist_ok=True)

        # # Summarize the text from each page
        # summary = ""
        # for i, page in enumerate(pages):
        #     if st_placeholder:
        #         st_placeholder.info(f"Processing page {i+1}/{len(pages)}...")
        #     logger.debug(f"Processing page {i+1}/{len(pages)}...")
        #     text = page['text'].strip()
        #     if text:
        #         with open(f"{processed_folders}/page_{i+1}.txt", "w", encoding="utf-8") as f:
        #             f.write(text)
        #         summary_text = llm_summary(text)
        #         summary += f"Page {i+1}:\n\n{summary_text}\n\n"
        
    return extracted_text.strip()  # Return the extracted text or summary
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import ORJSONResponse
import time
import io
from pypdf import PdfReader
# from loguru import logger
import logging as logger

app = FastAPI()

@app.post('/validate-pdf', response_class=ORJSONResponse, status_code=201)
async def check_pdf(
    file: UploadFile = File(...),
    include_text: bool = False,
    check_text: bool = False,
    include_page_errors: bool = False
):
    response = dict()
    t0 = time.time()

    response["file_name"] = file.filename
    response["content_type"] = file.content_type
    response["file_size"] = file.size
    filters = {
        "include_text": include_text,
        "check_text": check_text
    }

    if file.content_type != "application/pdf":
        message = f"File is not a PDF, but type {file.content_type}"
        logger.error(message)
        response["message"] = message
        return ORJSONResponse(content=response, status_code=400)

    pdf_content = await file.read()
    reader = PdfReader(io.BytesIO(pdf_content))

    if len(reader.pages) == 0:
        message = "The PDF is empty"
        logger.error(message)
        response["message"] = message
        return ORJSONResponse(content=response, status_code=400)

    response["page_count"] = len(reader.pages)

    meta = reader.metadata
    if meta is None:
        message = "The PDF does not contain meta data"
        logger.error(message)
        response["message"] = message
        return ORJSONResponse(content=response, status_code=400)

    cleaned_meta = {k: str(v).replace("\x00", "") for k, v in meta.items()}
    response["meta"] = cleaned_meta

    text = ""
    if check_text:
        results = get_pdf_content(pdf_content=pdf_content)
        text = results["text"]
        if not text.strip():
            message = "The PDF does not contain readable text"
            logger.error(message)
            response["message"] = message
            return ORJSONResponse(content=response, status_code=400)

        common_words = ["the", "and", "is"]
        words_found = [word for word in common_words if word in text]
        if len(words_found) == 0:
            message = "The PDF does not contain readable text, like the word 'the'"
            logger.error(message)
            response["message"] = message
            return ORJSONResponse(content=response, status_code=400)

        response["characters"] = len(text)
        response["words_found"] = words_found
        if include_page_errors:
            response["errors"] = results["errors"]

    if reader.is_encrypted:
        message = "The PDF is encrypted and not allowed"
        logger.error(message)
        response["message"] = message
        return ORJSONResponse(content=response, status_code=400)

    embedded_fonts = []
    for page in tqdm(reader.pages, desc="Finding Fonts"):
        fonts = page.get_fonts()
        for font in fonts:
            font_name = font.get("BaseFont", "").replace("/", "").replace("+", "")
            if font_name not in embedded_fonts:
                embedded_fonts.append(font_name)

    if not embedded_fonts:
        message = "The PDF does not have embedded fonts"
        logger.error(message)
        response["message"] = message
        return ORJSONResponse(content=response, status_code=400)

    response["fonts"] = embedded_fonts
    form_fields = any("/AcroForm" in reader.trailer for _ in reader.pages)
    if form_fields:
        message = "The PDF contains form fields"
        logger.error(message)
        response["message"] = message
        return ORJSONResponse(content=response, status_code=400)

    if include_text:
        response["text"] = text

    t1 = time.time()
    logger.debug(f"PDF check response: {response}")
    response["processing_time_seconds"] = f"{t1 - t0:.2f}"
    return ORJSONResponse(content=response, status_code=201)


# Function to extract data from a PDF file


# coding: utf-8
import io
import re
from functools import lru_cache

# from loguru import logger
import logging as logger  # Import the Loguru logger
from pypdf import PdfReader, PaperSize
from tqdm import tqdm
from unsync import unsync

@unsync
def extract_pdf_text(pdf_content, page_number: int):
    try:
        reader = get_reader(pdf_content)
        page = reader.pages[page_number].extract_text(extraction_mode="layout", layout_mode_strip_rotated=True)
        text = reader.pages[page_number].extract_text()
        box = reader.pages[page_number].mediabox

        print(f"left {box.left}")
        print(f"right {box.right}")
        print(f"lower left {box.lower_left}")
        print(f"lower right {box.lower_right}")
        print(f"upper left {box.upper_left}")
        print(f"upper right {box.upper_right}")
        print(f"top {box.top}")
        print(f"bottom {box.bottom}")

        return {"text": text, "page_num": page_number, "margin": box, "error": None}
    except Exception as ex:
        logger.error(ex)
        return {"text": "", "page_num": page_number, "margin": None, "error": ex}

@lru_cache(maxsize=300, typed=False)
def get_reader(pdf_content):
    reader = PdfReader(io.BytesIO(pdf_content))
    return reader

def is_valid_ssn(ssn):
    ssn_regex = re.compile(r"^(?!000|666)[0-8]\d{2}-(?!00)\d{2}-(?!0000)\d{4}$")
    return bool(ssn_regex.match(ssn))

def get_pdf_content(pdf_content):
    reader = PdfReader(io.BytesIO(pdf_content))

    tasks = [
        extract_pdf_text(pdf_content=pdf_content, page_number=page_number)
        for page_number in tqdm(range(len(reader.pages)), desc="PDF Text Processing")
    ]

    results = [task.result() for task in tqdm(tasks, desc="PDF Text Results")]

    results.sort(key=lambda x: x["page_num"])
    combined_text = "\n".join([result["text"] for result in results])
    has_ssn = is_valid_ssn(combined_text)
    margins = [result["margin"] for result in results]
    error_list = [result for result in results if result["error"] is not None]

    for result in results:
        if result["error"] is not None:
            error_list.append(f"Error on page {result['page_num']} of {result['error']}")

    return {"text": combined_text, "margins": margins, "errors": error_list, "PII": has_ssn}

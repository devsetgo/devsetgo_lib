import fitz  # PyMuPDF
import os
from tqdm import tqdm
import json
from datetime import datetime
from pytz import timezone

def check_interference(page, corner, width, height):
    try:
        page_rect = page.rect
        page_width, page_height = page_rect.width, page_rect.height

        if corner == "top_right":
            x0, y0 = page_width - width, 0
            x1, y1 = page_width, height
        elif corner == "bottom_right":
            x0, y0 = page_width - width, page_height - height
            x1, y1 = page_width, page_height
        else:
            raise ValueError("Invalid corner, can only be top_right or bottom_right")

        check_rect = fitz.Rect(x0, y0, x1, y1)

        text_blocks = page.get_text("dict")["blocks"]
        for block in text_blocks:
            if block["type"] == 0:
                bbox = fitz.Rect(block["bbox"])
                if check_rect.intersects(bbox):
                    return f"Text interference detected in {corner} corner."

        images = page.get_images(full=True)
        for img in images:
            xref = img[0]
            img_rect = fitz.Rect(page.get_image_bbox(xref))
            if check_rect.intersects(img_rect):
                return f"Image interference detected in {corner} corner."

        return None
    except Exception as e:
        return f"Error in processing {corner} {page}: {e}"

def get_margin_by_page(page):
    try:
        page_rect = page.rect
        page_width, page_height = page_rect.width, page_rect.height

        text_blocks = page.get_text("dict")["blocks"]
        text = page.get_text().encode("utf8")

        text_x0, text_y0 = page_width, page_height
        text_x1, text_y1 = 0, 0

        for block in text_blocks:
            if block["type"] == 0:
                bbox = block["bbox"]
                text_x0 = min(text_x0, bbox[0])
                text_y0 = min(text_y0, bbox[1])
                text_x1 = max(text_x1, bbox[2])
                text_y1 = max(text_y1, bbox[3])

        left_margin = text_x0
        right_margin = page_width - text_x1
        top_margin = text_y0
        bottom_margin = page_height - text_y1

        corners = [
            {"corner": "top_right", "width": 144, "height": 36},
            {"corner": "bottom_right", "width": 36, "height": 216},
        ]

        interference = []
        for c in corners:
            inter = check_interference(
                page=page, corner=c["corner"], width=c["width"], height=c["height"]
            )
            if inter and not inter.startswith("Error in"):
                interference.append(f"{c['corner']} {inter}")

        return {
            "left_margin": round(left_margin / 72, 2),
            "right_margin": round(right_margin / 72, 2),
            "top_margin": round(top_margin / 72, 2),
            "bottom_margin": round(bottom_margin / 72, 2),
            "page_text": text,
            "interference": interference,
        }
    except Exception as e:
        print(f"Error processing {page}: {e}")
        return {"error": str(e)}

def run_pdf(pdf_folder, output_folder, safety_margin=0.4):
    dir_list = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")][:200]

    page_count = 0
    document_margins = []
    for pdf_file in tqdm(dir_list, desc="processing file", leave=True):
        document = fitz.open(f"{pdf_folder}/{pdf_file}")

        margin_list = []
        for i in tqdm(range(len(document)), desc=f"processing {pdf_file}", leave=False):
            page = document[i]
            margin_dict = get_margin_by_page(page)
            margin_list.append({"page": i + 1, "margin": margin_dict})
            page_count += 1

        document_margins.append({"file": pdf_file, "margins": margin_list})

    margin_issues = []
    for da in document_margins:
        file_name = da.get("file")
        margin_page_list = []
        for a in da.get("margins"):
            page_number = a.get("page")
            page_margin = a.get("margin")
            warnings = []

            if "interference" in page_margin.items():
                for key, value in page_margin.items():
                    if key.endswith("_margin") and value <= safety_margin:
                        warnings.append(key)

                if page_margin["interference"]:
                    warnings.extend(page_margin["interference"])

            if warnings:
                margin_page_list.append({"page_number": page_number, "issues": warnings})

        if margin_page_list:
            margin_issues.append({"file": file_name, "issues": margin_page_list})

    dt = datetime.now().astimezone(timezone("America/New_York"))
    timestamp = dt.strftime("%Y-%m-%d-%H%M")

    output_path = os.path.join(output_folder, f"margin_issues_{timestamp}.json")
    with open(output_path, "w") as write_file:
        json.dump(margin_issues, write_file)

    print(f"Page count: {page_count} | len(margin_issues): {len(margin_issues)}")

if __name__ == "__main__":
    run_pdf(pdf_folder="/your/pdf/folder/", output_folder="/your/output/folder/")

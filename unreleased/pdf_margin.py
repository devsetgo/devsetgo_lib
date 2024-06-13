import fitz  # PyMuPDF

def get_margins(pdf_path):
    try:
        # Open the PDF file
        document = fitz.open(pdf_path)
        page = document[0]  # Get the first page

        # Get page dimensions
        page_rect = page.rect
        page_width, page_height = page_rect.width, page_rect.height

        # Get text blocks
        text_blocks = page.get_text("dict")["blocks"]

        # Initialize bounding box
        text_x0, text_y0 = page_width, page_height
        text_x1, text_y1 = 0, 0

        # Iterate through text blocks to find the bounding box
        for block in text_blocks:
            if block['type'] == 0:  # block['type'] == 0 indicates a text block
                bbox = block['bbox']
                text_x0 = min(text_x0, bbox[0])
                text_y0 = min(text_y0, bbox[1])
                text_x1 = max(text_x1, bbox[2])
                text_y1 = max(text_y1, bbox[3])

        # Calculate margins
        left_margin = text_x0
        right_margin = page_width - text_x1
        top_margin = text_y0
        bottom_margin = page_height - text_y1

        return {
            "left_margin": left_margin,
            "right_margin": right_margin,
            "top_margin": top_margin,
            "bottom_margin": bottom_margin
        }
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None
# Measure margins for the provided PDF files
pdf_files = ['pdf_sample.pdf', 'pdf_sample_narrow.pdf']
for pdf_file in pdf_files:
    margins = get_margins(pdf_file)
    print(f"Margins for {pdf_file}: {margins}")

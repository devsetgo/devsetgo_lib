import io
from pypdf import PdfReader

pdf_content = open("pdf_sample_narrow.pdf", "rb").read()

reader = PdfReader(io.BytesIO(pdf_content))

print(f"PDF Version {reader.pdf_header}")

parts = []

def visitor_body(text, cm, tm, font_dict, font_size):
    y = cm[5]
    # if y > 50 and y < 720:
    parts.append(text)

for page_number in range(len(reader.pages)):
    try:
        text = reader.pages[page_number].extract_text(visitor_text=visitor_body, layout_mode_scale_weight=1.0)
        mediabox = reader.pages[page_number].mediabox
        cropbox = reader.pages[page_number].cropbox
        trimbox = reader.pages[page_number].trimbox
        artbox = reader.pages[page_number].artbox
        bleedbox = reader.pages[page_number].bleedbox
        unit_size = reader.pages[page_number].user_unit

        print(f"Page {page_number}")
        # print("begin text.....")
        # print(text)
        # print("end text.....")
        print(f"MediaBox: {mediabox.width}x{mediabox.height}  divid by 72 = {mediabox[2] / 72} x {mediabox[3] / 72}")
        print(f"BropBox: {cropbox.width}x{cropbox.height} divid by 72 = {cropbox[2] / 72} x {cropbox[3] / 72}")
        print(f"TrimBox: {trimbox.width}x{trimbox.height} divid by 72 = {trimbox[2] / 72} x {trimbox[3] / 72}")
        print(f"ArtBox: {artbox.width}x{artbox.height} divid by 72 = {artbox[2] / 72} x {artbox[3] / 72}")
        print(f"BleedBox: {bleedbox.width}x{bleedbox.height} divid by 72 = {bleedbox[2] / 72} x {bleedbox[3] / 72}")
        print(f"Unit Size: {unit_size}")

    except Exception as ex:
        print(f"Error on page {page_number}: {ex}")



text_body = "".join(parts)

print(text_body)
for p in parts:
    if len(p) > 100:
        print(len(p),p)

line = "embed code for the video you want to add. You can also type a keyword to search online for the video that best fits"
print(len(line), line)

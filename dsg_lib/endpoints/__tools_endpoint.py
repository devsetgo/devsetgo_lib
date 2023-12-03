# # -*- coding: utf-8 -*-
# import json
# import time
# from enum import Enum
# from typing import List
# from xml.etree import ElementTree

# # Import custom modules
# from email_validator import EmailNotValidError, validate_email, EmailUndeliverableError

# # Import necessary modules
# from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
# from fastapi.responses import ORJSONResponse
# from fastapi.templating import Jinja2Templates
# from loguru import logger  # Import the Loguru logger
# from pydantic import BaseModel, Field
# from xmltodict import parse as xml_parse
# from xmltodict import unparse as xml_unparse

# # Create an instance of APIRouter
# router = APIRouter()
# templates = Jinja2Templates(directory="templates")


# class EmailVerification(BaseModel):
#     email_address: str = Field(
#         ..., description="The email address to be checked", examples=["test@gmail.com"]
#     )
#     check_deliverability: bool = Field(True, description="Check the dns of the domain")
#     test_environment: bool = Field(
#         False, description="Used for test environments to bypass dns check"
#     )


# @router.post(
#     "/email-validation", response_class=ORJSONResponse, status_code=status.HTTP_200_OK
# )
# async def check_email(
#     # email_address: str = Query(...),
#     # check_deliverability: bool = Query(True),
#     # test_environment: bool = Query(False),
#     email_verification: EmailVerification,
# ):
#     t0 = time.time()
#     try:
#         email_data = await validate_email_address(
#             email_address=email_verification.email_address,
#             check_deliverability=email_verification.check_deliverability,
#             test_environment=email_verification.test_environment,
#         )

#         t1 = time.time() - t0

#         if "error" in email_data:
#             return email_data
#         else:
#             email_data["duration_seconds"] = round(t1, 4)
#             data = email_data

#         logger.debug(f"email validation data: {data} {t1:.4f}")
#         # Log a success message
#         logger.info(
#             f"Email validation succeeded for: {email_verification.email_address}"
#         )

#         return data

#     except Exception as e:
#         t1 = time.time() - t0
#         # Log an error message for other exceptions
#         logger.error(
#             f"Error processing email address: {email_verification.email_address}, error: {str(e)}"
#         )

#         raise HTTPException(status_code=500, detail=str(e))


# async def validate_email_address(
#     email_address: str,
#     check_deliverability: bool = True,
#     test_environment: bool = False,
# ):
#     if not email_address:
#         raise HTTPException(status_code=400, detail="Email address is required")

#     try:
#         email_data = validate_email(
#             email_address,
#             check_deliverability=check_deliverability,
#             test_environment=test_environment,
#         )
#         data = {
#             "normalized": email_data.normalized,
#             "valid": True,
#             "local_part": email_data.local_part,
#             "domain": email_data.domain,
#             "ascii_email": email_data.ascii_email,
#             "ascii_local_part": email_data.ascii_local_part,
#             "ascii_domain": email_data.ascii_domain,
#             "smtputf8": email_data.smtputf8,
#             "mx": None if not check_deliverability else email_data.mx,
#             "mx_fallback_type": None
#             if not check_deliverability
#             else email_data.mx_fallback_type,
#         }
#         return data
#     except EmailUndeliverableError as ex:
#         return {
#             "email_address": email_address,
#             "valid": False,
#             "error": f"EmailUndeliverableError '{str(ex)}'",
#         }

#     except EmailNotValidError as ex:
#         return {
#             "email_address": email_address,
#             "valid": False,
#             "error": f"EmailNotValidError '{str(ex)}'",
#         }

#     except Exception as ex:
#         return {
#             "email_address": email_address,
#             "valid": False,
#             "error": f"An Exception for '{str(ex)}' has occured. This could be due to no value is set on the domain.",
#         }


# class FileFormatEnum(str, Enum):
#     json = "json"
#     xml = "xml"
#     # toml = "toml"
#     # yaml = "yaml"


# @router.get("/file-formats", response_model=List[str])
# async def list_file_formats():
#     return [format.value for format in FileFormatEnum]


# # Function to convert XML to JSON with XML format validation
# async def xml_to_json(xml_content: bytes) -> dict:
#     try:
#         # Parse the XML content
#         xml_tree = ElementTree.fromstring(xml_content)

#         # Convert the ElementTree to a string or bytes format if needed
#         # For example, using ElementTree.tostring if your xml_parse expects a string or bytes
#         xml_string = ElementTree.tostring(xml_tree, encoding="utf-8")

#         # Use xml_parse on the string representation of the XML
#         result = xml_parse(
#             xml_string, encoding="utf-8", process_namespaces=True, xml_attribs=True
#         )
#         return result
#     except ElementTree.ParseError:
#         raise HTTPException(status_code=400, detail="Invalid XML format.")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# # Function to convert JSON to XML with JSON format validation
# async def json_to_xml(json_content: bytes) -> str:
#     try:
#         new_dict = json.loads(json_content.decode("utf8"))
#         # continue with your json to xml conversion
#         result = xml_unparse(new_dict, pretty=True)
#         return result
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format.")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# # The main file conversion endpoint
# @router.post("/file-converter", status_code=status.HTTP_201_CREATED)
# async def convert_file(
#     request: Request,
#     convert_from: FileFormatEnum,
#     convert_to: FileFormatEnum,
#     file: UploadFile = File(...),
# ):
#     if convert_from == convert_to:
#         return {"error": "convert_from and convert_to cannot be the same"}

#     # Check if the file type matches the convert_from format
#     filename = file.filename.lower()
#     if convert_from == FileFormatEnum.json and not filename.endswith(".json"):
#         raise HTTPException(status_code=400, detail="Uploaded file is not a JSON file.")
#     elif convert_from == FileFormatEnum.xml and not filename.endswith(".xml"):
#         raise HTTPException(status_code=400, detail="Uploaded file is not an XML file.")

#     file_content = await file.read()

#     # Determine conversion type and perform conversion
#     if convert_from == FileFormatEnum.xml and convert_to == FileFormatEnum.json:
#         conversion_result = await xml_to_json(file_content)
#     elif convert_from == FileFormatEnum.json and convert_to == FileFormatEnum.xml:
#         conversion_result = await json_to_xml(file_content)
#     else:
#         return ORJSONResponse({"error": "Unsupported conversion type"})

#     # return {
#     #     "message": f"File converted successfully from {convert_from} to {convert_to}",
#     #     "result": conversion_result,
#     # }
#     return ORJSONResponse(
#         {
#             "message": f"File converted successfully from {convert_from.value} to {convert_to.value}",
#             "result": conversion_result,
#         }
#     )


# @router.post("/file-converter-html", status_code=status.HTTP_201_CREATED)
# async def convert_file_html(
#     request: Request,
#     convert_from: FileFormatEnum = Form(...),
#     convert_to: FileFormatEnum = Form(...),
#     file: UploadFile = File(...),
# ):
#     data = {"message": None, "result": None, "error": None}

#     # Similar validation as in the JSON endpoint
#     if convert_from == convert_to:
#         return {"error": "convert_from and convert_to cannot be the same"}

#     filename = file.filename.lower()
#     if convert_from == FileFormatEnum.json and not filename.endswith(".json"):
#         raise HTTPException(status_code=400, detail="Uploaded file is not a JSON file.")
#     elif convert_from == FileFormatEnum.xml and not filename.endswith(".xml"):
#         raise HTTPException(status_code=400, detail="Uploaded file is not an XML file.")

#     file_content = await file.read()

#     # Perform conversion
#     if convert_from == FileFormatEnum.xml and convert_to == FileFormatEnum.json:
#         conversion_result = await xml_to_json(file_content)
#     elif convert_from == FileFormatEnum.json and convert_to == FileFormatEnum.xml:
#         conversion_result = await json_to_xml(file_content)
#     else:
#         data["error"] = {"error": "Unsupported conversion type"}

#     # Assume conversion_result is your JSON data
#     if isinstance(conversion_result, dict):  # Check if the result is a JSON object
#         formatted = json.dumps(conversion_result, indent=4)  # Pretty print the JSON
#     else:
#         formatted = conversion_result  # If not JSON, use the original data

#     if data["error"] is not None:
#         data["message"] = "there has been an error"

#     else:
#         # Pass the result to the Jinja2 template
#         data = {
#             "message": f"File converted successfully from {convert_from.value} to {convert_to.value}",
#             "result": formatted,
#         }
#     return templates.TemplateResponse(
#         "file-converter-response.html", {"request": request, "data": data}
#     )

# @router.get("/email-validation", response_class=HTMLResponse)
# async def email_validation(request: Request):
#     data = []
#     return templates.TemplateResponse(
#         "email-check.html",
#         {"request": request, "data": data},
#     )


# @router.post("/email-validation", response_class=HTMLResponse)
# async def email_validation_response(request: Request):
#     t0 = time.time()

#     from src.api.tools import validate_email_address

#     form = await request.form()

#     logger.debug(f"request form data: {dict(form)}")

#     if form.get("check_deliverability") is None:
#         check_deliverability = False
#     elif form.get("check_deliverability") == "on":
#         check_deliverability = True

#     data = await validate_email_address(
#         email_address=form.get("email"),
#         check_deliverability=check_deliverability,
#     )

#     logger.info(f"email validation response: {data}")
#     t1 = time.time() - t0

#     data["duration_seconds"] = round(t1, 4)
#     logger.debug(data)
#     return templates.TemplateResponse(
#         "email-check-response.html",
#         {"request": request, "data": data},
#     )


# @router.get("/file-converter", response_class=HTMLResponse)
# async def file_convert(request: Request):
#     data = []
#     return templates.TemplateResponse(
#         "file-converter.html",
#         {"request": request, "data": data},
#     )


# email_check_html = """
# {% extends "base.html" %}
# {% block page_stylesheet %}
# <!-- Add page level stylesheets below -->
# <!-- <link href="https://cdn.jsdelivr.net/npm/simple-datatables@latest/dist/style.css" rel="stylesheet" /> -->
# <!-- End page level stylesheets -->
# {% endblock %}
# {% block body %}
# <!-- Main Section -->
# <main>
#     <div class="container-fluid px-4">
#         <div class="row">
#             <div class="col-md-8">
#                 <div class="container">
#                     <h1 class="mt-4">Email Validation</h1>
#                     <ol class="breadcrumb mb-4">
#                         <li class="breadcrumb-item active">Tools > Email Validation</li>
#                     </ol>
#                 </div>
#             </div>
#             <!-- <div class="col-md-4">
#                 <div class="container text-right">
#                     <span class="htmx-indicator">
#                         <img width='300' src="/static/img/loading_two.gif" title="Let me check on this!!!"/>
#                     </span>
#                 </div>
#             </div> -->
#         </div>
#     </div>
#     <div class="row">
#         <!-- First Column -->
#         <div class="col-md-4">
#             <div class="p-3 border bg-light">
#                 <form id="emailValidationForm" hx-post="/pages/email-validation" hx-target="#response" hx-indicator=".htmx-indicator" hx-trigger="submit">
#                     <label for="email_address">Enter an email:</label><br>
#                     <input type="text" id="email_address" name="email" required><br>
#                     <label for="check_deliverability">Check Deliverability:</label>
#                     <input type="checkbox" role="switch" id="check_deliverability" name="check_deliverability" checked><br>
#                     <button type="submit" id="submitBtn" title="Timeout at 15 seconds">Submit</button>
#                     <button id="loadingBtn" class="btn btn-primary" style="display:none;" hx-swap-oob="true" title="Timeout at 15 seconds">
#                         <span class="spinner-border spinner-border-sm"></span>
#                         Validating...
#                     </button>
#                 </form>
#                 <script>
#                     document.getElementById('emailValidationForm').addEventListener('submit', function() {
#                         document.getElementById('response').innerHTML = ''; // Clear the response div
#                         document.getElementById('submitBtn').style.display = 'none';
#                         document.getElementById('loadingBtn').style.display = '';
#                     });

#                     document.body.addEventListener('htmx:afterSwap', function(event) {
#                         if (event.detail.target.id === 'response') {
#                             document.getElementById('submitBtn').style.display = '';
#                             document.getElementById('loadingBtn').style.display = 'none';
#                         }
#                     });

#                     document.body.addEventListener('htmx:requestError', function(event) {
#                         // Handle HTMX request errors here
#                         // For example, show an error message to the user
#                         document.getElementById('submitBtn').style.display = '';
#                         document.getElementById('loadingBtn').style.display = 'none';
#                     });
#                 </script>
#             </div>
#         </div>
#         <!-- Second Column -->
#         <div class="col-md-7">
#             <div class="p-3 border bg-light">
#                 <div id="response">
#                 </div>
#             </div>
#         </div>
#     </div>
# </main>
# <!-- End Main Section -->
# {% endblock %}
# {% block page_scripts %}
# <!-- Begin Page Scripts -->
# <!-- End Page Scripts -->
# {% endblock %}

# """

# email_check_html_response = """
# <h3>Email Data</h3>
# <ul>
# {% for key, value in data.items() %}
#     {% if key in ['domain', 'ascii_domain'] and value %}
#         <li><strong>{{ key|capitalize }}</strong>: <a href="https://dnschecker.org/all-dns-records-of-domain.php?query={{ value }}&rtype=ALL&dns=google" target="_blank" title="See DNS record for domain">{{ value }}</a></li>
#     {% elif key in ['mx'] and value %}
#         <li><strong>{{ key|capitalize }}</strong>:
#             <ul>
#                 {% for mx_record in value %}
#                     <li><strong>Priority:</strong> {{ mx_record[0] }}, <strong>Server:</strong> {{ mx_record[1] }}</li>
#                 {% endfor %}
#             </ul>
#         </li>
#     {% elif key == 'valid' %}
#         <li><strong>{{ key|capitalize }}</strong>: <span style="font-weight: bold; color: {{ 'green' if value else 'red' }}">{{ value }}</span></li>
#     {% else %}
#         <li><strong>{{ key|capitalize }}</strong>: {{ value }}</li>
#     {% endif %}
# {% endfor %}
# </ul>

#  """

# file_converter_html = """
# {% extends "base.html" %}
# {% block page_stylesheet %}
# <link href="https://cdn.jsdelivr.net/npm/simple-datatables@latest/dist/style.css" rel="stylesheet" />
# <style>
#     .code-container {
#         overflow-x: auto;
#         /* Adds horizontal scrollbar if needed */
#         word-wrap: break-word;
#         /* Ensures long lines are wrapped */
#         white-space: pre-wrap;
#         /* Wraps text without breaking code formatting */
#         max-height: 500px;
#         /* Maximum height before vertical scrolling */
#     }
# </style>
# {% endblock %}

# {% block body %}
# <!-- Main Section -->

# <main>
#     <div class="container-fluid px-4">
#         <div class="row">
#             <div class="col-md-6">
#                 <div class="container">
#                     <h1 class="mt-4">File Converter</h1>
#                     <ol class="breadcrumb mb-4">
#                         <li class="breadcrumb-item active">Tools > File Converter</li>
#                     </ol>
#                 </div>
#             </div>
#             <!-- <div class="col-md-6">
#                 <div class="container text-right">
#                     <span class="htmx-indicator">
#                         <img width='200' src="/static/img/loading.gif" /> Loading...
#                     </span>
#                 </div>
#             </div> -->
#         </div>
#         <div class="row">
#             <!-- First Column -->
#             <div class="col-md-3">
#                 <!-- <form id="fileConversion" hx-post="/api/tools/v1/file-converter-html" hx-encoding="multipart/form-data"
#                     hx-target="#result" hx-indicator=".htmx-indicator"> -->
#                 <form id="fileConversion" hx-post="/api/tools/v1/file-converter-html" hx-encoding="multipart/form-data"
#                     hx-target="#result" hx-indicator=".htmx-indicator" hx-trigger="submit">

#                     <label for="convert_from">Convert From:</label>
#                     <select name="convert_from" id="convert_from">
#                         <option value="json">JSON</option>
#                         <option value="xml">XML</option>
#                     </select>
#                     <br>
#                     <label for="convert_to">Convert To:</label>
#                     <select name="convert_to" id="convert_to">
#                         <option value="json">JSON</option>
#                         <option value="xml">XML</option>
#                     </select>
#                     <br>
#                     <label for="file">File:</label>
#                     <input type="file" id="file" name="file" required>
#                     <br>
#                     <!-- <button type="submit">Convert</button> -->
#                     <button type="submit" id="convertBtn">Convert</button>
#                     <button id="loadingConvertBtn" class="btn btn-primary" style="display:none;" hx-swap-oob="true">
#                         <span class="spinner-border spinner-border-sm"></span>
#                         Converting file...
#                     </button>
#                 </form>
#                 <script>
#                     document.getElementById('fileConversion').addEventListener('submit', function () {
#                         document.getElementById('convertBtn').style.display = 'none';
#                         document.getElementById('loadingConvertBtn').style.display = '';
#                     });

#                     document.body.addEventListener('htmx:afterSwap', function (event) {
#                         if (event.detail.target.id === 'result') {
#                             document.getElementById('convertBtn').style.display = '';
#                             document.getElementById('loadingConvertBtn').style.display = 'none';
#                         }
#                     });
#                 </script>
#             </div>
#             <!-- Second Column -->
#             <div class="col-md-9">
#                 <div class="p-3 border bg-light">
#                     <div id="result"></div>
#                 </div>
#             </div>
#         </div>
#     </div>
# </main>

# <!-- End Main Section -->
# {% endblock %}
# {% block page_scripts %}
# <!-- Begin Page Scripts -->

# <!-- End Page Scripts -->

# {% endblock %}
# """

# file_converter_html_response = """
# <div class="card">
#     <div class="card-body">
#         <!-- Displaying the message -->
#         <h5 class="card-title">Conversion Result</h5>
#         <p class="card-text">{{ data.message }}</p>

#         <!-- Displaying the formatted result -->
#         <pre class="code-container"><code id="codeContent">{{ data.result | escape }}</code></pre>

#         <!-- Button to trigger copy -->
#         <button onclick="copyToClipboard()">Copy</button>
#     </div>
# </div>

# <script>
#     function copyToClipboard() {
#         // Get the text from the <code> element
#         var codeText = document.getElementById('codeContent').innerText;

#         // Create a temporary textarea element to hold the text
#         var textArea = document.createElement("textarea");
#         textArea.value = codeText;

#         // Add the textarea to the document
#         document.body.appendChild(textArea);

#         // Select the text
#         textArea.select();
#         // Removed setSelectionRange, as select() should select all text

#         // Copy the text inside the textarea
#         try {
#             var successful = document.execCommand("copy");
#             var msg = successful ? 'successful' : 'unsuccessful';
#             console.log('Copying text command was ' + msg);
#             alert("Copied to clipboard!");
#         } catch (err) {
#             console.error('Oops, unable to copy', err);
#         }

#         // Remove the textarea from the document
#         document.body.removeChild(textArea);
#     }
# </script>

#  """

# loading_bar_snippet = """
#     <!-- Flex container to align items -->
#     <div style="display: flex; justify-content: flex-end; align-items: center; width: 100%;">
#         <!-- HTMX Indicator aligned to the right -->
#         <span class="htmx-indicator" style="margin-right: 10px;">
#             <img width='200' src="/static/img/loading_bar_1.gif" title="Let me check on this!!!" />
#         </span>
#     </div>
#      """
# # -*- coding: utf-8 -*-

# import psutil
# from loguru import logger


# async def get_processes() -> list:
#     """
#     Get running processes and filter by python processes
#     Returns:
#         dict -- [pid, name, username]
#     """
#     result = []
#     proc = psutil.process_iter(attrs=["pid", "name", "username"])
#     process_check = ["python", "python3", "gunicorn", "uvicorn", "hypercorn", "daphne"]

#     for p in proc:
#         if p.info["name"] in process_check:
#             result.append(p.info)

#     logger.debug(result)
#     return result

# -*- coding: utf-8 -*-

# Import necessary modules
import io
import tempfile
import time
from typing import Dict, List, Optional, Union
import json

from email_validator import EmailNotValidError, EmailUndeliverableError, validate_email
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import (
    HTMLResponse,
    ORJSONResponse,
    StreamingResponse,
    FileResponse,
)
from fastapi.templating import Jinja2Templates
from jinja2 import Template

# Importing database connector module
# from loguru import logger
import logging as logger

from dsg_lib._converters import (
    FileFormatEnum,
    convert_file_format,
    create_example_json,
)
from dsg_lib.email_functions import validate_email_address
from dsg_lib.http_codes import generate_code_dict
from dsg_lib.models import EmailValidationResponse, EmailVerification


def create_tool_router(config: dict):
    """
    Creates a FastAPI router based on the provided configuration.

    The configuration can enable or disable certain endpoints. Currently, it supports enabling/disabling the email-validation endpoint.

    Args:
        config (dict): A dictionary containing the configuration.
                       Example: {"enable_email-validation": True}

    Returns:
        fastapi.routers.APIRouter: A FastAPI router with the configured endpoints.

    Example:
        config = {"enable_email-validation": True}
        tool_router = create_tool_router(config)
        app.include_router(tool_router, prefix="/api/tools", tags=["system-tools"])
    """

    # Store the start time of the application
    time.time()

    router = APIRouter()
    if config.get("enable_email_validation", True):
        model_content = {
            "model": dict,
            "content": {
                "application/json": {
                    "example": {
                        "message": "Example message",
                        "information": 'None or {"normalized": "email_address", "valid": True, "local_part": \
                        "local_part", "domain": "domain", "ascii_email": "ascii_email", "ascii_local_part":\
                        "ascii_local_part", "ascii_domain": "ascii_domain", "smtputf8": True, "mx": None,\
                        "mx_fallback_type": None}',
                        "error": "True or False",
                        "timer": 0.0023,
                    }
                }
            },
        }
        status_response = generate_code_dict(
            [400, 405, 422, 500], description_only=False
        )
        # Iterate over all status codes
        for code in status_response:
            # Update the status code dictionary
            status_response[code].update(model_content)  # type: ignore

        @router.post(
            "/email-validation",
            response_class=ORJSONResponse,
            status_code=status.HTTP_200_OK,
            responses=status_response,
            response_model=EmailValidationResponse,
        )
        async def check_email(
            email_verification: EmailVerification,
        ):
            t0 = time.time()

            email_data = await validate_email_address(
                email_address=email_verification.email_address,
                # check_deliverability=email_verification.check_deliverability,
                # test_environment=email_verification.test_environment,
            )
            t1 = time.time() - t0

            if email_data["error"]:
                logger.error(
                    f"Error processing email address: {email_verification.email_address}, error: {email_data['message']}"
                )
                raise HTTPException(status_code=400, detail=email_data["message"])

            logger.debug(f"email validation data: {email_data} {t1:.4f}")
            logger.info(
                f"Email validation succeeded for: {email_verification.email_address}"
            )

            email_data["timer"] = round(t1, 4)
            return email_data

    if config.get("enable_file_conversion", True):
        status_response = generate_code_dict(
            [400, 405, 422, 500], description_only=False
        )

        @router.get(
            "/file-formats", response_model=List[str], responses=status_response
        )
        async def list_file_formats():
            logger.info("Request received to list all available file formats")

            try:
                file_formats = [format.value for format in FileFormatEnum]
                logger.info(f"Available file formats: {file_formats}")

                return file_formats

            except Exception as e:
                error_message = f"Error in listing file formats: {str(e)}"
                logger.error(error_message)
                raise HTTPException(status_code=500, detail=error_message)

        # TODO: Add a background task for large files. See https://fastapi.tiangolo.com/tutorial/background-tasks/
        # TODO: Add a cleanup process to clear files from the temp directory after a certain time period

        @router.post("/file-converter", status_code=status.HTTP_200_OK)
        async def convert_file_api(
            convert: FileFormatEnum = Form(...), file: UploadFile = File(...)
        ) -> StreamingResponse:
            """
            Asynchronous API endpoint to convert files from one format to another.

            This function receives a file and a target format, performs the conversion,
            and returns the converted file. The conversion process is logged with its duration
            and the size of the converted file.

            Parameters:
            convert (FileFormatEnum): The target file format for conversion, received via form data.
            file (UploadFile): The file to be converted, received as an upload.

            Returns:
            StreamingResponse: A response object that streams the converted file back to the client.
            """

            # Record the start time for logging duration of the process
            t0 = time.time()

            # Read the content of the uploaded file
            file_content = await file.read()
            # Get the size of the file in bytes
            original_file_size = len(file_content)

            if original_file_size > 1000000:
                print(original_file_size)

            # Perform conversion using the specified format
            conversion_result = await convert_file_format(
                conversion_type=convert, content=file_content
            )

            # Convert the conversion result to bytes if it's not already in bytes format
            if isinstance(conversion_result, str):
                conversion_result_bytes = conversion_result.encode("utf-8")
            else:
                conversion_result_bytes = conversion_result

            # Create a file-like object from the conversion result bytes
            result_file = io.BytesIO(conversion_result_bytes)
            # Set the file name using the desired output format
            result_file.name = f"converted_file.{convert.value.split(' to ')[-1]}"

            # Calculate the size of the converted file for logging and response headers
            file_size = result_file.getbuffer().nbytes

            # Calculate the total processing time
            t1 = time.time() - t0
            # Log the processing time and file size
            logger.info(
                f"File converted from {convert.value} in {t1:.4f} seconds, file size: {file_size} bytes"
            )

            # Create a StreamingResponse to send the converted file back to the client
            return StreamingResponse(
                result_file,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={result_file.name}",
                    "Content-Length": str(file_size),
                },
            )

        @router.get("/example-json")
        async def get_example_json(qty: int = 10) -> StreamingResponse:
            logger.info(
                f"Request received to generate example JSON with quantity: {qty}"
            )

            try:
                # Generate example JSON data
                data = await create_example_json(qty=qty)
                logger.debug(f"Generated example JSON data: {data}")

                # Convert the JSON data to a string
                data_str = json.dumps(data)

                # Convert the JSON string to bytes
                data_bytes = data_str.encode("utf-8")

                # Create a file-like object from the data bytes
                result_file = io.BytesIO(data_bytes)
                # Set the file name
                result_file.name = "example_data.json"

                # Calculate the size of the file for response headers
                file_size = result_file.getbuffer().nbytes

                logger.info("Returning file response with generated JSON data")
                return StreamingResponse(
                    result_file,
                    media_type="application/octet-stream",  # Change this line
                    headers={
                        "Content-Disposition": f"attachment; filename={result_file.name}",
                        "Content-Length": str(file_size),
                    },
                )

            except Exception as e:
                logger.error(f"Error encountered in get_example_json: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    # return router back to main fastapi application
    return router


#     # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# if email validation html pages
# if config.get("enable_email_validation_form", False):

#     @router.get("/email-validation-form", response_class=HTMLResponse)
#     async def email_validation_form(
#         request: Request, post_endpoint: str = "/api/tools/email-validation-form"
#     ):
#         email_validation_form = f"""
#         <!-- Begin Email Validation Form -->
#         <div class="row">
#         <!-- First Column -->
#         <div class="col-md-4">
#             <div class="p-3 border bg-light">
#                 <form id="emailValidationForm" hx-post="{post_endpoint}" hx-target="#response" hx-indicator=".htmx-indicator" hx-trigger="submit">
#                     <label for="email_address">Enter an email:</label><br>
#                     <input type="email" id="email_address" name="email" required><br>
#                     <label for="check_deliverability">Check Deliverability:</label>
#                     <input type="checkbox" role="switch" id="check_deliverability" name="check_deliverability" checked><br>
#                     <button class="btn btn-primary" type="submit" id="submitBtn" title="Timeout at 15 seconds">Submit</button>
#                     <button id="loadingBtn" class="btn btn-primary" style="display:none;" hx-swap-oob="true" title="Timeout at 15 seconds">
#                         <span class="spinner-border spinner-border-sm"></span>
#                         Validating...
#                     </button>

#                 </form>
#                 <script>
#                     document.getElementById('emailValidationForm').addEventListener('submit', function() {{
#                         document.getElementById('response').innerHTML = ''; // Clear the response div
#                         document.getElementById('submitBtn').style.display = 'none';
#                         document.getElementById('loadingBtn').style.display = '';
#                     }});

#                     document.body.addEventListener('htmx:afterSwap', function(event) {{
#                         if (event.detail.target.id === 'response') {{
#                             document.getElementById('submitBtn').style.display = '';
#                             document.getElementById('loadingBtn').style.display = 'none';
#                         }}
#                     }});

#                     document.body.addEventListener('htmx:requestError', function(event) {{
#                         // Handle HTMX request errors here
#                         // For example, show an error message to the user
#                         document.getElementById('submitBtn').style.display = '';
#                         document.getElementById('loadingBtn').style.display = 'none';
#                     }});
#                 </script>
#                 </div>
#             </div>
#             <!-- Second Column -->
#             <div class="col-md-7">
#                 <div class="p-3 border bg-light">
#                     <div id="response"></div>
#                 </div>
#             </div>
#         </div>
#         <!-- End Email Validation Form -->
#         """
#         return HTMLResponse(content=email_validation_form, status_code=200)

#     @router.post("/email-validation-form", response_class=HTMLResponse)
#     async def email_validation_response(request: Request):
#         t0 = time.time()

#         form = await request.form()

#         logger.debug(f"request form data: {dict(form)}")

#         if form.get("check_deliverability") is None:
#             check_deliverability = False
#         elif form.get("check_deliverability") == "on":
#             check_deliverability = True

#         data = await validate_email_address(
#             email_address=form.get("email"),
#             check_deliverability=check_deliverability,
#         )

#         logger.info(f"email validation response: {data}")
#         t1 = time.time() - t0

#         data["duration_seconds"] = round(t1, 4)
#         logger.debug(f"Email validation response: {data}")
#         email_validation_form_response = """
#         <!-- Begin Email Validation Response -->
#         <ul>
#         {% for key, value in data.items() %}
#             {% if key == 'information' and value is not none %}
#                 <li><strong>{{ key|capitalize }}</strong>:
#                     <ul>
#                         {% for info_key, info_value in value.items() %}
#                             {% if info_key == 'mx' %}
#                                 <li><strong>{{ info_key|capitalize }}</strong>:
#                                     <ul>
#                                         {% for mx_record in info_value %}
#                                             <li><strong>Priority:</strong> {{ mx_record[0] }}, <strong>Address:</strong> {{ mx_record[1] }}</li>
#                                         {% endfor %}
#                                     </ul>
#                                 </li>
#                             {% else %}
#                                 <li><strong>{{ info_key|capitalize }}</strong>: {{ info_value }}</li>
#                             {% endif %}
#                         {% endfor %}
#                     </ul>
#                 </li>
#             {% elif key in ['domain', 'ascii_domain'] and value %}
#                 <li><strong>{{ key|capitalize }}</strong>: {{value}}</li>
#             {% elif key == 'dns_check' and value %}
#                 <li><strong>{{ key|capitalize }}</strong>: <a href="{{ value }}" target="_blank">DNS Check</a></li>
#             {% elif key in ['mx'] and value %}
#                 <li><strong>{{ key|capitalize }}</strong>:
#                     <ul>
#                         {% for mx_record in value %}
#                             <li><strong>Priority:</strong> {{ mx_record[0] }}, <strong>Server:</strong> {{ mx_record[1] }}</li>
#                         {% endfor %}
#                     </ul>
#                 </li>
#             {% elif key == 'valid' %}
#                 <li><strong>{{ key|capitalize }}</strong>: <span style="font-weight: bold; color: {{ 'green' if value else 'red' }}">{{ value }}</span></li>
#             {% else %}
#                 <li><strong>{{ key|capitalize }}</strong>: {{ value }}</li>
#             {% endif %}
#         {% endfor %}
#         </ul>
#         <!-- End Email Validation Response -->
#         """

#         template = Template(email_validation_form_response)
#         rendered_template = template.render(data=data)

#         return HTMLResponse(content=rendered_template)

#     @router.get("/email-validation-demo", response_class=HTMLResponse)
#     async def email_validation_demo():
#         html_content = """
#         <!DOCTYPE html>
#         <html lang="en">
#         <head>
#             <title>Bootstrap Example</title>
#             <meta charset="utf-8" />
#             <meta name="viewport" content="width=device-width, initial-scale=1" />
#             <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
#             <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>

#             <!-- Required for form use -->
#             <script src="https://unpkg.com/htmx.org@1.6.1"></script>
#             <script src="https://unpkg.com/htmx.org@1.6.1"></script>
#         </head>
#         <body>
#             <div class="jumbotron text-center">
#             <h2>Email Validation Form and Response Demo</h2>
#             <p>Resize this responsive page to see the effect!</p>
#             </div>

#             <div class="container">
#             <div
#                 id="emailValidationForm"
#                 hx-get="/api/tools/email-validation-form"
#                 hx-trigger="load"
#             >
#                 <!-- The email validation form will be loaded here -->
#             </div>
#             <div class="row mt-4">
#                 <div class="col-md-7">
#                 </div>
#             </div>
#             </div>
#         </body>
#         </html>
#         """
#         return HTMLResponse(content=html_content, status_code=200)


#     # # app route /api/v1/tools
#     # @router.post("/xml-json")
#     # async def convert_xml(
#     #     myfile: UploadFile = File(...),
#     # ) -> dict:
#     #     """
#     #     convert xml document to json

#     #     Returns:
#     #         json object
#     #     """

#     #     # determine if file has no content_type set
#     #     # set file_type to a value
#     #     if len(myfile.content_type) == 0:
#     #         file_type = "unknown"
#     #     else:
#     #         file_type = myfile.content_type

#     #     logger.info(f"file_name: {myfile.filename} file_type: {file_type}")

#     #     file_named = myfile.filename
#     #     # if document is not a xml document, give http exception
#     #     if file_named.endswith(".xml", 4) is not True:
#     #         error_exception = f"API requires a XML docuement, but file {myfile.filename} is {file_type}"
#     #         logger.error(error_exception)
#     #         raise HTTPException(status_code=400, detail=error_exception)

#     #     try:
#     #         # async method to get data from file upload
#     #         contents = await myfile.read()
#     #         # xml to json conversion with xmltodict
#     #         result = xml_parse(
#     #             contents, encoding="utf-8", process_namespaces=True, xml_attribs=True
#     #         )
#     #         logger.info("file converted to JSON")
#     #         return result

#     #     except Exception as e:
#     #         logger.error(f"error: {e}")
#     #         err = str(e)
#     #         # when error occurs output http exception
#     #         if err.startswith("syntax error") is True or e is not None:
#     #             error_exception = f"The syntax of the object is not valid. Error: {e}"
#     #             raise HTTPException(status_code=400, detail=error_exception)

#     # # app route /api/v1/tools
#     # @router.post("/json-xml")
#     # async def convert_json(
#     #     myfile: UploadFile = File(...),
#     # ) -> str:
#     #     """
#     #     convert json document to xml

#     #     Returns:
#     #         XML object
#     #     """

#     #     # determine if file is of zero bytes
#     #     # set file_type to a value
#     #     if len(myfile.content_type) == 0:
#     #         file_type = "unknown"
#     #     else:
#     #         file_type = myfile.content_type

#     #     logger.info(f"file_name: {myfile.filename} file_type: {file_type}")

#     #     file_named = myfile.filename
#     #     # if document is not a json document, give http exception
#     #     if file_named.endswith(".json", 5) is not True:
#     #         error_exception = f"API requirs a JSON docuement, but file {myfile.filename} is {file_type}"
#     #         logger.error(error_exception)
#     #         raise HTTPException(status_code=400, detail=error_exception)

#     #     try:
#     #         # async method to get data from file upload
#     #         content = await myfile.read()
#     #         # create a dictionary with decoded content
#     #         new_dict = json.loads(content.decode("utf8"))
#     #         # xml to json conversion with xmltodict
#     #         result = xml_unparse(new_dict, pretty=True)
#     #         logger.info("file converted to JSON")
#     #         return result

#     #     except Exception as e:
#     #         logger.error(f"error: {e}")
#     #         err = str(e)
#     #         # when error occurs output http exception
#     #         if err.startswith("Extra data") is True or e is not None:
#     #             error_exception = f"The syntax of the object is not valid. Error: {e}"
#     #             raise HTTPException(status_code=400, detail=error_exception)

#     # # app route /api/v1/tools
#     # @router.get("/database_type/")
#     # async def database_type():
#     #     async with AsyncDatabase().get_db_session() as session:
#     #         try:
#     #             # Check for PostgreSQL
#     #             result = await session.execute(text("SELECT version();"))
#     #             if "PostgreSQL" in result.scalar():
#     #                 return {"database_type": "PostgreSQL"}

#     #             # Check for MySQL
#     #             result = await session.execute(text("SELECT VERSION();"))
#     #             if "MySQL" in result.scalar():
#     #                 return {"database_type": "MySQL"}

#     #             # Check for SQLite
#     #             result = await session.execute(text("SELECT sqlite_version();"))
#     #             if (
#     #                 result.scalars().first() is not None
#     #             ):  # SQLite will return a version number
#     #                 return {"database_type": "SQLite"}

#     #             # Check for Oracle
#     #             result = await session.execute(
#     #                 text("SELECT * FROM v$version WHERE banner LIKE 'Oracle%';")
#     #             )
#     #             if "Oracle" in result.scalars().first():
#     #                 return {"database_type": "Oracle"}

#     #         except Exception as e:
#     #             return {"error": str(e)}

#     # # app route /api/v1/tools
#     # @router.get("/database_dialect/")
#     # async def database_dialect():
#     #     async with AsyncDatabase().engine.begin() as conn:
#     #         dialect = await conn.run_sync(lambda conn: inspect(conn).dialect.name)
#     #     return {"database_type": dialect}

#     # # app route /api/v1/tools
#     # @router.get("/config")
#     # async def get_config():
#     #     return settings.dict()

#     async def validate_email_address(
#         email_address: str,
#         check_deliverability: bool = True,
#         test_environment: bool = False,
#     ):
#         if not email_address:
#             raise HTTPException(status_code=400, detail="Email address is required")

#         try:
#             email_data = validate_email(
#                 email_address,
#                 check_deliverability=check_deliverability,
#                 test_environment=test_environment,
#             )
#             data = {
#                 "normalized": email_data.normalized,
#                 "valid": True,
#                 "local_part": email_data.local_part,
#                 "domain": email_data.domain,
#                 "ascii_email": email_data.ascii_email,
#                 "ascii_local_part": email_data.ascii_local_part,
#                 "ascii_domain": email_data.ascii_domain,
#                 "smtputf8": email_data.smtputf8,
#                 "mx": None if not check_deliverability else email_data.mx,
#                 "mx_fallback_type": None
#                 if not check_deliverability
#                 else email_data.mx_fallback_type,
#             }
#             return data
#         except EmailUndeliverableError as ex:
#             return {
#                 "email_address": email_address,
#                 "valid": False,
#                 "error": f"EmailUndeliverableError '{str(ex)}'",
#             }

#         except EmailNotValidError as ex:
#             return {
#                 "email_address": email_address,
#                 "valid": False,
#                 "error": f"EmailNotValidError '{str(ex)}'",
#             }

#         except Exception as ex:
#             return {
#                 "email_address": email_address,
#                 "valid": False,
#                 "error": f"An Exception for '{str(ex)}' has occured. This could be due to no value is set on the domain.",
#             }

#     html = """
#     <!--- Begin Return HTML for email validation --->
#     <ul>
#     {% for key, value in data.items() %}
#         {% if key in ['domain', 'ascii_domain'] and value %}
#             <li><strong>{{ key|capitalize }}</strong>: <a href="https://dnschecker.org/all-dns-records-of-domain.php?query={{ value }}&rtype=ALL&dns=google" target="_blank" title="See DNS record for domain">{{ value }}</a></li>
#         {% elif key in ['mx'] and value %}
#             <li><strong>{{ key|capitalize }}</strong>:
#                 <ul>
#                     {% for mx_record in value %}
#                         <li><strong>Priority:</strong> {{ mx_record[0] }}, <strong>Server:</strong> {{ mx_record[1] }}</li>
#                     {% endfor %}
#                 </ul>
#             </li>
#         {% elif key == 'valid' %}
#             <li><strong>{{ key|capitalize }}</strong>: <span style="font-weight: bold; color: {{ 'green' if value else 'red' }}">{{ value }}</span></li>
#         {% else %}
#             <li><strong>{{ key|capitalize }}</strong>: {{ value }}</li>
#         {% endif %}
#     {% endfor %}
#     </ul>
#     <!--- End Return HTML for email validation --->
#     """


# import time
# # import tracemalloc

# from fastapi import APIRouter, HTTPException, status
# from fastapi.responses import ORJSONResponse

# from dsg_lib.http_codes import generate_code_dict

# # Importing database connector module
# from loguru import logger

# # from loguru import logger
import logging as loggernfig: dict):

#     router = APIRouter()

#     # if config.get("enable_email-validation", True):
#     #     @router.get(
#     #         "/status",
#     #         tags=["system-health"],
#     #         status_code=status.HTTP_200_OK,
#     #         # response_class=ORJSONResponse,
#     #         # responses=status_response,
#     #     )
#     #     async def health_status():
#     #         """
#     #         GET status, uptime, and current datetime

#     #         Returns:
#     #             dict -- [status: UP, uptime: seconds current_datetime: datetime.now]
#     #         """
#     #         # Log the status request
#     #         logger.info("Health status of up returned")
#     #         # Return a dictionary with the status of the application
#     #         return {"status": "UP"}

#     @router.get(
#             "/foo",
#             tags=["system-health"],
#             status_code=status.HTTP_200_OK,
#             # response_class=ORJSONResponse,
#             # responses=status_response,
#         )
#     async def foo():
#         """
#         GET status, uptime, and current datetime

#         Returns:
#             dict -- [status: UP, uptime: seconds current_datetime: datetime.now]
#         """
#         # Log the status request
#         logger.info("Health status of up returned")
#         # Return a dictionary with the status of the application
#         return {"status": "UP"}

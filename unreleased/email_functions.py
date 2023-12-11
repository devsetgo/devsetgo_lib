# -*- coding: utf-8 -*-

"""
email_functions.py

This module contains a function for validating email addresses. It checks the
validity of the email format, and optionally checks for deliverability by
looking up the MX records of the email's domain. It also provides detailed
information about the email address and logs the process.
"""

# Import the time module to measure how long the email validation takes
import time

# Import the validate_email function and the necessary exceptions from the email_validator module
from email_validator import EmailNotValidError, EmailUndeliverableError, validate_email

# Import the logger from the loguru module for logging
from loguru import logger

# TODO: Require FastAPI, email-validator and other required libraries
#       https://github.com/pydantic/pydantic/blob/fd0dfffffcb5c4543e18d0ad428bb4f6fffa3fb4/pydantic/networks.py#L375


async def validate_email_address(
    email_address: str,
    check_deliverability: bool = True,
    test_environment: bool = False,
):
    """
    This function validates an email address.

    Parameters:
    email_address (str): The email address to validate.
    check_deliverability (bool): If True, checks whether the email address is deliverable.
    test_environment (bool): If True, runs the function in a test environment.

    Returns:
    dict: A dictionary containing information about the email address and any validation errors.
    """

    # Check if the email_address parameter is a string
    if isinstance(email_address, str) is False:
        raise ValueError("Email address must be a string")

    # Log the start of the email validation
    logger.debug(f"Validating email address: {email_address}")

    # Initialize a dictionary to store the validation results
    data = {
        "message": None,  # Will store any error messages
        "information": None,  # Will store information about the email address
        "dns_check": None,  # Will store a link to check the DNS records of the email domain
        "error": False,  # Will be set to True if there are any validation errors
    }

    # Check if the email_address parameter is not empty
    if not email_address:
        data["message"] = "Email address is required"
        data["error"] = True
        logger.warning("Email address is required")
        return data

    # Extract the domain from the email address
    domain = email_address.split("@")[1]

    # Generate a link to check the DNS records of the email domain
    data[
        "dns_check"
    ] = f"https://dnschecker.org/all-dns-records-of-domain.php?query={domain}&rtype=ALL&dns=google"

    # Try to validate the email address using the validate_email function
    try:
        # The validate_email function returns a data object with information about the email address
        email_data = validate_email(
            email_address,
            check_deliverability=check_deliverability,
            test_environment=test_environment,
        )

        # Store the information from the email_data object in the data dictionary
        data["information"] = {
            "normalized": email_data.normalized,  # The normalized email address
            "valid": True,  # The email address is valid
            "local_part": email_data.local_part,  # The local part of the email address (before the @)
            "domain": email_data.domain,  # The domain of the email address (after the @)
            "ascii_email": email_data.ascii_email,  # The email address in ASCII format
            "ascii_local_part": email_data.ascii_local_part,  # The local part of the email address in ASCII format
            "ascii_domain": email_data.ascii_domain,  # The domain of the email address in ASCII format
            "smtputf8": email_data.smtputf8,  # Whether the email address uses SMTPUTF8 (allows Unicode in email addresses)
            "mx": None
            if not check_deliverability
            else email_data.mx,  # The MX record of the email domain, if check_deliverability is True
            "mx_fallback_type": None
            if not check_deliverability
            else email_data.mx_fallback_type,  # The type of MX record fallback used, if check_deliverability is True
        }

        # Set the message in the data dictionary to indicate that the email validation was successful
        data["message"] = "Email validation successful"

        # Log that the email validation was successful
        logger.info("Email validation successful")

        # Return the data dictionary
        return data

    # If the email address is not deliverable, catch the EmailUndeliverableError
    except EmailUndeliverableError as ex:
        # Set the message in the data dictionary to the error message
        data["message"] = f"EmailUndeliverableError '{str(ex)}'"

        # Set error in the data dictionary to True
        data["error"] = True

        # Log the error
        logger.error(f"EmailUndeliverableError '{str(ex)}'")

        # Return the data dictionary
        return data

    # If the email address is not valid, catch the EmailNotValidError
    except EmailNotValidError as ex:
        # Set the message in the data dictionary to the error message
        data["message"] = f"EmailNotValidError '{str(ex)}'"

        # Set error in the data dictionary to True
        data["error"] = True

        # Log the error
        logger.error(f"EmailNotValidError '{str(ex)}'")
    # If a general exception occurs, catch it
    except Exception as ex:
        # Set the message in the data dictionary to the error message
        data[
            "message"
        ] = f"An Exception '{str(ex)}' has occured. This could be due to no value is set on the domain."

        # Set error in the data dictionary to True
        data["error"] = True

        # Log the error as a critical issue
        logger.critical(
            f"An Exception '{str(ex)}' has occured. This could be due to no value is set on the domain."
        )

    # Return the data dictionary
    return data


#####################################################################

# @router.get("/file-formats", response_model=List[str])
# async def list_file_formats():
#     logger.info("Request received to list all available file formats")

#     try:
#         file_formats = [format.value for format in FileFormatEnum]
#         logger.info(f"Available file formats: {file_formats}")

#         return file_formats

#     except Exception as e:
#         error_message = f"Error in listing file formats: {str(e)}"
#         logger.error(error_message)
#         raise HTTPException(status_code=500, detail=error_message)


# @router.post("/file-converter", status_code=status.HTTP_200_OK)
# async def convert_file_api(
#     convert: FileFormatEnum = Form(...), file: UploadFile = File(...)
# ) -> StreamingResponse:
#     """
#     Asynchronous API endpoint to convert files from one format to another.

#     This function receives a file and a target format, performs the conversion,
#     and returns the converted file. The conversion process is logged with its duration
#     and the size of the converted file.

#     Parameters:
#     convert (FileFormatEnum): The target file format for conversion, received via form data.
#     file (UploadFile): The file to be converted, received as an upload.

#     Returns:
#     StreamingResponse: A response object that streams the converted file back to the client.
#     """

#     # Record the start time for logging duration of the process
#     t0 = time.time()

#     # Read the content of the uploaded file
#     file_content = await file.read()

#     # Perform conversion using the specified format
#     conversion_result = await convert_file_format(
#         conversion_type=convert, content=file_content
#     )

#     # Convert the conversion result to bytes if it's not already in bytes format
#     if isinstance(conversion_result, str):
#         conversion_result_bytes = conversion_result.encode("utf-8")
#     else:
#         conversion_result_bytes = conversion_result

#     # Create a file-like object from the conversion result bytes
#     result_file = io.BytesIO(conversion_result_bytes)
#     # Set the file name using the desired output format
#     result_file.name = f"converted_file.{convert.value.split(' to ')[-1]}"

#     # Calculate the size of the converted file for logging and response headers
#     file_size = result_file.getbuffer().nbytes

#     # Calculate the total processing time
#     t1 = time.time() - t0
#     # Log the processing time and file size
#     logger.info(
#         f"File converted from {convert.value} in {t1:.4f} seconds, file size: {file_size} bytes"
#     )

#     # Create a StreamingResponse to send the converted file back to the client
#     return StreamingResponse(
#         result_file,
#         media_type="application/octet-stream",
#         headers={
#             "Content-Disposition": f"attachment; filename={result_file.name}",
#             "Content-Length": str(file_size),
#         },
#     )


# @router.post("/file-converter-html", status_code=status.HTTP_201_CREATED)
# async def convert_file_html(
#     request: Request,
#     convert: FileFormatEnum = Form(...),
#     file: UploadFile = File(...),
# ):
#     start_time = time.time()
#     logger.info(f"Initiating file conversion process, target format: {convert.name}")

#     data = {"message": None, "result": None, "error": None}

#     try:
#         # Read the uploaded file
#         file_content = await file.read()
#         logger.debug(
#             f"Received file '{file.filename}' for conversion, size: {len(file_content)} bytes"
#         )

#         # Perform conversion
#         conversion_result = await convert_file_format(
#             conversion_type=convert, content=file_content
#         )
#         logger.info(
#             f"File '{file.filename}' successfully converted from {convert.name}"
#         )

#         # Update the response data
#         data["message"] = f"File converted successfully from {convert.name}"
#         data["result"] = conversion_result

#     except Exception as e:
#         error_message = f"Error during file conversion: {str(e)}"
#         logger.error(error_message)
#         data["error"] = str(e)
#         data["message"] = "There has been an error during file conversion"

#         # Optionally re-raise the exception if you want to halt the process
#         # raise HTTPException(status_code=500, detail=error_message)

#     # Calculate processing time
#     processing_time = time.time() - start_time
#     logger.info(f"File conversion process completed in {processing_time:.4f} seconds")

#     # Return the response
#     return templates.TemplateResponse(
#         "file-converter-response.html", {"request": request, "data": data}
#     )


# async def create_example_json(qty: int = 10):
#     logger.info(f"Starting to create example JSON data with quantity: {qty}")

#     data = []
#     contact_method = ["email", "phone", "pigeon"]
#     client_status = ["active", "inactive", "jail"]
#     assigned_representatives = [
#         "Alice Smith",
#         "Bob Johnson",
#         "Cathy Brown",
#         "David Wilson",
#         "Emma Jones",
#         "Frank Garcia",
#         "Grace Miller",
#         "Harry Davis",
#         "Ivy Martinez",
#         "Jack Taylor",
#     ]

#     try:
#         for _ in tqdm(range(qty)):
#             days_ago = random.randint(0, 4 * 365)  # 4 years worth of days
#             last_contact_date = datetime.today() - timedelta(days=days_ago)

#             data_dict = {
#                 "pkid": str(uuid.uuid4()),
#                 "name": silly.name(),
#                 "date": datetime.today().strftime("%Y-%m-%d"),
#                 "description": silly.sentence(),
#                 "email": silly.email(),
#                 "phone_number": silly.phone_number(),
#                 "address": silly.address(),
#                 "preferred_contact_method": contact_method[
#                     random.randint(0, len(contact_method) - 1)
#                 ],
#                 "client_status": client_status[
#                     random.randint(0, len(client_status) - 1)
#                 ],
#                 "last_contact_date": last_contact_date.strftime("%Y-%m-%d"),
#                 "assigned_representative": assigned_representatives[
#                     random.randint(0, len(assigned_representatives) - 1)
#                 ],
#             }
#             data.append(data_dict)

#         logger.info("Successfully created example JSON data")

#     except Exception as e:
#         logger.error(f"Error in create_example_json: {e}")
#         raise  # Re-raise the exception after logging

#     return data


# @router.get("/example-json")
# async def get_example_json(qty: int = 10):
#     logger.info(f"Request received to generate example JSON with quantity: {qty}")

#     try:
#         # Generate example JSON data
#         data = await create_example_json(qty=qty)
#         logger.debug(f"Generated example JSON data: {data}")

#         # Create a temporary file to store the JSON data
#         with tempfile.NamedTemporaryFile(
#             mode="w+", delete=False, suffix=".json"
#         ) as tmp:
#             json.dump(data, tmp)
#             tmp_path = tmp.name
#             logger.debug(f"JSON data written to temporary file: {tmp_path}")

#         logger.info("Returning file response with generated JSON data")
#         return FileResponse(
#             path=tmp_path, filename="example_data.json", media_type="application/json"
#         )

#     except Exception as e:
#         logger.error(f"Error encountered in get_example_json: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

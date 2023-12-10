# -*- coding: utf-8 -*-
"""
File Type Conversion Matrix:
|       | JSON         | XML          | YAML         | TOML         |
|-------|--------------|--------------|--------------|--------------|
| JSON  | —            | JSON to XML  | JSON to YAML | JSON to TOML |
| XML   | XML to JSON  | —            | XML to YAML  | XML to TOML  |
| YAML  | YAML to JSON | YAML to XML  | —            | YAML to TOML |
| TOML  | TOML to JSON | TOML to XML  | TOML to YAML | —            |

Each cell in the matrix indicates the conversion from the row type to the column type.
For example, "JSON to XML" means converting from JSON to XML.
Cells marked with "—" indicate no conversion (same file type).
"""
import io
import json  # Used for reading and writing JSON data
import random
import string
import uuid
from datetime import datetime, timedelta
from enum import Enum

# TODO: Need to add check for imported libraries of xmltodict, pyyaml, and toml
import toml  # Used for reading and writing TOML data
import xmltodict  # Used for converting XML data to Python dictionary and vice versa
import yaml  # Used for reading and writing YAML data
from loguru import logger  # Used for logging
from tqdm import tqdm


def read_json(json_content):
    """
    Convert a JSON string into a Python dictionary.

    Args:
        json_content (str): The JSON string to convert.

    Returns:
        dict: The Python dictionary representation of the JSON string.

    Raises:
        Exception: If there is an error parsing the JSON string.
    """
    logger.debug("Reading JSON content")
    try:
        return json.loads(json_content)
    except Exception as e:
        logger.error(f"Error reading JSON content: {e}")
        raise


def write_json(dict_content):
    """
    Convert a Python dictionary into a JSON string.

    Args:
        dict_content (dict): The Python dictionary to convert.

    Returns:
        str: The JSON string representation of the Python dictionary.

    Raises:
        Exception: If there is an error generating the JSON string.
    """
    logger.debug("Writing JSON content")
    try:
        return json.dumps(dict_content, indent=4)
    except Exception as e:
        logger.error(f"Error writing JSON content: {e}")
        raise


def read_xml(xml_content):
    """
    Convert an XML string into a Python dictionary.

    Args:
        xml_content (str): The XML string to convert.

    Returns:
        dict: The Python dictionary representation of the XML string.

    Raises:
        Exception: If there is an error parsing the XML string.
    """
    logger.debug("Reading XML content")
    try:
        return xmltodict.parse(xml_content)  # Convert XML string to Python dictionary
    except Exception as e:
        logger.error(f"Error reading XML content: {e}")
        raise


def write_xml(dict_content, root_element="root"):
    """
    Convert a Python dictionary into an XML string.

    Args:
        dict_content (dict): The Python dictionary to convert.
        root_element (str): The root element of the XML string.

    Returns:
        str: The XML string representation of the Python dictionary.

    Raises:
        ValueError: If the content to be converted is not a dictionary.
    """
    logger.debug("Writing XML content")
    if not isinstance(dict_content, dict):  # Check if the content is a dictionary
        logger.error("XML content must be a dictionary")
        raise ValueError("XML content must be a dictionary")
    # Convert Python dictionary to XML string
    return xmltodict.unparse({root_element: dict_content}, pretty=True)


def read_yaml(yaml_content):
    """
    Convert a YAML string into a Python dictionary.

    Args:
        yaml_content (str): The YAML string to convert.

    Returns:
        dict: The Python dictionary representation of the YAML string.

    Raises:
        Exception: If there is an error parsing the YAML string.
    """
    logger.debug("Reading YAML content")
    try:
        return yaml.safe_load(yaml_content)  # Convert YAML string to Python dictionary
    except Exception as e:
        logger.error(f"Error reading YAML content: {e}")
        raise


def write_yaml(dict_content):
    """
    Convert a Python dictionary into a YAML string.

    Args:
        dict_content (dict): The Python dictionary to convert.

    Returns:
        str: The YAML string representation of the Python dictionary.

    Raises:
        Exception: If there is an error generating the YAML string.
    """
    logger.debug("Writing YAML content")
    try:
        return yaml.dump(dict_content)  # Convert Python dictionary to YAML string
    except Exception as e:
        logger.error(f"Error writing YAML content: {e}")
        raise


def read_toml(toml_content):
    """
    Convert a TOML string into a Python dictionary.

    Args:
        toml_content (str): The TOML string to convert.

    Returns:
        dict: The Python dictionary representation of the TOML string.

    Raises:
        Exception: If there is an error parsing the TOML string.
    """
    logger.debug("Reading TOML content")
    try:
        toml_content = ensure_string(toml_content)  # Ensure the content is a string
        return toml.loads(toml_content)  # Convert TOML string to Python dictionary
    except Exception as e:
        logger.error(f"Error reading TOML content: {e}")
        raise


def write_toml(dict_content):
    """
    Convert a Python dictionary into a TOML string.

    Args:
        dict_content (dict): The Python dictionary to convert.

    Returns:
        str: The TOML string representation of the Python dictionary.

    Raises:
        Exception: If there is an error generating the TOML string.
    """
    logger.debug("Writing TOML content")
    try:
        return toml.dumps(dict_content)  # Convert Python dictionary to TOML string
    except Exception as e:
        logger.error(f"Error writing TOML content: {e}")
        raise


def ensure_string(content):
    """
    Ensure the content is a string.

    Args:
        content (Any): The content to convert to a string.

    Returns:
        str: The content as a string.
    """
    if isinstance(content, bytes):
        # If the content is bytes, decode it to a string
        return content.decode("utf-8")
    elif not isinstance(content, str):
        # If the content is not a string or bytes, convert it to a string
        return str(content)
    else:
        # If the content is already a string, return it as is
        return content


class FileFormatEnum(str, Enum):
    """
    This enumeration defines the supported file format conversions between JSON, XML, YAML, and TOML.
    Each enum value represents a specific conversion from one format to another.

    The conversion matrix below provides an overview of all possible conversions. In the matrix:
    - Rows represent the source format.
    - Columns represent the target format.
    - Each cell shows the conversion direction, e.g., 'JSON to XML'.
    - Cells marked with '—' indicate no conversion is needed (same file type).

    Conversion Matrix:
    |       | JSON         | XML          | YAML         | TOML         |
    |-------|--------------|--------------|--------------|--------------|
    | JSON  | —            | JSON to XML  | JSON to YAML | JSON to TOML |
    | XML   | XML to JSON  | —            | XML to YAML  | XML to TOML  |
    | YAML  | YAML to JSON | YAML to XML  | —            | YAML to TOML |
    | TOML  | TOML to JSON | TOML to XML  | TOML to YAML | —            |

    Enum values:
    - json_to_yaml: Converts JSON to YAML
    - json_to_xml: Converts JSON to XML
    - json_to_toml: Converts JSON to TOML
    - xml_to_json: Converts XML to JSON
    - xml_to_yaml: Converts XML to YAML
    - xml_to_toml: Converts XML to TOML
    - yaml_to_json: Converts YAML to JSON
    - yaml_to_xml: Converts YAML to XML
    - yaml_to_toml: Converts YAML to TOML
    - toml_to_json: Converts TOML to JSON
    - toml_to_xml: Converts TOML to XML
    - toml_to_yaml: Converts TOML to YAML
    """

    json_to_yaml = "json to yaml"
    json_to_xml = "json to xml"
    json_to_toml = "json to toml"
    xml_to_json = "xml to json"
    xml_to_yaml = "xml to yaml"
    xml_to_toml = "xml to toml"
    yaml_to_json = "yaml to json"
    yaml_to_xml = "yaml to xml"
    yaml_to_toml = "yaml to toml"
    toml_to_json = "toml to json"
    toml_to_xml = "toml to xml"
    toml_to_yaml = "toml to yaml"


async def convert_file_format(
    conversion_type: FileFormatEnum, content, xml_root_element="root"
):
    """
    Convert file content from one format to another.

    Args:
        conversion_type (FileFormatEnum): The type of conversion to perform.
        content (str): The content to convert.
        xml_root_element (str, optional): The root element for XML content. Defaults to "root".

    Returns:
        str: The converted content.

    Raises:
        Exception: If there is an error during conversion.
    """
    # Split the conversion type into source and target formats
    source_format, target_format = conversion_type.value.split(" to ")
    logger.info(
        f"Initiating file format conversion from {source_format} to {target_format}"
    )

    try:
        # Read the content into a dictionary
        dict_content = None
        if source_format.lower() == "json":
            logger.debug("Reading JSON content")
            dict_content = read_json(
                content
            )  # Convert JSON content to Python dictionary
        elif source_format.lower() == "xml":
            logger.debug("Reading XML content")
            dict_content = read_xml(content)  # Convert XML content to Python dictionary
        elif source_format.lower() == "yaml":
            logger.debug("Reading YAML content")
            dict_content = read_yaml(
                content
            )  # Convert YAML content to Python dictionary
        elif source_format.lower() == "toml":
            logger.debug("Reading TOML content")
            dict_content = read_toml(
                content
            )  # Convert TOML content to Python dictionary
        else:
            # Raise an error if the source format is not supported
            logger.error(f"Unsupported source format: {source_format}")
            raise ValueError(f"Unsupported source format: {source_format}")

        # Write the dictionary to the target format
        if target_format.lower() == "json":
            logger.debug("Writing to JSON format")
            return write_json(dict_content)  # Convert Python dictionary to JSON string
        elif target_format.lower() == "xml":
            logger.debug("Writing to XML format")
            # Convert Python dictionary to XML string
            return write_xml(dict_content, root_element=xml_root_element)
        elif target_format.lower() == "yaml":
            logger.debug("Writing to YAML format")
            return write_yaml(dict_content)  # Convert Python dictionary to YAML string
        elif target_format.lower() == "toml":
            logger.debug("Writing to TOML format")
            return write_toml(dict_content)  # Convert Python dictionary to TOML string
        else:
            # Raise an error if the target format is not supported
            logger.error(f"Unsupported target format: {target_format}")
            raise ValueError(f"Unsupported target format: {target_format}")

    except Exception as e:
        # Log the error and re-raise it
        logger.error(
            f"Error in file format conversion ({source_format} to {target_format}): {e}"
        )
        raise


async def create_example_json(qty: int = 10):
    logger.info(f"Starting to create example JSON data with quantity: {qty}")

    data: list = []

    contact_method = ["email", "phone", "pigeon"]
    client_status = ["active", "inactive", "jail"]
    assigned_representatives = [
        "Alice Smith",
        "Bob Johnson",
        "Cathy Brown",
        "David Wilson",
        "Emma Jones",
        "Frank Garcia",
        "Grace Miller",
        "Harry Davis",
        "Ivy Martinez",
        "Jack Taylor",
    ]

    try:
        for _ in tqdm(range(qty)):
            days_ago = random.randint(0, 4 * 365)  # 4 years worth of days
            last_contact_date = datetime.today() - timedelta(days=days_ago)

            # Generate random string of 5 characters for name
            name = "".join(
                random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5)
            )

            # Generate random string of 10 characters for description
            description = "".join(
                random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)
            )

            # Generate random email
            email = (
                "".join(random.choices(string.ascii_lowercase, k=5)) + "@example.com"
            )

            # Generate random phone number
            phone_number = "".join(random.choices(string.digits, k=10))

            # Generate random address
            address = "".join(
                random.choices(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits,
                    k=20,
                )
            )

            data_dict = {
                "pkid": str(uuid.uuid4()),
                "name": name,
                "date": datetime.today().strftime("%Y-%m-%d"),
                "description": description,
                "email": email,
                "phone_number": phone_number,
                "address": address,
                "preferred_contact_method": random.choice(contact_method),
                "client_status": random.choice(client_status),
                "last_contact_date": last_contact_date.strftime("%Y-%m-%d"),
                "assigned_representative": random.choice(assigned_representatives),
            }
            data.append(data_dict)

        logger.info("Successfully created example JSON data")

    except Exception as e:
        logger.error(f"Error in create_example_json: {e}")
        raise  # Re-raise the exception after logging

    result: dict = {"psuedo_users": data}
    return result


# if __name__ == "__main__":
#     # Define a list of conversions with example content
#     conversion_examples = [
#         {"conversion_type": FileFormatEnum.json_to_xml, "content": '{"person": {"name": "John", "age": 30}}', "xml_root_element": "person"},
#         {"conversion_type": FileFormatEnum.xml_to_json, "content": '<person><name>John</name><age>30</age></person>'},
#         {"conversion_type": FileFormatEnum.json_to_yaml, "content": '{"person": {"name": "John", "age": 30}}'},
#         {"conversion_type": FileFormatEnum.yaml_to_json, "content": 'person:\n  name: John\n  age: 30'},
#         {"conversion_type": FileFormatEnum.json_to_toml, "content": '{"person": {"name": "John", "age": 30}}'},
#         {"conversion_type": FileFormatEnum.toml_to_json, "content": '[person]\nname = "John"\nage = 30'},
#         {"conversion_type": FileFormatEnum.xml_to_yaml, "content": '<person><name>John</name><age>30</age></person>'},
#         {"conversion_type": FileFormatEnum.yaml_to_xml, "content": 'person:\n  name: John\n  age: 30', "xml_root_element": "person"},
#         {"conversion_type": FileFormatEnum.xml_to_toml, "content": '<person><name>John</name><age>30</age></person>'},
#         {"conversion_type": FileFormatEnum.toml_to_xml, "content": '[person]\nname = "John"\nage = 30', "xml_root_element": "person"},
#         {"conversion_type": FileFormatEnum.yaml_to_toml, "content": 'person:\n  name: John\n  age: 30'},
#         {"conversion_type": FileFormatEnum.toml_to_yaml, "content": '[person]\nname = "John"\nage = 30'}
#     ]


#     # Loop through each conversion example
#     for example in conversion_examples:
#         conversion_type = example["conversion_type"]
#         content = example["content"]
#         xml_root_element = example.get("xml_root_element", "root")

#         # Perform the conversion
#         result = convert_file_format(conversion_type, content, xml_root_element=xml_root_element)

#         # Print the results
#         print(f"\nConversion: {conversion_type.value}")
#         print("Result:", result)


########################################################################
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

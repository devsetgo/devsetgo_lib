# -*- coding: utf-8 -*-
"""
This module provides a dictionary of HTTP status codes and their descriptions.

The dictionary `ALL_HTTP_CODES` contains the HTTP status codes as keys. Each key
maps to another dictionary that contains a description of the status code and a
link to its documentation on the Mozilla Developer Network (MDN).

Example:
    ```python from dsg_lib import http_codes

    # Get the description and link for HTTP status code 200 status_200 =
    http_codes.ALL_HTTP_CODES[200] print(status_200)  # {'description': 'OK',
    'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200'} ```

Variables:
    ALL_HTTP_CODES (dict): A dictionary of HTTP status codes. Each key is an
    HTTP status code (int), and each value is another dictionary with keys
    'description' (str) and 'link' (str).
"""
from loguru import logger

from ._all_codes import ALL_HTTP_CODES

# TODO: Create a way to extend the ALL_HTTP_CODES dictionary with custom codes.
# TODO: Create a way to extend the ALL_HTTP_CODES example response like the
# model_content below. model_content = { "model": dict, "content": {
#             "application/json": { "example": { "message": "Example message", }
#             } }, } status_response = generate_code_dict( [400, 405, 422, 500],
#                 description_only=False ) # Iterate over all status codes for
#                     code in status_response: # Update the status code
#                         dictionary status_response[code].update(model_content)
#                     # type: ignore"""


def generate_code_dict(codes, description_only=False):
    """
    Generate a dictionary of specific HTTP error codes from the http_codes
    dictionary.

    This function takes a list of HTTP status codes and an optional boolean
    flag. If the flag is True, the function returns a dictionary where each key
    is an HTTP status code from the input list and each value is the
    corresponding description from the ALL_HTTP_CODES dictionary. If the flag is
    False, the function returns a dictionary where each key is an HTTP status
    code from the input list and each value is the corresponding dictionary from
    the ALL_HTTP_CODES dictionary.

    Args:
        codes (list): A list of HTTP status codes. description_only (bool,
        optional): If True, only the description of the codes will be returned.
        Defaults to False.

    Returns:
        dict: A dictionary where each key is an HTTP error code from the input
        list and each value depends on the description_only parameter.

    Example:
        ```python from dsg_lib import http_codes

        # Generate a dictionary for HTTP status codes 200 and 404 status_dict =
        http_codes.generate_code_dict([200, 404]) print(status_dict)  # {200:
        {'description': 'OK', 'link':
        'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200'}, 404:
        {'description': 'Not Found', 'link':
        'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404'}}

        # Generate a dictionary for HTTP status codes 200 and 404 with only
        descriptions status_dict = http_codes.generate_code_dict([200, 404],
        description_only=True) print(status_dict)  # {200: 'OK', 404: 'Not
        Found'} ```
    """

    if description_only:
        # Log the operation
        logger.debug(f"description_only is True and returning HTTP codes: {codes}")

        # If description_only is True, return a dictionary where each key is an
        # HTTP error code from the input list and each value is the
        # corresponding description from the ALL_HTTP_CODES dictionary.
        return {
            code: ALL_HTTP_CODES[code]["description"]
            for code in codes
            if code in ALL_HTTP_CODES
        }
    else:
        # Log the operation
        logger.debug(f"returning HTTP codes: {codes}")

        # If description_only is False, return a dictionary where each key is an
        # HTTP error code from the input list and each value is the
        # corresponding dictionary from the ALL_HTTP_CODES dictionary.
        return {code: ALL_HTTP_CODES[code] for code in codes if code in ALL_HTTP_CODES}


# Usage: A list of common HTTP status codes used in various HTTP methods
common_codes = [200, 400, 401, 403, 404, 408, 429, 500, 503]

# A dictionary of common HTTP status codes and additional codes specific to GET
# requests

GET_CODES = generate_code_dict(common_codes + [206, 304, 307, 410, 502])

"""
GET_CODES is a dictionary of HTTP status codes for GET requests. It includes all
the common codes, plus some additional codes that are specific to GET requests.

Example:
    ```python from dsg_lib import http_codes

    # Print the dictionary of HTTP status codes for GET requests
    print(http_codes.GET_CODES) ```
"""

# A dictionary of common HTTP status codes and additional codes specific to POST
# requests
POST_CODES = generate_code_dict(common_codes + [201, 202, 205, 307, 409, 413, 415])
"""
POST_CODES is a dictionary of HTTP status codes for POST requests. It includes
all the common codes, plus some additional codes that are specific to POST
requests.

Example:
    ```python from dsg_lib import http_codes

    # Print the dictionary of HTTP status codes for POST requests
    print(http_codes.POST_CODES) ```
"""

# A dictionary of common HTTP status codes and additional codes specific to PUT
# requests
PUT_CODES = generate_code_dict(common_codes + [202, 204, 206, 409, 412, 413])
"""
PUT_CODES is a dictionary of HTTP status codes for PUT requests. It includes all
the common codes, plus some additional codes that are specific to PUT requests.

Example:
    ```python from dsg_lib import http_codes

    # Print the dictionary of HTTP status codes for PUT requests
    print(http_codes.PUT_CODES) ```
"""

# A dictionary of common HTTP status codes and additional codes specific to
# PATCH requests
PATCH_CODES = generate_code_dict(common_codes + [202, 204, 206, 409, 412, 413])
"""
PATCH_CODES is a dictionary of HTTP status codes for PATCH requests. It includes
all the common codes, plus some additional codes that are specific to PATCH
requests.

Example:
    ```python from dsg_lib import http_codes

    # Print the dictionary of HTTP status codes for PATCH requests
    print(http_codes.PATCH_CODES) ```
"""

# A dictionary of common HTTP status codes and additional codes specific to
# DELETE requests
DELETE_CODES = generate_code_dict(common_codes + [202, 204, 205, 409])
"""
DELETE_CODES is a dictionary of HTTP status codes for DELETE requests. It
includes all the common codes, plus some additional codes that are specific to
DELETE requests.

Example:
    ```python from dsg_lib import http_codes

    # Print the dictionary of HTTP status codes for DELETE requests
    print(http_codes.DELETE_CODES) ```
"""

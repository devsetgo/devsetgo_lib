# -*- coding: utf-8 -*-
"""
.. module:: http_codes
   :platform: Unix, Windows
   :synopsis: Dictionary of HTTP error codes and their descriptions based on the HTTP/1.1 specification.
The dictionary provides a mapping between HTTP error codes and their description strings.
Use example:
- `http_codes` can be used to define or handle custom error responses for an API,
- GET_CODES, POST_CODES, PUT_CODES, PATCH_CODES, and DELETE_CODES can be used to define
    HTTP error codes commonly encountered with each type of request method in an API.

.. moduleauthor:: Mike Ryan <mike@devsetgo.com>

"""
from ..logger import logger

ALL_HTTP_CODES = {
    100: {
        "description": "Continue",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/100",
    },
    101: {
        "description": "Switching Protocols",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/101",
    },
    102: {
        "description": "Processing",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/102",
    },
    103: {
        "description": "Early Hints",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/103",
    },
    200: {
        "description": "OK",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200",
    },
    201: {
        "description": "Created",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/201",
    },
    202: {
        "description": "Accepted",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202",
    },
    203: {
        "description": "Non-Authoritative Information",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/203",
    },
    204: {
        "description": "No Content",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/204",
    },
    205: {
        "description": "Reset Content",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/205",
    },
    206: {
        "description": "Partial Content",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/206",
    },
    207: {
        "description": "Multi-Status",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/207",
    },
    208: {
        "description": "Already Reported",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/208",
    },
    226: {
        "description": "IM Used",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/226",
    },
    300: {
        "description": "Multiple Choices",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/300",
    },
    301: {
        "description": "Moved Permanently",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301",
    },
    302: {
        "description": "Found",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/302",
    },
    303: {
        "description": "See Other",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/303",
    },
    304: {
        "description": "Not Modified",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/304",
    },
    305: {
        "description": "Use Proxy",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/305",
    },
    306: {
        "description": "(Unused)",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/306",
    },
    307: {
        "description": "Temporary Redirect",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/307",
    },
    308: {
        "description": "Permanent Redirect",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/308",
    },
    400: {
        "description": "Bad Request",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400",
    },
    401: {
        "description": "Unauthorized",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401",
    },
    402: {
        "description": "Payment Required",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402",
    },
    403: {
        "description": "Forbidden",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403",
    },
    404: {
        "description": "Not Found",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404",
    },
    405: {
        "description": "Method Not Allowed",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405",
    },
    406: {
        "description": "Not Acceptable",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/406",
    },
    407: {
        "description": "Proxy Authentication Required",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/407",
    },
    408: {
        "description": "Request Timeout",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408",
    },
    409: {
        "description": "Conflict",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409",
    },
    410: {
        "description": "Gone",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/410",
    },
    411: {
        "description": "Length Required",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/411",
    },
    412: {
        "description": "Precondition Failed",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/412",
    },
    413: {
        "description": "Payload Too Large",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/413",
    },
    414: {
        "description": "URI Too Long",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/414",
    },
    415: {
        "description": "Unsupported Media Type",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/415",
    },
    416: {
        "description": "Range Not Satisfiable",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/416",
    },
    417: {
        "description": "Expectation Failed",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/417",
    },
    418: {
        "description": "I'm a teapot",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418",
    },
    421: {
        "description": "Misdirected Request",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/421",
    },
    422: {
        "description": "Unprocessable Entity",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422",
    },
    423: {
        "description": "Locked",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/423",
    },
    424: {
        "description": "Failed Dependency",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/424",
    },
    425: {
        "description": "Too Early",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/425",
    },
    426: {
        "description": "Upgrade Required",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/426",
    },
    428: {
        "description": "Precondition Required",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/428",
    },
    429: {
        "description": "Too Many Requests",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429",
    },
    431: {
        "description": "Request Header Fields Too Large",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/431",
    },
    451: {
        "description": "Unavailable For Legal Reasons",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/451",
    },
    500: {
        "description": "Internal Server Error",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500",
    },
    501: {
        "description": "Not Implemented",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/501",
    },
    502: {
        "description": "Bad Gateway",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502",
    },
    503: {
        "description": "Service Unavailable",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503",
    },
    504: {
        "description": "Gateway Timeout",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504",
    },
    505: {
        "description": "HTTP Version Not Supported",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/505",
    },
    506: {
        "description": "Variant Also Negotiates",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/506",
    },
    507: {
        "description": "Insufficient Storage",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/507",
    },
    508: {
        "description": "Loop Detected",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/508",
    },
    510: {
        "description": "Not Extended",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/510",
    },
    511: {
        "description": "Network Authentication Required",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/511",
    },
}


def generate_code_dict(codes, description_only=False):
    """
    Generate a dictionary of specific HTTP error codes from the http_codes dictionary.

    Args:
        codes (list): A list of HTTP error codes.
        description_only (bool): If True, only the description of the codes will be
         returned.

    Returns:
        dict: A dictionary where each key is an HTTP error code from the input list and
              each value depends on the description_only parameter.
    """

    if description_only:
        # Log the operation
        logger.debug(f"description_only is True and returning HTTP codes: {codes}")

        # If description_only is True, return a dictionary where each key is an HTTP error code from the input list
        # and each value is the corresponding description from the ALL_HTTP_CODES dictionary.
        return {
            code: ALL_HTTP_CODES[code]["description"]
            for code in codes
            if code in ALL_HTTP_CODES
        }
    else:
        # Log the operation
        logger.debug(f"returning HTTP codes: {codes}")

        # If description_only is False, return a dictionary where each key is an HTTP error code from the input list
        # and each value is the corresponding dictionary from the ALL_HTTP_CODES dictionary.
        return {code: ALL_HTTP_CODES[code] for code in codes if code in ALL_HTTP_CODES}


# Usage:
common_codes = [200, 400, 401, 403, 404, 408, 429, 500, 503]

GET_CODES = generate_code_dict(common_codes + [206, 304, 307, 410, 502])

# Generate dictionary of common error codes for POST requests
POST_CODES = generate_code_dict(common_codes + [201, 202, 205, 307, 409, 413, 415])

# Generate dictionary of common error codes for PUT requests
PUT_CODES = generate_code_dict(common_codes + [202, 204, 206, 409, 412, 413])

# Generate dictionary of common error codes for PATCH requests
PATCH_CODES = generate_code_dict(common_codes + [202, 204, 206, 409, 412, 413])

# Generate dictionary of common error codes for DELETE requests
DELETE_CODES = generate_code_dict(common_codes + [202, 204, 205, 409])

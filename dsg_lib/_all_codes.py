# -*- coding: utf-8 -*-
"""
A dictionary containing all HTTP status codes, their descriptions, and links to
their documentation.

This dictionary is a mapping from HTTP status codes to dictionaries containing
their descriptions and links to their documentation.

Each key in this dictionary is an HTTP status code, and each value is another
dictionary with keys 'description' and 'link'. The 'description' key maps to a
string that describes the HTTP status code, and the 'link' key maps to a string
that is a link to the documentation for the HTTP status code.

Example:
    ```python from dsg_lib.http_codes import ALL_HTTP_CODES

    # Get the dictionary for HTTP status code 200 status_200 =
    ALL_HTTP_CODES[200] print(status_200)  # {'description': 'OK', 'link':
    'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200'}

    # Get the description for HTTP status code 404 description_404 =
    ALL_HTTP_CODES[404]['description'] print(description_404)  # 'Not Found'

    # Get the link to the documentation for HTTP status code 500 link_500 =
    ALL_HTTP_CODES[500]['link'] print(link_500)  #
    'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500' ```
"""

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

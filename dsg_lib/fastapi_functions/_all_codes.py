# -*- coding: utf-8 -*-
"""
This module contains a dictionary mapping HTTP status codes to their descriptions,
extended descriptions, and links to their documentation.

Each key in this dictionary is an HTTP status code, and each value is another
dictionary with keys 'description', 'extended_description', and 'link'.

The 'description' key maps to a brief string that describes the HTTP status code.
The 'extended_description' key maps to a more detailed explanation of the status code.
The 'link' key maps to a string that is a link to the documentation for the HTTP status code.

Example:
    ```python
    from dsg_lib.fastapi_functions.http_codes import ALL_HTTP_CODES

    # Get the dictionary for HTTP status code 200
    status_200 = ALL_HTTP_CODES[200]
    print(status_200)
    # Output: {'description': 'OK', 'extended_description': 'The request has succeeded.', 'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200'}

    # Get the description for HTTP status code 404
    description_404 = ALL_HTTP_CODES[404]['description']
    print(description_404)  # Output: 'Not Found'

    # Get the extended description for HTTP status code 200
    extended_description_200 = ALL_HTTP_CODES[200]['extended_description']
    print(extended_description_200)  # Output: 'The request has succeeded.'

    # Get the link to the documentation for HTTP status code 500
    link_500 = ALL_HTTP_CODES[500]['link']
    print(link_500)  # Output: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500'
    ```

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""

ALL_HTTP_CODES = {
    100: {
        "description": "Continue",
        "extended_description": "The client should continue with its request. This interim response indicates that everything so far is OK and that the client should continue with the request, or ignore it if it is already finished.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/100",
    },
    101: {
        "description": "Switching Protocols",
        "extended_description": "The server understands and is willing to comply with the client's request, via the Upgrade message header field, for a change in the application protocol being used on this connection.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/101",
    },
    102: {
        "description": "Processing",
        "extended_description": "This code indicates that the server has received and is processing the request, but no response is available yet.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/102",
    },
    103: {
        "description": "Early Hints",
        "extended_description": "This status code is primarily intended to be used with the Link header, letting the user agent start preloading resources while the server is still preparing a response.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/103",
    },
    200: {
        "description": "OK",
        "extended_description": "The request has succeeded.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200",
    },
    201: {
        "description": "Created",
        "extended_description": "The request has been fulfilled and has resulted in a new resource being created.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/201",
    },
    202: {
        "description": "Accepted",
        "extended_description": "The request has been accepted for processing, but the processing has not been completed.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202",
    },
    203: {
        "description": "Non-Authoritative Information",
        "extended_description": "The server successfully processed the request, but is returning information that may be from another source.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/203",
    },
    204: {
        "description": "No Content",
        "extended_description": "The server successfully processed the request and is not returning any content.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/204",
    },
    205: {
        "description": "Reset Content",
        "extended_description": "The server successfully processed the request, but is not returning any content. Unlike a 204 response, this response requires that the requester reset the document view.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/205",
    },
    206: {
        "description": "Partial Content",
        "extended_description": "The server is delivering only part of the resource due to a range header sent by the client.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/206",
    },
    207: {
        "description": "Multi-Status",
        "extended_description": "The message body that follows is an XML message and can contain a number of separate response codes, depending on how many sub-requests were made.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/207",
    },
    208: {
        "description": "Already Reported",
        "extended_description": "The members of a DAV binding have already been enumerated in a preceding part of the (multistatus) response, and are not being included again.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/208",
    },
    226: {
        "description": "IM Used",
        "extended_description": "The server has fulfilled a request for the resource, and the response is a representation of the result of one or more instance-manipulations applied to the current instance.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/226",
    },
    300: {
        "description": "Multiple Choices",
        "extended_description": "Indicates multiple options for the resource that the client may follow.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/300",
    },
    301: {
        "description": "Moved Permanently",
        "extended_description": "This and all future requests should be directed to the given URI.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301",
    },
    302: {
        "description": "Found",
        "extended_description": "Tells the client to look at (browse to) another URL.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/302",
    },
    303: {
        "description": "See Other",
        "extended_description": "The response to the request can be found under another URI using the GET method.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/303",
    },
    304: {
        "description": "Not Modified",
        "extended_description": "Indicates that the resource has not been modified since the version specified by the request headers If-Modified-Since or If-None-Match.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/304",
    },
    305: {
        "description": "Use Proxy",
        "extended_description": "The requested resource is available only through a proxy, the address for which is provided in the response.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/305",
    },
    306: {
        "description": "(Unused)",
        "extended_description": "No longer used. Originally meant 'Subsequent requests should use the specified proxy.'",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/306",
    },
    307: {
        "description": "Temporary Redirect",
        "extended_description": "The request should be repeated with another URI, but future requests should still use the original URI.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/307",
    },
    308: {
        "description": "Permanent Redirect",
        "extended_description": "The request, and all future requests should be repeated using another URI.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/308",
    },
    400: {
        "description": "Bad Request",
        "extended_description": "The server could not understand the request due to invalid syntax.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400",
    },
    401: {
        "description": "Unauthorized",
        "extended_description": "The request requires user authentication.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401",
    },
    402: {
        "description": "Payment Required",
        "extended_description": "This code is reserved for future use.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402",
    },
    403: {
        "description": "Forbidden",
        "extended_description": "The server understood the request, but it refuses to authorize it.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403",
    },
    404: {
        "description": "Not Found",
        "extended_description": "The server can not find the requested resource.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404",
    },
    405: {
        "description": "Method Not Allowed",
        "extended_description": "The method specified in the request is not allowed for the resource identified by the request URI.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405",
    },
    406: {
        "description": "Not Acceptable",
        "extended_description": "The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/406",
    },
    407: {
        "description": "Proxy Authentication Required",
        "extended_description": "The client must first authenticate itself with the proxy.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/407",
    },
    408: {
        "description": "Request Timeout",
        "extended_description": "The server timed out waiting for the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408",
    },
    409: {
        "description": "Conflict",
        "extended_description": "The request could not be completed due to a conflict with the current state of the resource.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409",
    },
    410: {
        "description": "Gone",
        "extended_description": "The requested resource is no longer available at the server and no forwarding address is known.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/410",
    },
    411: {
        "description": "Length Required",
        "extended_description": "The server refuses to accept the request without a defined Content-Length.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/411",
    },
    412: {
        "description": "Precondition Failed",
        "extended_description": "The precondition given in one or more of the request-header fields evaluated to false when it was tested on the server.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/412",
    },
    413: {
        "description": "Payload Too Large",
        "extended_description": "The server is refusing to process a request because the request payload is larger than the server is willing or able to process.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/413",
    },
    414: {
        "description": "URI Too Long",
        "extended_description": "The server is refusing to service the request because the request-target is longer than the server is willing to interpret.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/414",
    },
    415: {
        "description": "Unsupported Media Type",
        "extended_description": "The media format of the requested data is not supported by the server, so the server is rejecting the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/415",
    },
    416: {
        "description": "Range Not Satisfiable",
        "extended_description": "The range specified in the Range header field of the request can't be fulfilled; it's possible that the range is outside the size of the target URI's data.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/416",
    },
    417: {
        "description": "Expectation Failed",
        "extended_description": "The expectation given in the Expect request header could not be met by the server.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/417",
    },
    418: {
        "description": "I'm a teapot",
        "extended_description": "The server refuses to brew coffee because it is, permanently, a teapot. A combined coffee/tea pot that is temporarily out of coffee should instead return 503. This error is a reference to Hyper Text Coffee Pot Control Protocol defined in April Fools' jokes in 1998 and 2014.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418",
    },
    421: {
        "description": "Misdirected Request",
        "extended_description": "The request was directed at a server that is not able to produce a response. This can be sent by a server that is not configured to produce responses for the combination of scheme and authority that are included in the request URI.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/421",
    },
    422: {
        "description": "Unprocessable Entity",
        "extended_description": "The server understands the content type of the request entity, and the syntax of the request entity is correct, but it was unable to process the contained instructions.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422",
    },
    423: {
        "description": "Locked",
        "extended_description": "The resource that is being accessed is locked.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/423",
    },
    424: {
        "description": "Failed Dependency",
        "extended_description": "The request failed due to failure of a previous request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/424",
    },
    425: {
        "description": "Too Early",
        "extended_description": "Indicates that the server is unwilling to risk processing a request that might be replayed.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/425",
    },
    426: {
        "description": "Upgrade Required",
        "extended_description": "The server refuses to perform the request using the current protocol but might be willing to do so after the client upgrades to a different protocol. The server sends an Upgrade header in a 426 response to indicate the required protocol(s).",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/426",
    },
    428: {
        "description": "Precondition Required",
        "extended_description": "The origin server requires the request to be conditional. This response is intended to prevent the 'lost update' problem, where a client GETs a resource's state, modifies it, and PUTs it back to the server, when meanwhile a third party has modified the state on the server, leading to a conflict.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/428",
    },
    429: {
        "description": "Too Many Requests",
        "extended_description": "The user has sent too many requests in a given amount of time ('rate limiting').",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429",
    },
    431: {
        "description": "Request Header Fields Too Large",
        "extended_description": "The server is unwilling to process the request because its header fields are too large.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/431",
    },
    451: {
        "description": "Unavailable For Legal Reasons",
        "extended_description": "The server is denying access to the resource as a consequence of a legal demand.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/451",
    },
    500: {
        "description": "Internal Server Error",
        "extended_description": "The server encountered an unexpected condition that prevented it from fulfilling the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500",
    },
    501: {
        "description": "Not Implemented",
        "extended_description": "The server does not support the functionality required to fulfill the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/501",
    },
    502: {
        "description": "Bad Gateway",
        "extended_description": "The server, while acting as a gateway or proxy, received an invalid response from an inbound server it accessed while attempting to fulfill the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502",
    },
    503: {
        "description": "Service Unavailable",
        "extended_description": "The server is currently unable to handle the request due to a temporary overload or scheduled maintenance, which will likely be alleviated after some delay.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503",
    },
    504: {
        "description": "Gateway Timeout",
        "extended_description": "The server, while acting as a gateway or proxy, did not receive a timely response from an upstream server it needed to access in order to complete the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504",
    },
    505: {
        "description": "HTTP Version Not Supported",
        "extended_description": "The server does not support, or refuses to support, the major version of HTTP that was used in the request message.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/505",
    },
    506: {
        "description": "Variant Also Negotiates",
        "extended_description": "The server has an internal configuration error: the chosen variant resource is configured to engage in transparent content negotiation itself, and is therefore not a proper end point in the negotiation process.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/506",
    },
    507: {
        "description": "Insufficient Storage",
        "extended_description": "The method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/507",
    },
    508: {
        "description": "Loop Detected",
        "extended_description": "The server detected an infinite loop while processing a request with 'Depth: infinity'. This status indicates that the entire operation failed.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/508",
    },
    510: {
        "description": "Not Extended",
        "extended_description": "Further extensions to the request are required for the server to fulfill it.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/510",
    },
    511: {
        "description": "Network Authentication Required",
        "extended_description": "The client needs to authenticate to gain network access. Intended for use by intercepting proxies used to control access to the network.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/511",
    },
}

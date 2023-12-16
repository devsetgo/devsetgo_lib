from dsg_lib import  http_codes
from dsg_lib import _all_codes


def generate_code_dict(codes: list, examples: list = None) -> dict:
    """
    Generate a dictionary of HTTP status codes.

    Arguments:
        codes (list): A list of HTTP status codes.
        examples (list): A list of dictionaries containing examples for each status code.

    Returns:
        dict: A dictionary of HTTP status codes.
    """
    # Initialize the dictionary
    code_dict = {}

    # Loop through each code
    for code in codes:
        # Initialize the code dictionary
        code_dict[code] = {}

        # If examples were provided
        if examples:
            # Loop through each example
            for example in examples:
                # If the code is in the example
                if code in example:
                    # Add the example to the code dictionary
                    code_dict[code]["examples"] = example[code]

        # If the code is in the _all_codes dictionary
        if code in _all_codes:
            # Add the description to the code dictionary
            code_dict[code]["description"] = _all_codes[code]

    # Return the dictionary
    return code_dict


codes = [
    {
        206: {
            "examples": {
                "message": "Not Found",
                "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            }
        }
    }
]
response = http_codes.generate_code_dict([206, 304, 307, 410, 502], examples=codes)
print(response)

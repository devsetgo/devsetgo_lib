# HTTP Codes Module

Welcome to the `dsg_lib.http_codes` module. This module is a part of the `dsg_lib` library, designed to streamline and enhance your experience with the FastAPI framework.

The `http_codes` module provides a set of constants representing HTTP status codes. These constants are designed to be used in FastAPI endpoints, making your code more readable and maintainable by replacing hard-coded status code numbers with meaningful constant names.

Whether you are building a simple API or a complex web application, the `http_codes` module can help you ensure that your endpoints return the correct HTTP status codes. This not only improves the clarity of your code, but also helps to ensure that your API behaves in a way that is consistent with HTTP standards.

In the following sections, we will guide you on how to import and use this module, along with examples to illustrate its usage in various scenarios. Whether you are a beginner or an experienced developer, we hope this documentation will be a valuable resource as you work with the `dsg_lib.http_codes` module.
## Using the Module

The `http_codes` module provides constants for HTTP status codes. These constants can be used in FastAPI endpoints to set the HTTP status code of the response.

Here are examples of how to use the `http_codes` constants in FastAPI endpoints:

```python
from fastapi import FastAPI
from dsg_lib import http_codes

app = FastAPI()

# Create your own list of codes
custom_response = generate_code_dict([400, 405, 500], description_only=False)


# GET endpoint
@app.get("/items/{item_id}",responses=custom_response) # could also use http_codes.GET_CODES
async def read_item(item_id: int):
    # ... get the item ...
    return {"item": item, "code": http_codes.HTTP_200_OK}

# POST endpoint
@app.post("/items/",responses=http_codes.POST_CODES)
async def create_item(item: Item):
    # ... create the item ...
    return {"item": item, "code": http_codes.HTTP_201_CREATED}

# PUT endpoint
@app.put("/items/{item_id}",responses=http_codes.PUT_CODES)
async def update_item(item_id: int, item: Item):
    # ... update the item ...
    return {"item": item, "code": http_codes.HTTP_200_OK}

# DELETE endpoint
@app.delete("/items/{item_id}",responses=http_codes.DELETE_CODES)
async def delete_item(item_id: int):
    # ... delete the item ...
    return {"code": http_codes.HTTP_204_NO_CONTENT}
```

In these examples, the `http_codes` constants are used to set the HTTP status code of the response. The `HTTP_200_OK` constant is used for successful GET and PUT requests, the `HTTP_201_CREATED` constant is used for successful POST requests, and the `HTTP_204_NO_CONTENT` constant is used for successful DELETE requests.

Please note that you need to replace `Item` with your actual item model and implement the logic for getting, creating, updating, and deleting items.


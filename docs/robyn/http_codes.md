# Reference

The HTTP status code helpers are framework-neutral and live in
`dsg_lib.web_common.http_codes`. `dsg_lib.robyn_functions.http_codes` re-exports
them. For Robyn's `responses=` route argument, use the description-only form:

```python
from robyn import Robyn
from dsg_lib.robyn_functions import http_codes

app = Robyn(__file__)

@app.get("/items/:item_id", responses=http_codes.generate_code_dict([404, 422], description_only=True))
def get_item(request):
    ...
```

::: dsg_lib.web_common.http_codes
    handler: python

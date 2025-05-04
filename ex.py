from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from PySchemaForms.form import FormConfig, FormBuilder

app = FastAPI()

# Define a simple Pydantic model for the form
class SimpleForm(BaseModel):
    name: str = Field(..., title="Your Name")
    age: int = Field(..., title="Your Age")

# Configure the form
form_config = FormConfig(
    post_url="/submit",
    theme="bootstrap5",
    form_title="Simple Example Form"
)
form_builder = FormBuilder(SimpleForm, form_config)

@app.get("/", response_class=HTMLResponse)
async def show_form():
    html = form_builder.render_html()
    return HTMLResponse(content=html)

@app.post("/submit")
async def submit_form(request: Request):
    data = await request.json()
    try:
        form = SimpleForm(**data)
        # Here you could process/store the form data
        return JSONResponse({"message": "Success", "data": form.dict()})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
# To run the example, save this code in a file named `example.py` and run it using:

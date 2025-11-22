from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from logic import resolver

app = FastAPI(title="Aviso Entity Resolution Agent")

# 1. Mount the "static" folder
# This tells FastAPI: "Allow the browser to access files inside the 'static' folder"
app.mount("/static", StaticFiles(directory="static"), name="static")

class LeadInput(BaseModel):
    raw_text: str

# 2. Serve the Frontend at the Homepage
@app.get("/")
def home():
    # When someone visits the site, send them the HTML file
    return FileResponse('static/index.html')

# 3. The API Endpoint (The Logic)
@app.post("/resolve")
def resolve_lead(lead: LeadInput):
    """
    Takes raw text (e.g. 'mr. john smith at acme inc') 
    and finds the matching CRM record + Graph connections.
    """
    result = resolver.resolve_entity(lead.raw_text)
    return result
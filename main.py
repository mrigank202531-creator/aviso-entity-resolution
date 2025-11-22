from fastapi import FastAPI
from pydantic import BaseModel
from logic import resolver

app = FastAPI(title="Aviso Entity Resolution Agent")

class LeadInput(BaseModel):
    raw_text: str

@app.get("/")
def home():
    return {"message": "Aviso Entity Resolution API is Running. Go to /docs to test."}

@app.post("/resolve")
def resolve_lead(lead: LeadInput):
    """
    Takes raw text (e.g. 'mr. john smith at acme inc') 
    and finds the matching CRM record + Graph connections.
    """
    result = resolver.resolve_entity(lead.raw_text)
    return result
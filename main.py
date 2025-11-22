from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from logic import resolver
import pandas as pd
import io

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse('static/index.html')

# 1. NEW: Get Database Info (Transparency)
@app.get("/db-info")
def get_db_info():
    return resolver.get_db_preview()

# 2. NEW: Upload & Process CSV
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    # Read the uploaded file into Pandas
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    # Run the bulk cleaning logic
    cleaned_data = resolver.bulk_resolve(df)
    
    return {"filename": file.filename, "results": cleaned_data}

# Keep the single resolve for the 'Manual Search' tab if you want
class LeadInput(BaseModel):
    raw_text: str

@app.post("/resolve")
def resolve_lead(lead: LeadInput):
    res = resolver.resolve_single(lead.raw_text)
    # Add graph logic return for the single search
    if res['match_score'] > 0.6:
        comp = res['match_details']['company']
        if resolver.graph.has_node(comp):
            res['potential_colleagues'] = [n for n in resolver.graph.neighbors(comp)][:3]
    return res
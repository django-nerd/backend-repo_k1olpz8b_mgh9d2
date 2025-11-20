import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from database import create_document

app = FastAPI(title="Kwick Stays Holiday Homes LLC API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"name": "Kwick Stays Holiday Homes LLC", "status": "ok"}

@app.get("/api/hello")
def hello():
    return {"message": "Welcome to Kwick Stays Holiday Homes LLC API"}

# Public schema endpoint for tooling/validation
@app.get("/schema")
def get_schema():
    import inspect, schemas
    models = {}
    for name, obj in inspect.getmembers(schemas):
        try:
            if hasattr(obj, "model_json_schema"):
                models[name] = obj.model_json_schema()
        except Exception:
            continue
    return {"models": models}

# Inquiry endpoint
class InquiryPayload(BaseModel):
    name: str
    email: str
    phone: str | None = None
    message: str
    property_id: str | None = None
    check_in: str | None = None
    check_out: str | None = None
    guests: int | None = None

@app.post("/api/inquiries")
def create_inquiry(payload: InquiryPayload):
    try:
        inquiry_id = create_document("inquiry", payload.model_dump())
        return {"id": inquiry_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# backend/app.py
from fastapi_app import app

if __name__ == "__main__":
    import os, uvicorn
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

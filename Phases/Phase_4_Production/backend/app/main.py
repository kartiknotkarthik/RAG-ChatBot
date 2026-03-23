from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sys

# Path to frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

# Add Phase 2 to sys.path to access the RAGEngine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from Phases.Phase_2_RAG.src.chatbot.rag_engine import RAGEngine

# Initialize the real RAG Engine
try:
    engine = RAGEngine()
except Exception as e:
    print(f"Error initializing RAGEngine: {e}")
    engine = None

app = FastAPI(title="Mutual Fund RAG API", version="1.0.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    source: str
    is_advice: bool

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine_ready": engine is not None}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="RAG Engine not initialized. Please verify your GROQ_API_KEY in .env.")

    # Call the actual RAG Engine logic
    try:
        response_text = engine.handle_query(request.query)
        
        # Check if it was a refusal (advice/pii) or a factual answer
        is_refusal = any(kw in response_text.lower() for kw in ["i apologize", "out of my scope"])
        
        # Robust source extraction for clickable links
        source = "Mutual Fund Data Repository"
        # Search for 'Source:' anywhere in the text (case-insensitive)
        import re
        source_match = re.search(r"Source:\s*(https?://\S+)", response_text, re.IGNORECASE)
        
        if source_match:
            source = source_match.group(1).strip()
            # Clean up potential trailing characters like punctuation
            source = source.rstrip('.,;)]')
            # Remove the source line from the main answer to avoid double display in bubble
            # We replace 'Source: URL' and everything after it on that line
            response_text = re.sub(r"Source:\s*https?://\S+(?:\s|$)(\n*)", "", response_text, flags=re.IGNORECASE).strip()

        return QueryResponse(
            answer=response_text,
            source=source,
            is_advice=is_refusal
        )
    except Exception as e:
        import traceback
        print("Backend Error Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Backend Internal Error: {str(e)}")

# Frontend Routes
@app.get("/app")
async def serve_app():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Static Files (Mount at root but after routes)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Use port 8000 as defined in frontend script.js
    uvicorn.run(app, host="0.0.0.0", port=8000)

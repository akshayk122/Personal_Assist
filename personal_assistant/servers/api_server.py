from fastapi import FastAPI, HTTPException
from acp_sdk.client import Client
from colorama import Fore
import asyncio
import nest_asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personal Assistant API",
    description="API for Personal Assistant with user ID support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

# Apply nest_asyncio to allow running async code in Jupyter
nest_asyncio.apply()

@app.post("/query")
async def handle_query(request: QueryRequest):
    """Handle user query with user ID support - calls orchestrator server"""
    try:
        logger.info(f"Received query: '{request.query}' for user: {request.user_id}")
        
        # Prepare the query with user ID if provided
        if request.user_id:
            query_with_user = f"{request.query} for user: {request.user_id}"
        else:
            query_with_user = request.query
        
        # Call orchestrator server
        async with Client(base_url="http://localhost:8300") as client:
            response = await client.run_sync(
                agent="personal_assistant",
                input=query_with_user
            )
            
            response_content = response.output[0].parts[0].content
            
            return JSONResponse(
                content={
                    "message": response_content,
                    "status": "success",
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "query": request.query,
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Error processing query: {str(e)}",
                "status": "error",
                "user_id": request.user_id,
                "session_id": request.session_id,
                "query": request.query
            }
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Personal Assistant API",
        "version": "1.0.0",
        "endpoints": [
            "/query - General queries with user ID (calls orchestrator)",
            "/health - Health check"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Personal Assistant API",
        "version": "1.0.0",
        "description": "Single endpoint API that calls the orchestrator server",
        "endpoints": {
            "POST /query": "General queries with user ID support (calls orchestrator)",
            "GET /health": "Health check",
            "GET /": "API information"
        },
        "example_request": {
            "query": "Show my expenses",
            "user_id": "user123",
            "session_id": "session456"
        },
        "note": "All queries are routed through the orchestrator server which handles routing to appropriate agents"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Personal Assistant API Server on port 8400...")
    print("📋 Available Endpoints:")
    print("  - POST /query (General queries with user ID - calls orchestrator)")
    print("  - GET /health (Health check)")
    print("  - GET / (API information)")
    print("\n💡 Example usage:")
    print('  curl -X POST "http://localhost:8400/query" \\')
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"query": "Show my expenses", "user_id": "user123"}\'')
    print("\n🎯 All queries are routed through the orchestrator server!")
    uvicorn.run(app, host="0.0.0.0", port=8400)
from fastapi import FastAPI, HTTPException
from acp_sdk.client import Client
from colorama import Fore
import asyncio
import nest_asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply nest_asyncio to allow running async code in Jupyter
nest_asyncio.apply()

@app.get("/query/{user_input:path}")
async def handle_query(user_input: str):
    """Handle user query and return response"""
    async with Client(base_url="http://localhost:8300") as client:
        try:
            response = await client.run_sync(
                agent="personal_assistant",
                input=user_input
            )
            return response.output[0].parts[0].content
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}" + Fore.RESET)
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting API server on port 8400...")
    print("Endpoints:")
    print("  - GET /query/{query} (Send user queries)")
    print("  - GET /health (Health check)")
    uvicorn.run(app, host="0.0.0.0", port=8400)
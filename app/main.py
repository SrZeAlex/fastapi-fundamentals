"""
FastAPI Fundamentals Lab - Main Application
"""

from fastapi import FastAPI
from datetime import datetime

# Create FastAPI instance
app = FastAPI(
    title="FastAPI Fundamentals Lab",
    description="A hands-on lab to learn FastAPI basics",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint - welcome message."""
    return {
        "message": "Welcome to FastAPI Fundamentals Lab!",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/hello/{name}")
async def say_hello(name: str):
    """Greet someone by name."""
    return {"message": f"Hello, {name}!"}

@app.get("/hello")
async def say_hello_query(name: str = "World"):
    """Greet someone using query parameter."""
    return {"message": f"Hello, {name}!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

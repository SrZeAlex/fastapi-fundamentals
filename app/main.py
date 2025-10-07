"""
FastAPI Fundamentals Lab - Main Application
"""

from fastapi import FastAPI
from datetime import datetime

from app.routers import books

# Create FastAPI instance
app = FastAPI(
    title="FastAPI Fundamentals Lab",
    description="""
    A hands-on lab to learn FastAPI basics through a book library API.
    
    ## Features
    
    * **Books**: Full CRUD operations for managing books
    * **Validation**: Comprehensive data validation with Pydantic
    * **Documentation**: Automatic interactive API documentation
    * **Filtering**: Advanced book filtering and pagination
    
    ## Getting Started
    
    1. Create some books using the POST /books/ endpoint
    2. Retrieve books using GET /books/ with optional filters
    3. Update or delete books using PUT and DELETE endpoints
    4. Check library statistics at /books/stats/summary
    """,
    version="1.0.0",
    contact={
        "name": "FastAPI Lab Support",
        "email": "support@fastapi-lab.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Include routers
app.include_router(books.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to FastAPI Fundamentals Lab!",
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "Book management CRUD operations",
            "Advanced filtering and pagination", 
            "Automatic data validation",
            "Interactive API documentation",
            "Library statistics"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

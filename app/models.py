"""
Pydantic models for the book store API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class BookGenre(str, Enum):
    """Book genre enumeration."""
    FICTION = "fiction"
    NON_FICTION = "non-fiction"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    SCIENCE_FICTION = "science-fiction"
    FANTASY = "fantasy"
    BIOGRAPHY = "biography"
    HISTORY = "history"
    TECHNOLOGY = "technology"

class BookBase(BaseModel):
    """Base book model with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    author: str = Field(..., min_length=1, max_length=100, description="Book author")
    genre: BookGenre = Field(..., description="Book genre")
    publication_year: int = Field(..., ge=1000, le=2024, description="Year published")
    pages: int = Field(..., gt=0, le=10000, description="Number of pages")
    isbn: Optional[str] = Field(None, regex=r'^\d{10}(\d{3})?$', description="ISBN-10 or ISBN-13")
    
    @validator('title', 'author')
    def validate_text_fields(cls, v):
        """Validate text fields are not just whitespace."""
        if not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v.strip().title()
    
    @validator('publication_year')
    def validate_publication_year(cls, v):
        """Validate publication year is not in the future."""
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f'Publication year cannot be greater than {current_year}')
        return v

class BookCreate(BookBase):
    """Model for creating a new book."""
    pass

class BookUpdate(BaseModel):
    """Model for updating an existing book."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[BookGenre] = None
    publication_year: Optional[int] = Field(None, ge=1000, le=2024)
    pages: Optional[int] = Field(None, gt=0, le=10000)
    isbn: Optional[str] = Field(None, regex=r'^\d{10}(\d{3})?$')
    
    @validator('title', 'author')
    def validate_text_fields(cls, v):
        """Validate text fields are not just whitespace."""
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v.strip().title() if v else v

class Book(BookBase):
    """Model for book responses."""
    id: int = Field(..., description="Unique book ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "The Python Programming Language",
                "author": "Guido Van Rossum",
                "genre": "technology",
                "publication_year": 2020,
                "pages": 450,
                "isbn": "9781234567890",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": None
            }
        }

class BookListResponse(BaseModel):
    """Response model for book list with pagination."""
    books: List[Book]
    total: int = Field(..., description="Total number of books")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "books": [
                    {
                        "id": 1,
                        "title": "FastAPI Guide",
                        "author": "Sebastian Ramirez",
                        "genre": "technology",
                        "publication_year": 2023,
                        "pages": 300,
                        "isbn": "9781234567890",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": None
                    }
                ],
                "total": 25,
                "page": 1,
                "limit": 10,
                "has_next": True
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Application-specific error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Book not found",
                "error_code": "BOOK_NOT_FOUND",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

"""
Book management endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List, Optional
from datetime import datetime
import uuid

from app.models import (
    Book, BookCreate, BookUpdate, BookListResponse, 
    BookGenre, ErrorResponse
)

# Create router
router = APIRouter(prefix="/books", tags=["books"])

# In-memory storage (for demo purposes)
books_db: List[Book] = []
next_id = 1

def get_next_id() -> int:
    """Get next available ID."""
    global next_id
    current = next_id
    next_id += 1
    return current

@router.post(
    "/",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    description="Add a new book to the library with automatic validation",
    responses={
        201: {"description": "Book created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid book data"},
        422: {"description": "Validation error"}
    }
)
async def create_book(book: BookCreate) -> Book:
    """
    Create a new book in the library.
    
    - **title**: Book title (1-200 characters)
    - **author**: Author name (1-100 characters)
    - **genre**: Book genre from predefined list
    - **publication_year**: Year published (1000-current year)
    - **pages**: Number of pages (1-10,000)
    - **isbn**: Optional ISBN-10 or ISBN-13
    """
    # Check for duplicate ISBN
    if book.isbn:
        existing_book = next((b for b in books_db if b.isbn == book.isbn), None)
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {book.isbn} already exists"
            )
    
    # Create new book
    new_book = Book(
        id=get_next_id(),
        **book.model_dump(),
        created_at=datetime.now()
    )
    
    books_db.append(new_book)
    return new_book

@router.get(
    "/",
    response_model=BookListResponse,
    summary="Get books with filtering and pagination",
    description="Retrieve books with optional filtering by genre, author, or publication year"
)
async def get_books(
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of books to return"),
    genre: Optional[BookGenre] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, min_length=1, description="Filter by author name"),
    year: Optional[int] = Query(None, ge=1000, le=2024, description="Filter by publication year")
) -> BookListResponse:
    """
    Get a list of books with optional filtering.
    
    Supports pagination and filtering by:
    - **genre**: Book genre
    - **author**: Author name (partial match)
    - **year**: Publication year
    """
    # Apply filters
    filtered_books = books_db.copy()
    
    if genre:
        filtered_books = [b for b in filtered_books if b.genre == genre]
    
    if author:
        author_lower = author.lower()
        filtered_books = [b for b in filtered_books if author_lower in b.author.lower()]
    
    if year:
        filtered_books = [b for b in filtered_books if b.publication_year == year]
    
    # Pagination
    total = len(filtered_books)
    paginated_books = filtered_books[skip:skip + limit]
    has_next = skip + limit < total
    
    return BookListResponse(
        books=paginated_books,
        total=total,
        page=(skip // limit) + 1,
        limit=limit,
        has_next=has_next
    )

@router.get(
    "/{book_id}",
    response_model=Book,
    summary="Get a specific book",
    description="Retrieve a book by its ID",
    responses={
        200: {"description": "Book found"},
        404: {"model": ErrorResponse, "description": "Book not found"}
    }
)
async def get_book(
    book_id: int = Path(..., gt=0, description="Book ID")
) -> Book:
    """Get a specific book by ID."""
    book = next((b for b in books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book

@router.put(
    "/{book_id}",
    response_model=Book,
    summary="Update a book",
    description="Update an existing book with new information",
    responses={
        200: {"description": "Book updated successfully"},
        404: {"model": ErrorResponse, "description": "Book not found"},
        400: {"model": ErrorResponse, "description": "Invalid update data"}
    }
)
async def update_book(
    book_id: int = Path(..., gt=0, description="Book ID"),
    book_update: BookUpdate = ...
) -> Book:
    """Update an existing book."""
    book_index = next((i for i, b in enumerate(books_db) if b.id == book_id), None)
    if book_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    # Check ISBN uniqueness if updating
    if book_update.isbn:
        existing_book = next((b for b in books_db if b.isbn == book_update.isbn and b.id != book_id), None)
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {book_update.isbn} already exists"
            )
    
    # Update book
    existing_book = books_db[book_index]
    update_data = book_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(existing_book, field, value)
    
    existing_book.updated_at = datetime.now()
    
    return existing_book

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description="Remove a book from the library",
    responses={
        204: {"description": "Book deleted successfully"},
        404: {"model": ErrorResponse, "description": "Book not found"}
    }
)
async def delete_book(
    book_id: int = Path(..., gt=0, description="Book ID")
):
    """Delete a book from the library."""
    book_index = next((i for i, b in enumerate(books_db) if b.id == book_id), None)
    if book_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    books_db.pop(book_index)
    return None

# Statistics endpoints
@router.get(
    "/stats/summary",
    summary="Get library statistics",
    description="Get summary statistics about the book library"
)
async def get_library_stats():
    """Get library statistics."""
    if not books_db:
        return {
            "total_books": 0,
            "genres": {},
            "average_pages": 0,
            "publication_year_range": None
        }
    
    # Calculate statistics
    total_books = len(books_db)
    
    # Genre distribution
    genre_counts = {}
    for book in books_db:
        genre_counts[book.genre] = genre_counts.get(book.genre, 0) + 1
    
    # Average pages
    total_pages = sum(book.pages for book in books_db)
    average_pages = round(total_pages / total_books) if total_books > 0 else 0
    
    # Publication year range
    years = [book.publication_year for book in books_db]
    year_range = {
        "earliest": min(years),
        "latest": max(years)
    }
    
    return {
        "total_books": total_books,
        "genres": genre_counts,
        "average_pages": average_pages,
        "publication_year_range": year_range
    }

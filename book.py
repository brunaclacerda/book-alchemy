import logging
from datetime import date

import author
import data_models as models
from data_models import Book

logger = logging.getLogger(__name__)


def get_all(user_sort: dict | None = None) -> list[Book]:
    """
    Get all books

    Args
        sort: order and direction parameters

    Return
        List of books
    """
    try:
        logger.debug("Getting all books.")
        books = models.select_book_author(sort=user_sort)

        return {"data": books}
    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error.", "code": 500}


def get_book(book_id: int) -> list[Book]:
    """
    Get book by its id

    Return
        Book found.
    """
    try:
        book_found = models.get_book_by_id(int(book_id))

        return {"data": book_found}
    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error.", "code": 500}


def validate_book(book: dict, new=False) -> str | None:
    """
    Validate user input for creating or editing a book

    """
    logger.debug("Validating user input")
    if "title" not in book and new:
        return {"error": "Title of book must be provided."}

    if "publication_year" in book and book.get("publication_year", None):
        publication_year = book["publication_year"]
        curr_year = date.today().year
        if publication_year and int(publication_year) > curr_year:
            return {"error": f"Publication year should not be superior to: {curr_year}"}

    if "rating" in book and book.get("rating", None):
        logger.debug("Rating: %s", book["rating"])
        if isinstance(book["rating"], str) and not book["rating"].isnumeric():
            return {"error": "Rating must be a number."}
        elif int(book["rating"]) < 1 or int(book["rating"]) > 10:
            return {"error": "Rating value must be between 1 and 10."}

    return None


def create(new_book: dict) -> Book | dict:
    """
    Create a new book.
    Args
        new_book: Dictionary with Book data.

    Return
        Book created or error
    """
    try:
        error = validate_book(new_book, new=True)
        if error:
            error["code"] = 400
            return error

        book = Book(
            title=new_book["title"],
            isbn=new_book.get("isbn", None),
            publication_year=new_book.get("publication_year", None),
            author_id=new_book.get("author_id", None),
            rating=new_book.get("rating", None),
        )
        logger.debug(book)
        logger.debug("Saving book.")
        book.save()
        return {"data": book}

    except (TypeError, ValueError) as e:
        logger.error(e)
        return {"error": "Invalid input provided."}
    except Exception as e:
        logger.error("Error creating a new book: %s", e)
        return {"error": "Unexpected error."}


def delete_book(book_id: int) -> dict | None:
    """
    Delete a book providing its ID.
    Args
        book_id: Book ID

    Return
        None for success and error dictionary if failure.
    """
    try:
        book = models.get_book_by_id(int(book_id))
        if not book:
            logger.debug("Book %i not found.", book_id)
            return {"error": f"Book with id {book_id} not found.", "code": "404"}

        book.delete()
        author.check_author_has_books(book.author_id)
        return None

    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error.", "code": 500}


def edit(book_id: int, updates: dict) -> dict:
    """
    Edit a book providing its ID.
    Args
        book_id: Book ID
        updates: Dictionary with the books updates

    Return
        Book updated or error
    """
    try:
        book = models.get_book_by_id(int(book_id))
        if not book:
            logger.debug("Book %i not found.", book_id)
            return {"error": f"Book with id {book_id} not found.", "code": "404"}

        error = validate_book(updates)
        if error:
            error["code"] = 400
            logger.debug(error)
            return error

        if "title" in updates:
            book.title = updates["title"]
        if "isbn" in updates:
            book.isbn = updates["isbn"]
        if "publication_year" in updates:
            book.publication_year = updates["publication_year"]
        if "author_id" in updates:
            book.author_id = updates["author_id"]
        if "rating" in updates:
            book.rating = updates["rating"]

        book.save()
        return {"data": book}

    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error.", "code": 500}


def search_book(query: str) -> list[Book]:
    """
    Get all books that match search criteria. Partial text is accepted.

    Args
        query: Author name or title of the book.

    Return
        List of books
    """
    try:
        logger.debug("Getting all books.")
        books = models.select_book_author(search_criteria=query)

        return {"data": books}
    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error.", "code": 500}

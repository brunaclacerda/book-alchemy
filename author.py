import logging
from datetime import date

from sqlalchemy.exc import OperationalError

import data_models as models
from data_models import Author
from setup import db

logger = logging.getLogger(__name__)


def create(new_author: dict):
    """
    Create a new author
    Args:
        new_author: Dictionary with Author attributes
    Return:
        Object saved on the db
    """
    try:
        logger.debug("Creating a new author")
        if "birth_date" in new_author:
            birth_date = date.fromisoformat(new_author["birth_date"])
        else:
            birth_date = None
        if "date_of_death" in new_author and new_author["date_of_death"]:
            date_of_death = date.fromisoformat(new_author["date_of_death"])
        else:
            date_of_death = None

        author = Author(
            name=new_author.get("iname", None),
            birth_date=birth_date,
            date_of_death=date_of_death,
        )

        logger.debug("Saving new record %s.", author)
        author.save()
        logger.debug("Author ID: %i", author.id)

        return {"data": author}

    except (TypeError, ValueError) as e:
        logger.error(e)
        return {"error": "Invalid input provided."}
    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error."}


def delete_author(author_id: int) -> dict | None:
    try:
        author = models.get_author_by_id(int(author_id))
        if not author:
            logger.debug("Author %i not found.", author_id)
            return {"error": f"Author with id {author_id} not found.", "code": 404}

        author.delete()

    except OperationalError as e:
        logger.error(e)
        return {"error": "DB communication error.", "code": 500}
    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error.", "code": 500}


def get_all() -> list[Author]:
    """
    Get all authors

    Return
        List of authors
    """
    try:
        authors = Author.select_all()

        return {"data": authors}
    except Exception as e:
        logger.error(e)
        return {"error": "Unexpected error.", "code": 500}


def check_author_has_books(author_id: int) -> None:
    """
    Check if the author has any books in the library.
    If no books found the author is deleted.

    Args:
        author_id: Author ID

    Return
        None
    """

    try:
        logger.debug("Checking if author has books in the library.")
        author = models.get_author_by_id(author_id)
        if not author:
            return
        if author.count_books() == 0:
            logger.debug("No books found for author %i %s", author.id, author.name)
            logger.debug("Deleting author.")
            author.delete()
        return

    except Exception as e:
        logger.error(e)

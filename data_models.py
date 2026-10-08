import logging
from datetime import date
from typing import Optional

from sqlalchemy import ForeignKey, desc, func, or_, select
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

from setup import db

logger = logging.getLogger(__name__)


class Author(db.Model):
    """
    Class for mapping author table

    Attributes:
        id: Unique ID, autoincrement
        name: Name of the author, required
        birth_date: Date of birth, Optional
        date_of_death: Date of death, Optional

    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column()
    date_of_death: Mapped[Optional[date]] = mapped_column()

    def __str__(self):
        return (
            f"Author ID: {self.id}, name: {self.name}, Birth date: {self.birth_date},"
            f"Death date: {self.date_of_death}"
        )

    def count_books(self) -> int:
        stmt = select(func.count(Book.id)).where(Book.author_id == self.id)

        nr_books = db.session.scalar(stmt)
        logger.debug("Author has %s books", nr_books)
        return nr_books


class Book(db.Model):
    """
    Book Class

    Attributes
        id: Unique ID
        isbn: ISBN
        title: Title
        publication_year: Publication year
        author_id: Author of the book

    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    isbn: Mapped[Optional[str]] = mapped_column()
    title: Mapped[str] = mapped_column()
    publication_year: Mapped[int] = mapped_column()
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))

    author: Mapped["Author"] = relationship()

    def __str__(self):
        return (
            f"Book ID: {self.id}, title: {self.title}, ISBN: {self.isbn}, "
            f"Publication Year: {self.publication_year}, Author ID: {self.author_id}"
        )


def select_book_author(
    search_criteria: str | None = None, sort: dict | None = None
) -> list:
    """
    Select books with author name
    """
    logger.debug("Selecting Book table")
    stmt = select(Book).options(joinedload(Book.author))
    if search_criteria:
        condition = f"%{search_criteria}%"
        stmt = stmt.where(
            or_(
                Book.author.has(Author.name.ilike(condition)),
                Book.title.ilike(condition),
            )
        )
    if sort and sort["order"]:
        logger.debug("Sorting.")
        if sort["direction"] == "asc":
            stmt = stmt.order_by(sort["order"])
        else:
            stmt = stmt.order_by(desc(sort["order"]))
    records = db.session.execute(stmt).scalars().all()

    logger.debug(records)
    return records


def get_book_by_id(book_id: int) -> Book:
    """
    Select book by its ID
    Args
        book_id: Book ID

    Return
        Book

    Raises

    """
    stmt = select(Book).where(Book.id == book_id)
    return db.session.execute(stmt).scalar_one_or_none()


def get_author_by_id(author_id: int) -> Author:
    """
    Select author by its ID
    Args
        author_id: author ID

    Return
        author

    Raises

    """
    stmt = select(Author).where(Author.id == author_id)
    return db.session.execute(stmt).scalar_one_or_none()

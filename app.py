import logging
import os
from datetime import date

from flask import Flask, flash, jsonify, redirect, render_template, request

import author
import book
from setup import db

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# DB setup
# Implement .env
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "BOOKALCHEMY_DATABASE_URI",
    f"sqlite:///{os.path.join(BASEDIR, 'data/library.sqlite')}",
)
db.init_app(app)


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# implement .env
app.secret_key = "wwd96Se3WBNQQDP++K1OdORq7pP1kAB7kI/IEPkLIPhWj6xbNi9b5r5dJxv6yUhm"


@app.route("/")
def home():
    """
    GET
        Index page
    """
    sort = None
    if request.args and request.args.get("order", None):
        sort = {
            "order": request.args["order"],
            "direction": request.args.get("direction", "asc"),
        }
    logger.debug(sort)
    books = book.get_all(user_sort=sort)
    authors = author.get_all()

    return render_template("index.html", books=books["data"], authors=authors["data"])


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    GET
        Return the template

    POST
        Create a new book
    """
    if request.method == "GET":
        return render_template(
            "add_book.html", form_action="add_book", curr_year=date.today().year
        )

    if request.form:
        result = book.create(request.form)
        if result.get("error", None):
            return jsonify({"error": result["error"]}), 400

        flash("Book created successfully.")
        return redirect("/")

    return jsonify({"error": "Invalid request."}), 400


@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    """
    GET
        Return the template

    POST
        Update a book
    """
    if request.method == "GET":
        logger.debug("Return edit book template")
        book_to_edit = book.get_book(book_id)
        if book_to_edit.get("data", None):
            return render_template(
                "add_book.html",
                curr_year=date.today().year,
                form_action="edit_book",
                book=book_to_edit["data"],
            )
        return jsonify({"error": "Book not found."}), 404

    if request.form:
        result = book.edit(book_id, request.form)
        if result and result.get("error", None):
            flash(result["error"], "error")
        else:
            flash("Book updated successfully.", "success")
        return redirect("/")

    return jsonify({"error": "Invalid request."}), 400


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Delete a book by id
    """

    result = book.delete_book(book_id)
    if result and result.get("error", None):
        flash(result["error"], "error")
    else:
        flash("Book deleted successfully.", "success")
    return redirect("/")


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    GET
        Return the template

    POST
        Create a new author
    """
    if request.method == "GET":
        return render_template("add_author.html")

    if request.form:
        result = author.create(request.form)
        if result.get("error", None):
            return jsonify({"error": result["error"]}), 400

        flash("New author saved.")
        return redirect("/")

    return jsonify({"error": "Invalid request."}), 400


@app.get("/author")
def get_author():
    """
    GET
        Return list of authors
    """
    result = author.get_all()
    if result.get("error", None):
        return jsonify(result["error"]), result["code"]

    return jsonify(result["data"])


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    """
    Delete a author by id
    """
    logger.debug("Deleting author %i", author_id)
    result = author.delete_author(author_id)
    if result and result.get("error", None):
        flash(result["error"], "error")
    else:
        flash("Author deleted successfully.", "success")
    return redirect("/")


@app.route("/search")
def search():
    """
    Search a book by author name or book's title
    """
    query = request.args.get("criteria", None)
    books = book.search_book(query=query).get("data", [])
    if not books:
        flash("None books found.", "success")
    authors = author.get_all().get("data", [])

    return render_template("index.html", books=books, authors=authors)


@app.post("/rate/<int:book_id>")
def rate_book(book_id):
    if request.form and request.form.get("rating", None):
        result = book.edit(book_id, {"rating": request.form.get("rating", None)})
        if result and result.get("error", None):
            flash(result["error"], "error")
    else:
        flash("No valid rating value provided.", "error")
    return redirect("/")


if __name__ == "__main__":
    # create tables
    # with app.app_context():
    #     db.create_all()

    app.run(debug=True)

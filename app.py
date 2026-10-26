import re
import os
import uuid
from decimal import Decimal, InvalidOperation
from functools import wraps

import bcrypt
import pymysql
from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymysql.constants import CLIENT
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024      

UPLOAD_DIR = os.path.join(app.static_folder, "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def format_price(value):
    return f"{value:,.2f} EGP"

app.jinja_env.filters["egp"] = format_price

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

EMAIL_PATTERN = re.compile(r"^[^@ ]+@[^@ .]+([.][^@ .]+)+$")


def get_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                        database=DB_NAME, cursorclass=pymysql.cursors.DictCursor,
                        client_flag=CLIENT.FOUND_ROWS)


def run(sql, params=(), fetch=False):
    """Run one SQL statement. SELECT -> list of rows, otherwise -> rows matched."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper



@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("books"))
    if request.method == "GET":
        return render_template("login.html", errors={}, email="")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = {}
    if email == "":
        errors["email"] = "Email is required"
    elif not EMAIL_PATTERN.match(email):
        errors["email"] = "Email is not valid"
    if password == "":
        errors["password"] = "Password is required"
    if errors:
        return render_template("login.html", errors=errors, email=email)

    rows = run("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,), fetch=True)
    user = rows[0] if rows else None
    if user is None or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return render_template("login.html", errors={"form": "Invalid email or password"}, email=email)

    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect(url_for("books"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("books"))
    if request.method == "GET":
        return render_template("register.html", errors={}, name="", email="")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = {}
    if name == "":
        errors["name"] = "Name is required"
    if email == "":
        errors["email"] = "Email is required"
    if password == "":
        errors["password"] = "Password is required"
    if confirm_password == "":
        errors["confirm_password"] = "Confirm password is required"
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match"
    if errors:
        return render_template("register.html", errors=errors, name=name, email=email)

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                    (email, name, password_hash))
        conn.commit()
        new_user_id = cur.lastrowid
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            return render_template("register.html", errors={"email": "Email Already Exists"},
                                name=name, email=email)
        raise
    finally:
        conn.close()

    session["user_id"] = new_user_id
    session["name"] = name
    return redirect(url_for("books"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))



def image_error(file):
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXT:
            return "Image must be png, jpg, jpeg, gif or webp"
    return None


def save_image(file):
    """Save an uploaded image with a random name and return that name (or None)."""
    if not file or not file.filename:
        return None
    name = uuid.uuid4().hex + "." + file.filename.rsplit(".", 1)[-1].lower()
    file.save(os.path.join(UPLOAD_DIR, name))
    return name


def remove_image(name):
    if name:
        path = os.path.join(UPLOAD_DIR, name)
        if os.path.exists(path):
            os.remove(path)



@app.route("/books")
@login_required
def books():
    rows = run("SELECT book_id, title, price, author_id, cover FROM book ORDER BY book_id", fetch=True)
    # a second simple SELECT (no JOIN) gives us the author names
    names = {a["author_id"]: a["name"] for a in run("SELECT author_id, name FROM author", fetch=True)}
    return render_template("books.html", books=rows, names=names)


def read_book_form():
    book = {"title": request.form.get("title", "").strip(),
            "price": request.form.get("price", "").strip(),
            "author_id": request.form.get("author_id", "").strip()}
    errors = {}
    if book["title"] == "":
        errors["title"] = "Title is required"
    elif len(book["title"]) > 200:
        errors["title"] = "Title is too long (200 characters at most)"
    try:
        price = Decimal(book["price"])
        if not price.is_finite() or price < 0 or price > Decimal("99999999.99"):
            raise InvalidOperation
    except InvalidOperation:
        errors["price"] = "Price must be a number between 0 and 99999999.99"
    if not book["author_id"].isdigit():
        errors["author_id"] = "Choose an author"
    return book, errors


@app.route("/books/add", methods=["GET", "POST"])
@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
def book_form(book_id=None):
    authors = run("SELECT author_id, name FROM author ORDER BY name", fetch=True)
    book, errors = {"title": "", "price": "", "author_id": "", "cover": None}, {}

    if book_id is not None:
        rows = run("SELECT title, price, author_id, cover FROM book WHERE book_id = %s", (book_id,), fetch=True)
        if not rows:
            flash("Book not found.")
            return redirect(url_for("books"))
        book = rows[0]
    old_cover = book["cover"]

    if request.method == "POST":
        file = request.files.get("cover")
        book, errors = read_book_form()
        book["cover"] = old_cover
        if image_error(file):
            errors["cover"] = image_error(file)
        if not errors:
            saved = save_image(file)
            cover = saved or old_cover
            try:
                if book_id is None:
                    run("INSERT INTO book (title, price, author_id, cover) VALUES (%s, %s, %s, %s)",
                        (book["title"], book["price"], book["author_id"], cover))
                    flash("Book added.")
                else:
                    run("UPDATE book SET title = %s, price = %s, author_id = %s, cover = %s WHERE book_id = %s",
                        (book["title"], book["price"], book["author_id"], cover, book_id))
                    flash("Book updated.")
                if saved:
                    remove_image(old_cover)
                return redirect(url_for("books"))
            except pymysql.err.IntegrityError:
                remove_image(saved)
                errors["author_id"] = "This author does not exist"

    return render_template("book_form.html", book=book, errors=errors, authors=authors,
                        editing=book_id is not None)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
@login_required
def delete_book(book_id):
    rows = run("SELECT cover FROM book WHERE book_id = %s", (book_id,), fetch=True)
    deleted = run("DELETE FROM book WHERE book_id = %s", (book_id,))
    if rows:
        remove_image(rows[0]["cover"])
    flash("Book deleted." if deleted else "Book not found.")
    return redirect(url_for("books"))



@app.route("/authors")
@login_required
def authors():
    rows = run("SELECT author_id, name, country, photo FROM author ORDER BY author_id", fetch=True)

    def image_url(name):
        return url_for("static", filename="uploads/" + name) if name else None

    books_by_author = {}
    for b in run("SELECT title, price, author_id, cover FROM book ORDER BY title", fetch=True):
        books_by_author.setdefault(b["author_id"], []).append(
            {"title": b["title"], "price": format_price(b["price"]), "cover": image_url(b["cover"])})
    author_data = {a["author_id"]: {"name": a["name"], "country": a["country"] or "",
                                    "photo": image_url(a["photo"]),
                                    "books": books_by_author.get(a["author_id"], [])} for a in rows}
    return render_template("authors.html", authors=rows, author_data=author_data)


@app.route("/authors/add", methods=["GET", "POST"])
@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
@login_required
def author_form(author_id=None):
    author, errors = {"name": "", "country": "", "photo": None}, {}

    if author_id is not None:
        rows = run("SELECT name, country, photo FROM author WHERE author_id = %s", (author_id,), fetch=True)
        if not rows:
            flash("Author not found.")
            return redirect(url_for("authors"))
        author = rows[0]
    old_photo = author["photo"]

    if request.method == "POST":
        file = request.files.get("photo")
        author = {"name": request.form.get("name", "").strip(),
                "country": request.form.get("country", "").strip(), "photo": old_photo}
        if author["name"] == "":
            errors["name"] = "Name is required"
        elif len(author["name"]) > 100:
            errors["name"] = "Name is too long (100 characters at most)"
        if len(author["country"]) > 50:
            errors["country"] = "Country is too long (50 characters at most)"
        if image_error(file):
            errors["photo"] = image_error(file)
        if not errors:
            saved = save_image(file)
            photo = saved or old_photo
            country = author["country"] or None
            if author_id is None:
                run("INSERT INTO author (name, country, photo) VALUES (%s, %s, %s)",
                    (author["name"], country, photo))
                flash("Author added.")
            else:
                run("UPDATE author SET name = %s, country = %s, photo = %s WHERE author_id = %s",
                    (author["name"], country, photo, author_id))
                flash("Author updated.")
            if saved:
                remove_image(old_photo)
            if author_id is None and request.args.get("next") == "book":
                return redirect(url_for("book_form"))      # back to the Add book form
            return redirect(url_for("authors"))

    return render_template("author_form.html", author=author, errors=errors, editing=author_id is not None)


@app.route("/authors/<int:author_id>/delete", methods=["POST"])
@login_required
def delete_author(author_id):
    photo = run("SELECT photo FROM author WHERE author_id = %s", (author_id,), fetch=True)
    covers = run("SELECT cover FROM book WHERE author_id = %s", (author_id,), fetch=True)
    # ON DELETE CASCADE in the book table removes this author's books too
    deleted = run("DELETE FROM author WHERE author_id = %s", (author_id,))
    if deleted:
        for row in photo:
            remove_image(row["photo"])
        for row in covers:
            remove_image(row["cover"])
    flash("Author and their books deleted." if deleted else "Author not found.")
    return redirect(url_for("authors"))


if __name__ == "__main__":
    app.run(debug=True)

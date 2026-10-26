# Lab 3: Library Management Application

A Flask and MySQL web application for managing a small library: its **authors** and their **books**. Users register, log in, and then view, add, edit, and delete books and authors, with optional cover and photo images.

## 1. Team Members

Team Member 1: Youssef Ashraf Attia  2304083

Team Member 2: Mohamed Abdellatief   2304027

We worked together on the database design and SQL scripts, the implementation of the website (back end, front end, and database integration), testing, and debugging. The website continues our Lab 2 application: the login and register pages are kept, and the to-do list was replaced by the library pages.

## 2. Project Idea

The library keeps two kinds of records:

- **Authors:** an ID, a name, a country, and an optional photo.
- **Books:** an ID, a title, a price, an optional cover, and the author who wrote it.

Every book belongs to one author, and one author can have many books. This is a one-to-many relationship, implemented with a **foreign key** from `book.author_id` to `author.author_id`. The database guarantees that a book can never point to an author that does not exist, and when an author is deleted, all of their books are deleted too (`ON DELETE CASCADE`).

## 3. Technologies Used

- Back end: Python, Flask
- Front end: HTML, CSS, JavaScript
- Database: MySQL
- Database connector: PyMySQL
- Password hashing: bcrypt
- Environment configuration: python-dotenv (`.env`)

## 4. Project Structure

```text
lab3-<student-id>/
├── problem2_DDL.sql
├── problem2_DML.sql
├── README.md
└── website/
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── static/
    │   ├── css/style.css
    │   ├── js/
    │   │   ├── login.js
    │   │   ├── register.js
    │   │   └── library.js
    │   └── uploads/          (created automatically, holds the uploaded images)
    └── templates/
        ├── base.html
        ├── macros.html
        ├── login.html
        ├── register.html
        ├── books.html
        ├── book_form.html
        ├── authors.html
        └── author_form.html
```

## 5. Database

| File | What it does |
| --- | --- |
| `problem2_DDL.sql` | Creates the `library` database with the `author` and `book` tables (primary keys and the foreign key), and a `users` table used only by the login and register pages |
| `problem2_DML.sql` | Inserts sample data: 4 authors and 8 books |

The DDL script starts with `DROP DATABASE IF EXISTS library`, so it can be re-run at any time. **Warning:** this deletes the existing `library` database and all its data before recreating it, so after re-running it you must register a new account.

## 6. Setup and Run from a Fresh Machine

### Requirements

Install Python 3, MySQL Server, and Git. During setup, make sure the Python and MySQL commands are available from the terminal.

### Step 1 — Get the project

Clone the GitHub repository, or download and extract its ZIP file. Open a terminal in the project folder.

```bash
git clone <GITHUB_REPOSITORY_URL>
cd <PROJECT_FOLDER>
```

### Step 2 — Create the database

1. Start MySQL Server.
2. Open MySQL Workbench or a MySQL terminal using an account allowed to create databases.
3. Run the DDL script first and then the DML script.

From a terminal where the MySQL client is installed:

```bash
mysql -u root -p < problem2_DDL.sql
mysql -u root -p < problem2_DML.sql
```

In MySQL Workbench: `File > Open SQL Script`, choose the file, and run the whole script with the first lightning icon.

### Step 3 — Create and activate a virtual environment (recommended)

Open a terminal inside the `website` folder.

**Windows Command Prompt:**

```bat
py -m venv .venv
.venv\Scripts\activate
```

**Windows PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 4 — Install Python packages

```bash
python -m pip install -r requirements.txt
```

### Step 5 — Configure environment variables

Copy `.env.example` to `.env`:

**Windows Command Prompt:**

```bat
copy .env.example .env
```

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

Edit `.env` and enter the credentials for your local MySQL installation. Set a long, random `SECRET_KEY` value. Do not commit or upload `.env`; only commit `.env.example` with placeholder values.

```dotenv
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library
SECRET_KEY=replace-with-a-long-random-secret
```

### Step 6 — Start Flask

```bash
python app.py
```

Open the local address shown by Flask, normally:

http://127.0.0.1:5000/

The home route redirects to the login page. Register a new account, then use the **Books** and **Authors** tabs.

## 7. Features

### Accounts

- **Register:** create an account with name, email, password, and confirmation. A duplicate email is rejected.
- **Login and logout:** passwords are checked against a bcrypt hash. All library pages require login.

### Books

- **View:** a table showing the book ID, title, price, author ID, and author name.
- **Add:** title, price, and an author chosen from a list. The list ends with a "+ Add a new author..." option that opens the Add author page and returns to the book form after saving.
- **Edit:** change the title, price, or author in a form filled with the current values.
- **Delete:** remove a book with the trash icon, after a confirmation message.

### Authors

- **View:** a table showing the author ID, name, and country.
- **Add and edit:** name and country.
- **Delete:** remove an author after confirmation. All of the author's books are deleted too.
- **Pop-up:** click an author to open a window with all the books of that author.

### Images

- **Upload:** a cover for each book and a photo for each author (png, jpg, jpeg, gif or webp, up to 5 MB).
- **Storage:** the files are saved in `website/static/uploads/` and only the file name is stored in the database (`book.cover`, `author.photo`).
- **Cleanup:** an image file is deleted together with its book or author, or when it is replaced.

### Interface

- **List and grid view:** both pages can be switched between a table and a grid of cards, and the choice is remembered in the browser.
- **Icon buttons:** edit (pencil) and delete (trash) icons in every row and card.
- **Messages:** a short confirmation after every add, edit, and delete.

### Validation and Security

- **Validation:** required fields, title and name length, and a numeric price are checked on the server, with an error message under the field.
- **SQL:** only simple, parameterized `SELECT`, `INSERT`, `UPDATE`, and `DELETE` statements are used.
- **Passwords:** stored as bcrypt hashes, never as plain text.

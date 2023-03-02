from sqlalchemy import insert, select, update
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from functions import login_required, apology
from werkzeug.security import check_password_hash, generate_password_hash
from db_init import db_init
from sys import stdout

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Initialise database and tables
engine, users_table, destinations_table = db_init()


@app.route("/")
def index():
    """Homepage"""
    if session.get("user_id") is None:
        return render_template("index.html")
    else:
        return redirect("/dest")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            return apology("Must provide username and password!")
        elif password != confirmation:
            return apology("Passwords do not match!")
        print(username, password, confirmation)
        # Check if username already exists
        with engine.begin() as db:
            result = db.execute(
                select(users_table.c.id).where(users_table.c.username == username)
            ).all()
            print(result, stdout.flush())
            # result = db.execute(
            #    text('SELECT id FROM users WHERE username = :u'), {'u': username})
            if len(result) > 0:
                return apology("Username already exists")
            else:
                hash = generate_password_hash(password)
                print(hash, stdout.flush())
                db.execute(insert(users_table).values(username=username, hash=hash))
                print(
                    insert(users_table).values(username=username, hash=hash),
                    stdout.flush(),
                )
                db.commit()
                return redirect("/login")


def register_user(username, password, db):
    """Add user to DB"""
    hash = generate_password_hash(password)
    db.execute(insert(users_table).values(username=username, hash=hash))
    db.commit()


def check_if_username_exists(db, username):
    """Check is username already exists in DB"""
    result = db.execute(
        select(users_table.c.id).where(users_table.c.username == username)
    ).all()
    return len(result) > 0


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        with engine.begin() as db:
            password = str(request.form.get("password"))
            username = str(request.form.get("username"))
            rows = db.execute(
                select(users_table.c["id", "hash"]).where(
                    users_table.c.username == username
                )
            ).all()
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0][1], password):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0][0]

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/pwdchange", methods=["GET", "POST"])
def pwdchange():
    """Change user's password"""
    if request.method == "GET":
        return render_template("pwdchange.html")
    else:
        with engine.begin() as db:
            hash = db.execute(
                select(users_table.c.hash).where(users_table.c.id == session["user_id"])
            ).scalar()
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")
            confirmation = request.form.get("confirmation")
            if not old_password or not new_password or not confirmation:
                return apology("Must provide old and new passwords", 403)
            elif not check_password_hash(hash, old_password):  # type: ignore
                return apology("Invalid password", 403)
            elif new_password != confirmation:
                return apology("Passwords do not match!", 403)
            new_hash = generate_password_hash(new_password)
            db.execute(
                update(users_table)
                .where(users_table.c.id == session["user_id"])
                .values(hash=new_hash)
            )
            db.commit()
            return redirect("/")


@app.route("/blank")
def blank():
    """Blank page"""
    return render_template("blank.html")


@login_required
@app.route("/dest")
def dest():
    """Destinations page"""
    return render_template("dest.html")


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False)

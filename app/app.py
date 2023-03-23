from sqlalchemy import and_, delete, insert, select, update
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from .etc.functions import login_required, apology
from werkzeug.security import check_password_hash, generate_password_hash
from .etc.db_init import db_init


# from sys import stdout, stderr # - used for print() when debugging

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Debug and test mode enabled - REMOVE WHEN DEPLOYED!
app.debug = True
app.testing = True

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


@app.errorhandler(404)
def not_found(e):
    """404 handler"""
    return apology("Page not found", 404)


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
            if check_if_username_exists(db, username):
                return apology("Username already exists")
            else:
                register_user(username, password, db)

                # Remember which user has registered and log they in
                session["user_id"] = db.execute(
                    select(users_table.c["id"]).where(
                        users_table.c.username == username
                    )
                ).all()[0][0]
                return redirect("/login")


def register_user(username, password, db):
    """Add user to DB"""
    hash = generate_password_hash(password)
    db.execute(insert(table=users_table).values(username=username, hash=hash))
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
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

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
                return apology("Invalid username and/or password", 403)

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
        # Return password change form
        return render_template("pwdchange.html")
    else:
        # Change the password
        with engine.begin() as db:
            hash = db.execute(
                select(users_table.c.hash).where(users_table.c.id == session["user_id"])
            ).scalar()
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")
            confirmation = request.form.get("confirmation")
            # Check input for valifity
            if not old_password or not new_password or not confirmation:
                return apology("Must provide old and new passwords", 403)
            elif not check_password_hash(hash, old_password):  # type: ignore
                return apology("Invalid password", 403)
            elif new_password != confirmation:
                return apology("Passwords do not match!", 403)
            # Update database with new password
            new_hash = generate_password_hash(new_password)
            db.execute(
                update(users_table)
                .where(users_table.c.id == session["user_id"])
                .values(hash=new_hash)
            )
            db.commit()
            return redirect("/")


@app.route("/dest")
@login_required
def dest():
    """Destinations page"""
    with engine.begin() as db:
        # Get all the destinations for the current user and pass to the template
        destinations = db.execute(
            select(
                destinations_table.c.id,
                destinations_table.c.name,
                destinations_table.c.country,
                destinations_table.c.year,
                destinations_table.c.completed,
            ).where(destinations_table.c.user_id == session["user_id"])
        ).all()
    return render_template(
        "dest.html", not_empty=bool(len(destinations)), destinations=destinations
    )


@app.route("/dest-add", methods=["GET", "POST"])
@login_required
def dest_add():
    """Adding new destination"""
    if request.method == "GET":
        return render_template("dest-add.html")
    else:
        # Create a list of arguments for SQLALchemy
        args1 = {
            "user_id": session["user_id"],
            "name": request.form.get("name"),
            "country": request.form.get("country"),
            "year": request.form.get("year"),
        }
        if not args1["name"]:
            return apology("Must provide name", 403)
        args = {k: v for k, v in args1.items() if v}
        with engine.begin() as db:
            db.execute(
                insert(destinations_table)
                .values(args))
            db.commit()
        return redirect("/dest")


@app.route("/dest-edit", methods=["GET", "POST"])
@login_required
def dest_edit():
    """Editing destination"""
    if request.method == "GET":
        # This function always requires input from the front-end - redirect if no input
        return redirect("/dest")
    else:
        action = request.form.get("action")
        dest_id = str(request.form.get("id"))
        if action == "call":
            with engine.begin() as db:
                data = db.execute(
                    select(
                        destinations_table.c.id,
                        destinations_table.c.name,
                        destinations_table.c.country,
                        destinations_table.c.year,
                        destinations_table.c.completed,
                    ).where(
                        and_(
                            destinations_table.c.user_id == session["user_id"],
                            destinations_table.c.id == dest_id,
                        )
                    )
                ).all()[0]
                return render_template("dest-edit.html", data=data)
        elif action == "edit":
            # Create a list of arguments for SQLALchemy
            args1 = {
                "name": request.form.get("name"),
                "country": request.form.get("country"),
                "year": request.form.get("year"),
            }
            if not args1["name"]:
                return apology("Must provide name", 403)
            args = {k: v for k, v in args1.items() if v}
            with engine.begin() as db:
                db.execute(
                    update(destinations_table)
                    .where(destinations_table.c.id == dest_id)
                    .values(args)
                )
                db.commit()
            return redirect("/dest")
        else:
            return apology("Invalid operation call", 400)


@app.route("/dest-delete", methods=["GET", "POST"])
@login_required
def dest_delete():
    """Deleting destination"""
    if request.method == "GET":
        return redirect("/dest")
    else:
        dest_id = request.form.get("id")
        with engine.begin() as db:
            data = db.execute(
                delete(destinations_table).where(
                    and_(
                        destinations_table.c.user_id == session["user_id"],
                        destinations_table.c.id == dest_id,
                    )
                )
            )
        return redirect("/dest")


if __name__ == "__main__":
    app.run()

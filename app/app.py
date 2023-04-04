from flask import Flask, redirect, render_template, request, session
from sqlalchemy import and_, delete, insert, select, update
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session

from .etc.db_init import db_init
from .etc.functions import (
    apology,
    check_if_username_exists,
    get_dest_by_id,
    get_ideas,
    login_required,
    register_user,
    strip_args,
)

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
engine, users_table, destinations_table, ideas_table = db_init()


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
            if check_if_username_exists(db, username, users_table):
                return apology("Username already exists")
            else:
                register_user(username, password, db, users_table)

                # Remember which user has registered and log they in
                user_id = db.execute(
                    select(users_table.c["id"]).where(
                        users_table.c.username == username
                    )
                ).all()[0][0]

                session["user_id"] = user_id
                return redirect("/")


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
        args = {
            "user_id": session["user_id"],
            "name": request.form.get("name"),
            "country": request.form.get("country"),
            "year": request.form.get("year"),
        }
        # Check for required input - name must be provided
        if not args["name"]:
            return apology("Must provide name", 403)
        with engine.begin() as db:
            db.execute(insert(destinations_table).values(args))  # type: ignore
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
        user_id = session["user_id"]
        if action == "call":
            with engine.begin() as db:
                dest_data = get_dest_by_id(dest_id, db, user_id, destinations_table)
                return render_template("dest-edit.html", data=dest_data)
        elif action == "edit":
            # Create a list of arguments for SQLALchemy
            args = {
                "name": request.form.get("name"),
                "country": request.form.get("country"),
                "year": request.form.get("year"),
            }
            if not args["name"]:
                return apology("Must provide name", 403)
            args = strip_args(args)
            with engine.begin() as db:
                db.execute(
                    update(destinations_table)
                    .where(
                        and_(
                            destinations_table.c.user_id == user_id,
                            destinations_table.c.id == dest_id,
                        )
                    )
                    .values(args)  # type: ignore
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


@app.route("/ideas", methods=["GET", "POST"])
@login_required
def ideas():
    """Ideas page for selected destination"""
    if request.method != "POST":
        return redirect("/dest")
    else:
        user_id = session["user_id"]
        dest_id = request.form.get("id")
        with engine.begin() as db:
            # Get all the ideas for the current destination and pass to the template
            ideas_data = get_ideas(dest_id, db, user_id, ideas_table)
            dest_data = get_dest_by_id(dest_id, db, user_id, destinations_table)
            return render_template(
                "ideas.html", ideas_data=ideas_data, dest_data=dest_data
            )


@app.route("/idea-add", methods=["GET", "POST"])
@login_required
def idea_add():
    """Editing destination"""
    if request.method != "POST":
        # This function always requires input from the front-end - redirect if no input
        return redirect("/dest")
    else:
        # Create a list of arguments for SQLALchemy
        dest_id = request.form.get("dest_id")
        user_id = session["user_id"]
        args = {
            "user_id": user_id,
            "dest_id": dest_id,
            "description": request.form.get("description"),
            "notes": request.form.get("notes"),
            "link": request.form.get("link"),
            "map_link": request.form.get("map_link"),
            "day": request.form.get("day"),
            "completed": False,
        }
        # Check for required input - description must be provided
        if not args["description"]:
            return apology("Must provide description", 403)
        # Remove empty arguments and insert data into db
        args = strip_args(args)
        with engine.begin() as db:
            # Add the idea to the db
            db.execute(insert(ideas_table).values(args))  # type: ignore
            # Get all the ideas for the current destination and pass to the template
            ideas_data = get_ideas(dest_id, db, user_id, ideas_table)
            dest_data = get_dest_by_id(dest_id, db, user_id, destinations_table)
            return render_template(
                "ideas.html", ideas_data=ideas_data, dest_data=dest_data
            )


@app.route("/idea_delete", methods=["GET", "POST"])
@login_required
def idea_delete():
    """Deleting an idea from db"""
    if request.method == "POST":
        user_id = session["user_id"]
        dest_id = request.form.get("dest_id")
        id = request.form.get("id")
        if not dest_id or not id:
            return apology("Invalid input", 400)
        with engine.begin() as db:
            db.execute(
                delete(ideas_table).where(
                    and_(
                        ideas_table.c.user_id == user_id,
                        ideas_table.c.dest_id == dest_id,
                        ideas_table.c.id == id,
                    )
                )
            )
            # Get all the ideas for the current destination and pass to the template
            ideas_data = get_ideas(dest_id, db, user_id, ideas_table)
            dest_data = get_dest_by_id(dest_id, db, user_id, destinations_table)
            return render_template("ideas.html", ideas_data=ideas_data, dest_data=dest_data)
    else:
        return redirect("/dest")


@app.route("/day_add", methods=["GET", "POST"])
@login_required
def day_add():
    """Adding a day to a destination"""
    if request.method == "POST":
        user_id = session["user_id"]
        dest_id = request.form.get("dest_id")
        with engine.begin() as db:
            # Check how many days it is
            days = int(db.execute(
                select(destinations_table.c.days).where(
                    and_(
                        ideas_table.c.user_id == user_id,
                        ideas_table.c.dest_id == dest_id,
                    )
                )
            ).all()[0][0])
            # Increase amount of days by 1
            db.execute(
                update(destinations_table)
                .where(destinations_table.c.id == dest_id)
                .values(days=days+1)
            )
            # Get all the updated data for the current destination and pass to the template
            ideas_data = get_ideas(dest_id, db, user_id, ideas_table)
            dest_data = get_dest_by_id(dest_id, db, user_id, destinations_table)
            return render_template("ideas.html", ideas_data=ideas_data, dest_data=dest_data)
    else:
        return redirect("/dest")


if __name__ == "__main__":
    app.run()

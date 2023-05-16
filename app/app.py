from flask import Flask, redirect, render_template, request, session
from sqlalchemy import and_, delete, insert, select, update
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from etc.db_init import db_init
from etc.functions import (
    apology,
    check_if_username_exists,
    day_add,
    day_delete,
    delete_idea,
    get_dest_by_id,
    login_required,
    move_day,
    register_user,
    render_ideas,
    strip_args,
)
from etc.config import env

# from sys import stdout, stderr # - used for print() when debugging

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Debug and test mode enabled for Development and Test enviromnents only
if env == "DEV" or "TEST":
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
        if check_if_username_exists(username):
            return apology("Username already exists")
        else:
            register_user(username, password)
        # Remember which user has registered and log they in
        with engine.begin() as db:
            user_id = db.execute(
                select(users_table.c["id"]).where(users_table.c.username == username)
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
    session.pop("dest_id", default=None)
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
    session.pop("dest_id", default=None)
    if request.method == "GET":
        return render_template("dest-add.html")
    else:
        # Create a list of arguments for SQLALchemy
        try:
            args = {
                "user_id": session["user_id"],
                "name": request.form.get("name"),
                "country": request.form.get("country"),
                "year": request.form.get("year"),
            }
        except:
            return apology("Invalid input", 400)
        # Check for required input - name must be provided
        if not args["name"]:
            return apology("Must provide name", 403)
        args = strip_args(args)
        with engine.begin() as db:
            db.execute(insert(destinations_table).values(args))  # type: ignore
            db.commit()
        return redirect("/dest")


@app.route("/dest-edit", methods=["GET", "POST"])
@login_required
def dest_edit():
    """Editing destination"""
    session.pop("dest_id", default=None)
    if request.method == "GET":
        # This function always requires input from the front-end - redirect if no input
        return redirect("/dest")
    else:
        action = request.form.get("action")
        dest_id = str(request.form.get("dest_id"))
        user_id = session["user_id"]
        # Call action renders a page with a form for editing destination
        if action == "call":
            with engine.begin() as db:
                dest_data = get_dest_by_id(dest_id, user_id)
                return render_template("dest-edit.html", data=dest_data)
        # Edit action is the result of submitting edit destination form - updates DB with the provided input
        elif action == "edit":
            # Create a list of arguments for SQLALchemy
            args = {
                "name": request.form.get("name"),
                "country": request.form.get("country"),
                "year": request.form.get("year"),
            }
            # Check for required input
            if not args["name"]:
                return apology("Must provide name", 403)
            args = strip_args(args)
            # Update DB
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
        # Clear dest_id from session
        session.pop("dest_id", default=None)
        user_id = session["user_id"]
        dest_id = request.form.get("dest_id")
        # Delete all ideas related to this destination first
        with engine.begin() as db:
            db.execute(
                delete(ideas_table).where(
                    and_(
                        ideas_table.c.user_id == user_id,
                        ideas_table.c.dest_id == dest_id,
                    )
                )
            )
            db.commit()
        # Delete a destination record
        with engine.begin() as db:
            db.execute(
                delete(destinations_table).where(
                    and_(
                        destinations_table.c.user_id == user_id,
                        destinations_table.c.id == dest_id,
                    )
                )
            )
            db.commit()
        return redirect("/dest")


@app.route("/ideas", methods=["GET", "POST"])
@login_required
def ideas():
    """Ideas page for selected destination"""
    # Check if page has been accessed via POST or whether dest_id is stored in the session
    if request.method == "POST" or session.get("dest_id"):
        action = request.form.get("action")
        user_id = session["user_id"]
        dest_id = request.form.get("dest_id") or session["dest_id"]
        # Add idea
        if action == "add":
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
        # Delete idea
        elif action == "delete":
            idea_id = request.form.get("idea_id")
            if not dest_id or not dest_id:
                return apology("Invalid input", 400)
            delete_idea(user_id, dest_id, idea_id)
        # Add a day to the schedule
        elif action == "day_add":
            day_add(user_id, dest_id)
        # Delete a day from the schedule
        elif action == "day_delete":
            day = int(request.form.get("day"))  # type: ignore
            day_delete(user_id, dest_id, day)
        return render_ideas(user_id, dest_id)
    # If not accesed via POST or no dest_id stored in the session - return to main page
    return redirect("/dest")


@app.route("/idea_edit", methods=["GET", "POST"])
@login_required
def idea_edit():
    """Edit specified idea"""
    if request.method != "POST":
        return redirect("/dest")
    else:
        # Get all the arguments from session and request and put them into dictionary
        args = {
            "user_id": session["user_id"],
            "dest_id": request.form.get("dest_id"),
            "description": request.form.get("description"),
            "notes": request.form.get("notes"),
            "link": request.form.get("link"),
            "map_link": request.form.get("map_link"),
            "completed": False,
        }
        # Check for required input - description must be provided
        if not args["description"]:
            return apology("Must provide description", 403)
        # Update db record
        with engine.begin() as db:
            db.execute(
                update(ideas_table)
                .where(
                    and_(
                        ideas_table.c.user_id == args["user_id"],
                        ideas_table.c.id == request.form.get("idea_id"),
                    )
                )
                .values(args)  # type: ignore
            )
        session["dest_id"] = args["dest_id"]
        return redirect("/ideas")


@app.route("/move_day_up", methods=["GET", "POST"])
@login_required
def move_day_up():
    """Move day up in the schedule"""
    # Require that function accessed via POST
    if request.method != "POST":
        return redirect("/dest")
    else:
        user_id = session["user_id"]
        dest_id = request.form.get("dest_id")
        day = request.form.get("day")
        # Move day by -1
        move_day(user_id, dest_id, day, -1)
        # Save dest_id to session so /ideas knows what destination to render
        session["dest_id"] = dest_id
        return redirect("/ideas")


@app.route("/move_day_down", methods=["GET", "POST"])
@login_required
def move_day_daown():
    """Move day down in the schedule"""
    # Require that function accessed via POST
    if request.method != "POST":
        return redirect("/dest")
    else:
        user_id = session["user_id"]
        dest_id = request.form.get("dest_id")
        day = request.form.get("day")
        # Move day by +1
        move_day(user_id, dest_id, day, 1)
        # Save dest_id to session so /ideas knows what destination to render
        session["dest_id"] = dest_id
        return redirect("/ideas")


if __name__ == "__main__":
    app.run()


@app.route("/dest-complete", methods=["GET", "POST"])
@login_required
def dest_complete():
    """Mark destination as complete/incomplete"""
    if request.method == "GET":
        return redirect("/dest")
    else:
        # Clear dest_id from session
        session.pop("dest_id", default=None)
        try:
            user_id = int(session["user_id"])
            dest_id = int(request.form.get("dest_id"))  # type: ignore
            complete = bool(int(request.form.get("complete")))  # type: ignore
        except:
            return apology("Invalid input", 400)
        # Update DB to mark destination as complete
        with engine.begin() as db:
            db.execute(
                update(destinations_table)
                .where(
                    and_(
                        destinations_table.c.user_id == user_id,
                        destinations_table.c.id == dest_id,
                    )
                )
                .values(completed=complete)
            )
            db.commit()
        return redirect("/dest")


@app.route("/idea-complete", methods=["GET", "POST"])
@login_required
def idea_complete():
    """Marks idea as complete or incomplete"""
    if request.method != "POST":
        return redirect("/dest")
    else:
        # Get all the arguments from session and request and put them into dictionary
        try:
            user_id = int(session["user_id"])
            idea_id = int(request.form.get("idea_id"))  # type: ignore
            dest_id = int(request.form.get("dest_id"))  # type: ignore
            complete = bool(int(request.form.get("complete")))  # type: ignore
        except:
            return apology("Invalid input", 400)
        # Update db record
        with engine.begin() as db:
            db.execute(
                update(ideas_table)
                .where(
                    and_(
                        ideas_table.c.user_id == user_id,
                        ideas_table.c.id == idea_id,
                    )
                )
                .values(completed=complete)  # type: ignore
            )
        session["dest_id"] = dest_id
        return redirect("/ideas")

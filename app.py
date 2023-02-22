from sqlalchemy import insert, select
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from functions import login_required, apology
from werkzeug.security import check_password_hash, generate_password_hash
from db_init import db_init

# Configure application
app = Flask(__name__)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Initialise database and tables
engine, users_table = db_init()


@app.route("/")
def index():
    return render_template("index.html")


@ app.route("/register", methods=["GET", "POST"])
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

        # Check if username already exists
        with engine.begin() as db:
            result = db.execute(select(users_table.c.id).where(
                users_table.c.username == 'user')).all()
            # result = db.execute(
            #    text('SELECT id FROM users WHERE username = :u'), {'u': username})
            if len(result) > 0:
                # return apology("Username already exists")
                return apology("Username already exists")
            else:
                hash = generate_password_hash(password)
                db.execute(insert(users_table).values(
                    username=username, hash=hash))
                db.commit()
                # db.execute(text(
                #    "INSERT INTO users (username, hash) VALUES (:u, :h)"), {"u": username, "h": hash})
                return redirect("/login")


@ app.route("/login", methods=["GET", "POST"])
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
            rows = db.execute(select(users_table.c["id","hash"]).where(users_table.c.username=username).all()
            #rows = db.execute(text("SELECT id, hash FROM users WHERE username = :u"), {
            #                 "u": request.form.get("username")}).all()
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

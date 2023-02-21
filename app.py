from sqlalchemy import text, select
from flask import Flask, redirect, render_template, request
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
            result = select(users_table).where(
                users_table.c.username == username)
            # result = db.execute(
            #    text('SELECT id FROM users WHERE username = :u'), {'u': username})
            print(result)
            if result.rowcount > 0:
                # return apology("Username already exists")
                return apology("Username already exists")
            else:
                hash = generate_password_hash(password)
                db.execute(text(
                    "INSERT INTO users (username, hash) VALUES (:u, :h)"), {"u": username, "h": hash})
                return redirect("/login")

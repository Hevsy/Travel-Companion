from functools import wraps
from flask import redirect, render_template, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import and_, delete, insert, select


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, message=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def strip_args(args1):
    """Strips args from empty arguments"""
    return {f: b for f, b in args1.items() if b}


def register_user(username, password, db, users_table):
    """Add user to DB"""
    hash = generate_password_hash(password)
    db.execute(insert(table=users_table).values(username=username, hash=hash))


def check_if_username_exists(db, username, users_table):
    """Check is username already exists in DB"""
    result = db.execute(
        select(users_table.c.id).where(users_table.c.username == username)
    ).all()
    return len(result) > 0

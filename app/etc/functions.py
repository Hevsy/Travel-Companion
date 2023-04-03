from functools import wraps
from flask import redirect, render_template, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import and_, delete, insert, select


def apology(message, code=400):
    """Render an error/apology message"""
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


def strip_args(args):
    """Strips dictionary arguments from empty arguments"""
    return {key: value for key, value in args.items() if value}


def register_user(username, password, db, users_table):
    """Add a user to DB"""
    hash = generate_password_hash(password)
    db.execute(insert(table=users_table).values(username=username, hash=hash))


def check_if_username_exists(db, username, users_table):
    """Check is username already exists in DB"""
    result = db.execute(
        select(users_table.c.id).where(users_table.c.username == username)
    ).all()
    return len(result) > 0


def get_ideas(dest_id, db, user_id, ideas_table):
    """Returns all ideas for specified dest_id"""
    ideas = db.execute(
        select(
            ideas_table.c.id,
            ideas_table.c.description,
            ideas_table.c.notes,
            ideas_table.c.link,
            ideas_table.c.map_link,
            ideas_table.c.day,
        ).where(
            and_(
                ideas_table.c.user_id == user_id,
                ideas_table.c.dest_id == dest_id,
            )
        )
    ).all()
    return ideas

def get_dest_by_id(dest_id, db, user_id, destinations_table):
    """Returns all ideas for specified dest_id plus data about that destination required for ideas templates"""
    # Get the destination's data bi its id to show in the template
    dest = db.execute(
        select(
            destinations_table.c.name,
            destinations_table.c.country,
            destinations_table.c.year,
            destinations_table.c.id,
            destinations_table.c.days,
            destinations_table.c.completed
        ).where(
            and_(
                destinations_table.c.user_id == user_id,
                destinations_table.c.id == dest_id,
            )
        )
    ).all()[0]
    return dest

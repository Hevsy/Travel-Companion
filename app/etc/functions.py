from functools import wraps
from flask import redirect, render_template, session
from werkzeug.security import generate_password_hash
from sqlalchemy import and_, case, delete, insert, select, update


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
    """Strips dictionary of arguments from empty arguments"""
    return {key: value for key, value in args.items() if value}


def register_user(username, password):
    """Add a user to DB"""
    from app.app import engine, users_table

    with engine.begin() as db:
        hash = generate_password_hash(password)
        db.execute(insert(table=users_table).values(username=username, hash=hash))


def check_if_username_exists(username):
    """Check is username already exists in DB"""
    from app.app import engine, users_table

    with engine.begin() as db:
        result = db.execute(
            select(users_table.c.id).where(users_table.c.username == username)
        ).all()
        return len(result) > 0


def get_dest_by_id(dest_id, user_id):
    """Returns all ideas for specified dest_id plus data about that destination required for ideas templates"""
    from app.app import engine, destinations_table

    # Get the destination's data by id to show in the template
    with engine.begin() as db:
        dest = db.execute(
            select(
                destinations_table.c.name,
                destinations_table.c.country,
                destinations_table.c.year,
                destinations_table.c.id,
                destinations_table.c.days,
                destinations_table.c.completed,
            ).where(
                and_(
                    destinations_table.c.user_id == user_id,
                    destinations_table.c.id == dest_id,
                )
            )
        ).all()[0]
        return dest._asdict()


def get_ideas(dest_id, user_id):
    """Returns all ideas for specified dest_id"""
    from app.app import engine, ideas_table

    # Get the ideas by destination's id to show in the template
    with engine.begin() as db:
        ideas = db.execute(
            select(
                ideas_table.c.id,
                ideas_table.c.description,
                ideas_table.c.notes,
                ideas_table.c.link,
                ideas_table.c.map_link,
                ideas_table.c.day,
                ideas_table.c.completed,
            ).where(
                and_(ideas_table.c.user_id == user_id, ideas_table.c.dest_id == dest_id)
            )
        ).all()
        return ideas


def delete_idea(user_id, dest_id, id):
    """Deletes an idea from db"""
    from app.app import engine, ideas_table

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
        db.commit()


def render_ideas(user_id, dest_id):
    """Fetches the data from db and renders ideas page for specified destination"""
    ideas_data = get_ideas(dest_id, user_id)
    dest_data = get_dest_by_id(dest_id, user_id)
    return render_template("ideas.html", ideas_data=ideas_data, dest_data=dest_data)


def day_add(user_id, dest_id):
    """Adds a day to selected destination"""
    from app.app import engine, destinations_table

    with engine.begin() as db:
        # Check how many days and increment by 1
        days = int(
            db.execute(
                select(destinations_table.c.days).where(
                    and_(
                        destinations_table.c.user_id == user_id,
                        destinations_table.c.id == dest_id,
                    )
                )
            ).all()[0][0]
        )
        days += 1
        # Update destination in db
        db.execute(
            update(destinations_table)
            .where(destinations_table.c.id == dest_id)
            .values(days=days)
        )
        db.commit()


def day_delete(user_id, dest_id, day_to_remove):
    """Delete a day from selected destination"""
    from app.app import engine, destinations_table, ideas_table

    with engine.begin() as db:
        # Check how many days in the current destination
        days = int(
            db.execute(
                select(destinations_table.c.days).where(
                    and_(
                        destinations_table.c.user_id == user_id,
                        destinations_table.c.id == dest_id,
                    )
                )
            ).all()[0][0]
        )
        days = days

        # Delete all ideas related to this day
        db.execute(
            delete(ideas_table).where(
                and_(
                    ideas_table.c.user_id == user_id,
                    ideas_table.c.dest_id == dest_id,
                    ideas_table.c.day == day_to_remove,
                )
            )
        )

        # Get the record of all ideas
        ideas = db.execute(
            select(ideas_table.c.id, ideas_table.c.day).where(
                and_(
                    ideas_table.c.user_id == user_id,
                    ideas_table.c.dest_id == dest_id,
                )
            )
        ).all()
        # Iterate through the ideas for the days after deleted one and move them up (decrement a day)
        for day in range(day_to_remove, days + 1):
            db.execute(
                update(ideas_table)
                .where(
                    and_(
                        ideas_table.c.user_id == user_id,
                        ideas_table.c.dest_id == dest_id,
                        ideas_table.c.day == day,
                    )
                )
                .values(day=day - 1)
            )

        # Update a record for amount of days in db
        # Check - do not delete the last day
        if days > 1:
            days -= 1
        # Update destination in db
        db.execute(
            update(destinations_table)
            .where(destinations_table.c.id == dest_id)
            .values(days=days)
        )
        db.commit()


def move_day(user_id, dest_id, day, step):
    """Moves the day up or down"""
    from app.app import engine, ideas_table

    with engine.begin() as db:
        dest = get_dest_by_id(dest_id, user_id)
        days = dest["days"]
        # Check if we're moving first day up or last day down - then do nothing
        if int(day) + int(step) < 1 or int(day) + int(step) > days:
            return
        # Swap the days (eg move all the ideas recorded for that day to a target day and vice versa)  
        db.execute(
            update(ideas_table)
            .where(
                and_(ideas_table.c.user_id == user_id, ideas_table.c.dest_id == dest_id)
            )
            .values(
                day=case(
                    (ideas_table.c.day == day, int(day) + int(step)),
                    (ideas_table.c.day == int(day) + int(step), day),
                    else_=ideas_table.c.day,
                )
            )
        )
        return

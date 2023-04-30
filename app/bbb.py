from sqlalchemy import (
    select,
)
from flask import Flask
from etc.db_init import db_init

# Configure application
app = Flask(__name__)

# Configure DB connection
# Import db config from etc/config
# Initialise database and tables
engine, users_table, destinations_table, ideas_table = db_init()


with engine.begin() as db:
    user_id = "1"
    dest_id = "1"
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
                destinations_table.c.user_id == user_id,
                destinations_table.c.id == dest_id,
            )
        ).fetchone()
        dest_dict = dest._asdict() # type: ignore
        print(dest_dict)
        print(dest_dict["id"])

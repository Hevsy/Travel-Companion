from sqlalchemy import (
    URL,
    ForeignKey,
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Boolean,
)
from sqlalchemy_utils import database_exists, create_database
from .config import db_config


def db_init():
    """Create db URL & engine"""
    db_url = URL.create(
        db_config["type"],
        database=db_config["db"],
        username=db_config["username"],
        password=db_config["pass"],
        host=db_config["host"],
    )
    engine = create_engine(db_url)
    # Initialise database
    if not database_exists(engine.url):
        create_database(engine.url)

    # DB Metadata
    # Create metadata object
    meta = MetaData()
    # Define tables
    users_table = Table(
        "users",
        meta,
        Column("id", Integer, primary_key=True),
        Column("username", String(30)),
        Column("hash", String(255)),
    )
    destinations_table = Table(
        "destinations",
        meta,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
        Column("name", String(60)),
        Column("country", String(60)),
        Column("year", Integer),
        Column("days", Integer, default=1, nullable=False),
        Column("completed", Boolean),
    )

    ideas_table = Table(
        "ideas",
        meta,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
        Column("dest_id", Integer, ForeignKey("destinations.id"), nullable=False),
        Column("description", String(60)),
        Column("notes", String(255)),
        Column("link", String(2000)),
        Column("map_link", String(2000)),
        Column("day", Integer, default=1, nullable=False),
        Column("completed", Boolean),
    )

    # Create tables
    meta.create_all(engine, checkfirst=True)
    return engine, users_table, destinations_table, ideas_table

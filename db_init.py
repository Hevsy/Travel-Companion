from sqlalchemy import URL, create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy_utils import database_exists, create_database
from etc.config import db_config


def db_init():
    # Create db URL & engine
    db_url = URL.create(db_config['type'], database=db_config['db'],
                        username=db_config['username'], password=db_config['pass'], host=db_config['host'])
    print(db_url)
    engine = create_engine(db_url)
# Initialise database
    if not database_exists(engine.url):
        create_database(engine.url)

# DB Metadata for ORM
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
# Create tables
    meta.create_all(engine, checkfirst=True)
    return engine, users_table

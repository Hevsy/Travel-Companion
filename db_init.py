from sqlalchemy import URL, create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy_utils import database_exists, create_database
from etc.config import db_config
import _mysql_connector   


def db_init():
    # Configure DB connection
    # Import db config from etc/config
    db_type = ""
    db_file = db_username = db_pass = db_host = None
# Assign variables from db_config
    for item in db_config:
        exec('{KEY} = {VALUE}'.format(KEY=item, VALUE=repr(db_config[item])))
# Create db URL & engine
    db_url = URL.create(db_type, database=db_file, username=db_username,
                        password=db_pass, host=db_host)
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
        Column("hash", String(60)),
    )
# Create tables
    meta.create_all(engine, checkfirst=True)
    return engine, users_table

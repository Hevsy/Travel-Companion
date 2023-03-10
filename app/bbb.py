from sqlalchemy import URL, create_engine, insert, text, MetaData, Table, Column, Integer, String, select
from sqlalchemy_utils import database_exists, create_database
from etc.config import db_config
from flask import Flask, redirect, render_template, request
from flask_session import Session
from etc.functions import login_required, apology
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure DB connection
# Import db config from etc/config
def db_init():
    # Create db URL & engine
    db_url = URL.create(db_config['type'], database=db_config['db'],
                        username=db_config['username'], password=db_config['pass'], host=db_config['host'])
    # print(db_url)
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

engine, users_table = db_init()

with engine.begin() as db:
    password = "123"
    username = "Paul"
    result = db.execute(
        select(users_table.c.id).where(users_table.c.username == username)).all()
    # result = db.execute(
    #    text('SELECT id FROM users WHERE username = :u'), {'u': username})

    print(result)
    print(len(result))
    if len(result) > 0:
        print("Username already exists")
    else:
        hash = generate_password_hash(password)
        db.execute(insert(users_table).values(username=username, hash=hash))
        print("insert")
        db.commit()
        print("commit")
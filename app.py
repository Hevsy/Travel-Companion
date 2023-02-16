from sqlalchemy import URL, create_engine
from etc.config import db_config
from flask import Flask, redirect, render_template, request
from flask_session import Session

# Configure application
app = Flask(__name__)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# import db config from etc/config
db_type = ""
db_file = db_username = db_pass = db_host = None
# Assign variables from db_config
for item in db_config:
    exec('{KEY} = {VALUE}'.format(KEY=item, VALUE=repr(db_config[item])))
# Create db URL & engine
db_url = URL.create(db_type, database=db_file,
                    username=db_username, password=db_pass, host=db_host)

engine = create_engine(db_url)


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
            result = db.execute(
                text('SELECT id FROM users WHERE username = :u'), {'u': username})
            print(result.rowcount)
            if result.rowcount > 0:
                # return apology("Username already exists")
                return apology("Username already exists")
            else:
                hash = generate_password_hash(password)
                db.execute(text(
                    "INSERT INTO users (username, hash) VALUES (:u, :h)"), {"u": username, "h": hash})
                return redirect("/login")

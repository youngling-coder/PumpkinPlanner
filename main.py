from flask import Flask, redirect, render_template, session, url_for,  request, flash, abort, g
from pumpkinDB import PumpkinDB
import sqlite3, os, uuid
from user_login import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from utilities import password_valid, username_valid


# Config variables
DATABASE = ""
DEBUG = True
SECRET_KEY = str(uuid.uuid4())

# Setting up flask application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "pumpkins.db")))

login_manager = LoginManager(app=app)
login_manager.login_view = "index"
login_manager.login_message = "⚠ Log in to view this page!"

# Close database connection after request
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()

# Create database connection
dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = PumpkinDB(db=db)


def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()

    return g.link_db

# Create and return database Connction reference
def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(os.path.join(os.getcwd(), "pumpkins.db"))
    conn.row_factory = sqlite3.Row

    return conn

# Create database structure
def create_structure() -> bool:
    db = PumpkinDB.connect_db()

    try:
        with open("structure.sql", "r") as db_structure:
            db.cursor().executescript(db_structure.read())
        db.commit()
        db.close()
    except sqlite3.Error as e:
        print(f"Error while creating database structure:\n{e}")
        return False

    return True

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id=user_id, db=dbase)

# Logout user
@app.route("/logout")
@login_required
def logout():
    logout_user()
    print("User logged out")
    return redirect(url_for("index"))

# Show index page
@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():

    if current_user.is_authenticated:
        return redirect(url_for("profile", username=current_user.get_username()))

    if request.method == "POST":
        user = dbase.getUser(request.form["username"])
        if user[0] and check_password_hash(user["password"], request.form["password"]):
            user_login = UserLogin().login(user=user)
            remember_me = True if request.form.get("remember-me") else False
            login_user(user_login, remember=remember_me)
            return redirect(url_for("profile", username=request.form["username"]))

        flash("⚠ Login credentials are wrong!", category="error")

    return render_template("index.html", title="Log In")

# Show not found page
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", title="Not found")


@app.route("/tasks/<title>")
@login_required
def task(title):
    task = dbase.getTaskByTitle(username=current_user.get_username(), title=title)

    if not task:
        abort(404)

    return render_template("task.html", title=task["title"], description=task["description"])


@app.route("/remove/<int:id_>")
@login_required
def remove(id_):
    tasks = dbase.getTasks(username=current_user.get_username())
    taskEx = dbase.removeTask(id=id_)
    if dbase.removeTask(id=id_):
        tasks = dbase.getTasks(username=current_user.get_username())
    if not tasks[0]:
        return render_template("profile.html", tasks=False, username=current_user.get_username(), title=current_user.get_username())
    else:
        return render_template("profile.html", tasks=tasks[1], username=current_user.get_username(), title=current_user.get_username())


# Show profile page
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    tasks = dbase.getTasks(username=current_user.get_username())
    if request.method == "POST":
        user = current_user.get_username()
        title = request.form["title"].lstrip()
        description = request.form["description"].lstrip()
        if title and description:
            dbase.addTask(title=title, description=description, username=user)
            tasks = dbase.getTasks(username=current_user.get_username())

    if not tasks[0]:
        return render_template("profile.html", tasks=False, username=current_user.get_username(), title=current_user.get_username())
    else:
        return render_template("profile.html", tasks=tasks[1], username=current_user.get_username(), title=current_user.get_username())

# Sign up process handler
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        pwd_valid = password_valid(psw=request.form["password"])
        password_equals = request.form["password"] == request.form["repeat_password"]
        uname_valid = username_valid(request.form["username"])
        if pwd_valid == True:
            if password_equals:
                if uname_valid == True:
                    psw_hash = generate_password_hash(password=request.form["password"])
                    res = dbase.addUser(username=request.form["username"], password=psw_hash)

                    if res[0]:
                        flash("✔ "+res[1], category="success")
                        return redirect(url_for("index"))
                    else:
                        flash(res[1], category="error")
                else:
                    flash(uname_valid, category="error")
            else:
                flash("⚠ Password doesn't match!", category="error")
        else:
            flash(pwd_valid, category="error")

    return render_template("signup.html", title="Sign Up")

if __name__ == "__main__":
    app.run(debug=DEBUG)

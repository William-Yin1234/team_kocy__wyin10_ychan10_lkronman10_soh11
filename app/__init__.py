# Team KOCY -- William Yin, Liam Kronman, Jason Chan, Stella Oh
# SoftDev
# P0: Da Art of Storytellin' (Pt.2)
# 2021-01-05


from flask import Flask, render_template, request, session, url_for, redirect, abort
from flask_bcrypt import Bcrypt
import bcrypt
import os
import time
import sqlite3
import utils


APP_NAME = "Kocy Blog"
app = Flask(APP_NAME)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(32)
DB_FILE = "kocy_blog.db"


@app.route("/")
@app.route("/index")
def index():

    if not session.get("user_id") or not session.get("username"):
        return redirect(url_for("login"))

    entries = utils.select_entries_by_author(DB_FILE, session.get("user_id"), True)

    return render_template("index.html", username=session.get("username"), entries=entries)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirm password"):
        return render_template("register.html", warning="Please fill out all fields.")
    elif len(request.form.get("password")) < 4:
        return render_template("register.html", warning="Password must be at least 4 characters long.")
    elif request.form.get("password") != request.form.get("confirm password"):
        return render_template("register.html", warning="Passwords do not match.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("select * from users where username = ?", (request.form.get("username"),))
    user = cursor.fetchone()
    if user:
        db.close()
        return render_template("register.html", warning="Username is already taken.")

    password_hash = bcrypt.generate_password_hash(request.form.get("password"))
    cursor.execute("insert into users (username, password) values (?, ?)", (request.form.get("username"), password_hash))
    cursor.execute("select * from users where username = ?", (request.form.get("username"),))
    user = cursor.fetchone()
    db.commit()
    db.close()

    session["user_id"] = user[0]
    session["username"] = user[1]
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("index"))
        return render_template("login.html")

    if not request.form.get("username") or not request.form.get("password"):
        return render_template("login.html", warning="Please fill out all fields.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("select * from users where username = ?", (request.form.get("username"),))
    user = cursor.fetchone()
    db.close()
    if not user or not bcrypt.check_password_hash(user[2], request.form.get("password")):
        return render_template("login.html", warning="Incorrect username or password.")

    session["user_id"] = user[0]
    session["username"] = user[1]
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    if not session.get("user_id") or not session.get("username"):
        return redirect(url_for("login"))

    session.pop("user_id")
    session.pop("username")
    return redirect(url_for("login"))


@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if not session.get("user_id") or not session.get("username"):
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("new_entry.html")

    if not request.form.get("title") or not request.form.get("body"):
        return render_template("new_entry.html", warning="Please include a title and a body.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("insert into entries (author_id, title, body, date) values (?, ?, ?, ?)",
        (session.get("user_id"), request.form.get("title"), request.form.get("body"), int(time.time())))
    db.commit()
    db.close()
    return redirect(url_for("index"))


@app.route("/user/<int:user_id>")
def display_user_entries(user_id):
    if not session.get("user_id") or not session.get("username"):
        return abort(403)

    entries = utils.select_entries_by_author(DB_FILE, author_id=user_id)

    return render_template("display_entries.html", entries=entries)


@app.route("/entry/<int:entry_id>/edit", methods=["GET", "POST"])
def edit_entry(entry_id):
    if not session.get("user_id") or not session.get("username"):
        return redirect(url_for("login"))

    results = utils.verify_user_owns_entry(DB_FILE, entry_id, session.get("user_id"))
    if results[0] != 0:
        abort(results[0])

    entry = results[1]
    if request.method == "GET":
        title = entry[4]
        body = entry[2]
        return render_template("edit_entry.html", title=title, body=body, id=entry_id)

    if not request.form.get("title") or not request.form.get("body"):
        return render_template("edit_entry.html", warning="Please include a title and a body.")

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("update entries set title = ?, body = ? where id = ?",
        (request.form.get("title"), request.form.get("body"), entry_id))
    db.commit()
    db.close()

    return redirect(url_for("display_user_entries", user_id=session.get("user_id")))


@app.route("/entry/<int:entry_id>/delete")
def delete_entry(entry_id):
    if not session.get("user_id") or not session.get("username"):
        return redirect(url_for("login"))

    results = utils.verify_user_owns_entry(DB_FILE, entry_id, session.get("user_id"))
    if results[0] != 0:
        abort(results[0])

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("delete from entries where id = ?",
        (entry_id,))
    db.commit()
    db.close()

    return redirect(url_for("display_user_entries", user_id=session.get("user_id")))


if __name__ == "__main__":
    app.debug = True
    app.run()

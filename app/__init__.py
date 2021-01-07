# Team KOCY -- William Yin, Liam Kronman, Jason Chan, Stella Oh
# SoftDev
# P0: Da Art of Storytellin' (Pt.2)
# 2021-01-05

from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session
import os
import sqlite3
from datetime import date

today = date.today()

DB_FILE="discobandit.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

# Used to create initial tables
#c.execute("CREATE TABLE Users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
#c.execute("CREATE TABLE Entries(id INTEGER PRIMARY KEY, author INTEGER, context TEXT, date TEXT)")

users = []
entries = []

c.execute("SELECT * FROM Users")
users = c.fetchall()

c.execute("SELECT * FROM Entries")
entries = c.fetchall()


USERNAME = "username" #needed?
PASSWORD = "1234"



#the conventional way:
#from flask import Flask, render_template, request

app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(32)


@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():

    # Two cases: user requests with GET, or user requests with POST
    # If user requests with GET, render welcome.html if session contains username, or render login.html if it does not.
    if request.method == "GET":
        if session.get("username"):
            return render_template("homepage.html", username=session.get("username"))
        else:
            return render_template('login.html')

    # If user requests with POST, then they are sending form data that needs to be authenticated.
    if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
        # Save username to session
        session["username"] = request.form.get("username")
        return render_template("homepage.html", username=session.get("username"))
    else:
        # Render error
        error = "Wrong"
        if request.form.get("username") != USERNAME:
            error += " username"
        if request.form.get("password") != PASSWORD:
            error += " password"
        return render_template("error.html", error=error)

# must be fixed to retain username
@app.route("/homepage", methods=["POST"])
def homepage():
    return render_template("homepage.html", username=session.get("username"))

# Only allow this route to be reached with post.
@app.route("/logout", methods=["POST"])
def logout():
    # Remove username key from session dict.
    session.pop("username")
    return render_template("loggedOut.html")

@app.route("/own")
def disp_own():
    u = session.get("username")
    iden = -1
    text = ""
    for row in users:
        if row[1] == u:
            iden = row[0]
    for row in entries:
        if row[0] == iden:
            text = "By " +  row[1] + "<br />" + row[3] + "<br />" + row[2]
    return render_template("ownBlog.html", entry=text)

@app.route("/other")
def disp_others():
    u = request.form.get("username")
    iden = -1
    text = ""
    for row in users:
        if row[1] == u:
            iden = row[0]
    for row in entries:
        if row[0] == iden:
            text = "By " +  row[1] + "<br />" + row[3] + "<br />" + row[2]
    return render_template("otherBlog.html", author=u, entry=text)

@app.route("/newentry", methods=["POST"])
def new_entry():
    return render_template("newEntry.html")

@app.route("/addentry")
def add_entry():
    c.execute("INSERT INTO Entries VALUES(session.get('id'), session.get('username'), request.form['addEntry'], date)")
    return disp_own()

@app.route("/editentry", methods=["POST"])
def edit_entry():
    return render_template("editEntry.html")

if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()

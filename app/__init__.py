# Team KOCY -- William Yin, Liam Kronman, Jason Chan, Stella Oh
# SoftDev
# P0: Da Art of Storytellin' (Pt.2)
# 2021-01-05

from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session
import os


USERNAME = "username"
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


# Only allow this route to be reached with post.
@app.route("/logout", methods=["POST"])
def logout():
    # Remove username key from session dict.
    session.pop("username")
    return render_template("loggedOut.html")



if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()

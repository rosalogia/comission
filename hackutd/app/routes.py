from flask import render_template
from app import app

@app.route("/")
@app.route("/index")
def index():
    print("hi")
    return render_template("index.html", title="Home")

@app.route("/explore")
def explore():
    return render_template("explore.html", title="Explore")

@app.route("/login")
def login():
    return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
    return render_template("logout.html", title="Logout")

@app.route("/profile")
def profile():
    return render_template("profile.html", title="Profile")

@app.route("/register")
def register():
    return render_template("register.html", title="Register")
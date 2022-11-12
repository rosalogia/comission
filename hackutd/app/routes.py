from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm, RegistrationForm

@app.route("/")
@app.route("/index")
def index():
    print("hi")
    return render_template("index.html", title="Home")

@app.route("/explore")
def explore():
    return render_template("explore.html", title="Explore")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    return render_template("logout.html", title="Logout")

@app.route("/profile")
def profile():
    return render_template("profile.html", title="Profile")

@app.route("/register")
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("register.html", title="Register", form=form)
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from werkzeug.urls import url_parse
import os
import datetime

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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", title="Profile")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, name=form.name.data, is_artist=form.is_artist.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("register.html", title="Register", form=form)

@app.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        img = form.image.data
        path = os.path.join(app.instance_path, 'posts', img.filename)
        img.save(path)
        tags = [s.strip() for s in form.tags.data.split(",")]
        new_post = Post(image_path=path, caption=form.caption.data, posted_at=datetime.datetime.now(), price=form.price.data)
        new_post.tags += tags
        current_user.posts.append(new_post)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template("create.html", title="Create", form=form)
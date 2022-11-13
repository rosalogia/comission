from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from werkzeug.urls import url_parse
import os
import datetime
import hashlib

@app.route("/")

@app.route("/index")
def index():
    print("hi")
    return render_template("index.html", title="Home")

@app.route("/explore", methods=['GET','POST'])
def explore():
    form = SearchForm()
    post=""
    if form.validate_on_submit():
        tag_list = form.search_tag.data.split(", ")
        posts = [t.post for t in Tag.query.filter(Tag.tag.in_(tag_list)).all() if t.post.artist.username == form.search_artist.data]
            
        if not posts:
            flash("No matching pictures found")
        post_cols = [[], [], []]
        for i in range(len(posts)):
            post_cols[i % 3].append(posts[i])
        print(post_cols)
        return render_template("explore.html", title="Explore", posts=post_cols, form=form)
    else:
        flash("Error")
    return render_template("explore.html", title="Explore", posts=[], form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts
    columns = [[], [], []]
    for i in range(len(posts)):
        columns[i % 3].append(posts[i])

    return render_template("profile.html", user=user, posts=columns, title="Profile")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            name=form.name.data,
            is_artist=form.is_artist.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        img = form.image.data
        file_extension = img.filename[-3:]
        hasher = hashlib.sha256(f"{img.filename}{current_user.username}{datetime.datetime.now()}".encode("utf-8"))
        new_filename = f"{hasher.hexdigest()}.{file_extension}"
        path = os.path.join(app.static_folder, "img", new_filename)
        img.save(path)
        tags = [Tag(tag=s.strip()) for s in form.tags.data.split(",")]
        new_post = Post(
            image_path=f"/static/img/{new_filename}",
            caption=form.caption.data,
            posted_at=datetime.datetime.now(),
            price=form.price.data,
        )
        new_post.tags += tags
        current_user.posts.append(new_post)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("index"))
    return render_template("create.html", title="Create", form=form)
    
@app.route("/artistpage/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = User.query.filter_by(username=username).first().posts
    return render_template('artistpage.html', user=user, posts=posts)
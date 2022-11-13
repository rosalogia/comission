from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm, SearchForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from werkzeug.urls import url_parse
import os
import datetime
import hashlib


@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        to_show_in_feed = [f.followee for f in Followers.query.filter_by(follower=current_user.id).all()]
        to_show_in_feed.append(current_user.id)
        print(to_show_in_feed)
        posts = []
        for followee in to_show_in_feed:
            f_posts = User.query.get(followee).posts
            posts += f_posts
        posts.sort(key=lambda x:x.posted_at, reverse=True)
        print(posts)
        posts = [(post, ", ".join([t.tag for t in post.tags])) for post in posts]
        return render_template("index.html", title="Home", posts=posts)
    return render_template("index.html", title="Home")

@app.route("/follow/<int:user_id>")
@login_required
def follow(user_id):
    user = User.query.get(user_id)
    f = Followers(follower=current_user.id, followee=user_id)
    db.session.add(f)
    db.session.commit()
    return redirect(f"/profile/{user.username}")

@app.route("/unfollow/<int:user_id>")
@login_required
def unfollow(user_id):
    user = User.query.get(user_id)
    f = Followers.query.filter_by(follower=current_user.id, followee=user_id).first()
    if f:
        db.session.delete(f)
        db.session.commit()
    return redirect(f"/profile/{user.username}")


@app.route("/explore", methods=["GET", "POST"])
def explore():
    form = SearchForm()
    if form.validate_on_submit():
        posts = []
        (tags, artist, max_price) = (form.search_tag.data.split(", "), form.search_artist.data, form.search_price.data if form.search_price.data > 0 else None)
        if tags:
            posts = [t.post for t in Tag.query.filter(Tag.tag.in_(tags)).all()]
        
        if artist:
            if posts:
                posts = [post for post in posts if post.artist.username == artist]
            else:
                user = User.query.filter_by(username=artist).first()
                if user:
                    posts = user.posts
                else:
                    flash(f"No artist with username {artist} was found")
        
        if max_price:
            if posts:
                posts = [post for post in posts if post.price < max_price]
            else:
                posts = Post.query.filter(Post.price < max_price).all()

            # posts = [
            #     t.post
            #     for t in Tag.query.filter(Tag.tag.in_(tag_list)).all()
            #     if t.post.artist.username == form.search_artist.data and t.post.price < form.search_price.data
            # ]

        if not posts:
            flash("No matching pictures found")
        post_cols = [[], [], []]
        for i in range(len(posts)):
            post_cols[i % 3].append(posts[i])
        print(post_cols)
        return render_template("explore.html", title="Explore", posts=post_cols, form=form)
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

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.name = form.name.data
        username = current_user.username
        db.session.add(current_user)
        db.session.commit()
        return redirect(f"/profile/{username}")
    elif request.method == "GET":
        form.username.data = current_user.username
        form.bio.data = current_user.bio
        form.name.data = current_user.name
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile/<username>")
def profile(username):
    if current_user.is_authenticated:
        if current_user.username == username:
            posts = current_user.posts
            columns = [[], [], []]
            for i in range(len(posts)):
                columns[i % 3].append(posts[i])

            return render_template("profile.html", user=current_user, posts=columns, title="Profile")
        else:
            following = False
            user = User.query.filter_by(username=username).first()
            posts = user.posts
            columns = [[], [], []]
            for i in range(len(posts)):
                columns[i % 3].append(posts[i])

            if Followers.query.filter_by(follower=current_user.id, followee=user.id).first():
                following = True
            return render_template("profile.html", user=user, posts=columns, title="Profile", following=following)

    user = User.query.filter_by(username=username).first()
    posts = user.posts
    columns = [[], [], []]
    for i in range(len(posts)):
        columns[i % 3].append(posts[i])

    return render_template("profile.html", user=user, posts=columns, title="Profile", following=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            name=form.name.data,
            email=form.email.data,
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
        hasher = hashlib.sha256(
            f"{img.filename}{current_user.username}{datetime.datetime.now()}".encode(
                "utf-8"
            )
        )
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
    return render_template("artistpage.html", user=user, posts=posts)


@app.route("/listing/<post_id>")
def listing(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    artist = User.query.filter_by(id=post.artist_id).first()
    return render_template("listing.html", post=post, artist=artist)


@app.route("/success")
def success():
    username = current_user.username
    return render_template("success.html", username=username)

from flask import Blueprint
from app import db, bcrypt, es
from flask import render_template, flash, redirect, url_for, request
from app.users.forms import (
    SignUpForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm,
    AddWords,
)
from app.models import User, NewWords
from flask_login import login_user, login_required, current_user, logout_user
from app.users.utils import send_reset_email
from hashlib import sha256
import json


users = Blueprint("users", __name__)


def generate_access_link(name: str) -> str:
    return sha256(f"{name}".encode()).hexdigest()


def find_user_by_access_link(access_link: str) -> str:
    return User.query.filter_by(access_link=access_link).first()


@users.route("/main", methods=["GET", "POST"])
def main():
    title = "Homepage"
    if current_user.is_authenticated:
        return render_template("layout.html", title=title)
    return render_template("layout.html", title=title)


@users.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("users.main"))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(name=form.name.data,
                    email=form.email.data,
                    password=hashed_password,
                    access_link=generate_access_link(form.name.data))
        db.session.add(user)
        db.session.commit()

        _name = user.name
        esdata = json.dumps(
            {
                "name": _name,
            }
        )
        es.index(index="names", doc_type="names", body=esdata)
        print("index added!")
        flash("Your account has been successfully created!", "success")    # not working
        return redirect(url_for("users.login"))
  
    return render_template("signup.html", title="Sign up", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.main"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("users.main"))
        else:
            flash("Login Unsuccessfull. Please check email and password.", "danger")
    return render_template("login.html", title="Sign up", form=form)


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    image_file = current_user.img_file
    access_to_telebot = current_user.access_link
    words = current_user.new_user_words
    points = (current_user.user_points / 300) * 100
    current_user.user_points = round(points, 1)
    form = AddWords()
    if form.validate_on_submit:
        if form.words.data:
            word_to_db = NewWords(user_word=form.words.data)
            db.session.add(word_to_db)
            words.append(word_to_db)
            db.session.commit()
            return redirect(url_for("users.account"))
    return render_template(
        "account.html",
        form=form,
        title="Account",
        image_file=image_file,
        access_to_telebot=access_to_telebot,
        words=words,
        )


@users.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = UpdateAccountForm()
    if form.validate_on_submit():    
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.telegram_info = form.telegram_info.data
        current_user.instagram = form.instagram.data
        current_user.twitter = form.twitter.data
        current_user.facebook = form.facebook.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.telegram_info.data = current_user.telegram_info
    image_file = current_user.img_file
    return render_template("settings.html", title="Account", image_file=image_file, form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("users.main"))


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("users.main"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect("users.login")
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("users.main"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")    # not working
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
  
    image_file = current_user.img_file
    return render_template("account.html", title="Account", image_file=image_file)


@users.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    users = User.query.order_by(User.user_points.desc()).all()
    headings = ("Position", "Name", "Level", "Score")
    title = "dashboard"
    return render_template("dashboard.html",
                           users=users,
                           title=title,
                           headings=headings,
                           )


@users.route("/user/<username>", methods=["GET"])
@login_required
def profile(username):
    user = User.query.filter_by(name=username).first_or_404()
    image_file = user.img_file
    return render_template("profile.html", user=user, image_file=image_file)


@users.route("/search/", methods=["GET", "POST"])
@login_required
def search():
    q = request.args.get("q")
    if q is not None:
        body = {
                "query": {
                    "multi_match": {
                        "query": q,
                        "type": "phrase_prefix",
                        "fields": ["name"]
                    }
                }
            }
        res = es.search(index="names", doc_type="names", size=5, body=body)
        print("res", res)
        return render_template("search.html", res=res)
    else:
        return render_template("404.html")

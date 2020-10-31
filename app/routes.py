from app import app, db, bcrypt
from flask import render_template, flash, redirect, url_for, request
from app.forms import SignUpForm, LoginForm
from app.models import User
from flask_login import login_user, login_required, current_user, logout_user


@app.route("/main", methods=["GET", "POST"])
def main():
    title = "Homepage"
    return render_template("layout.html", title=title)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Your account has been successfully created!", "success")    # not working
        return redirect(url_for("login"))
       
    return render_template("signup.html", title="Sign up", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main"))
        else:
            flash("Login Unsuccessfull. Please check email and password.", 'danger')
    return render_template("login.html", title="Sign up", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    return render_template("account.html", title="Account")
    

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    pass



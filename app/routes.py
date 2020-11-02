from app import app, db, bcrypt, mail
from flask import render_template, flash, redirect, url_for, request, current_app
from app.forms import SignUpForm, LoginForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm
from app.models import User
from flask_login import login_user, login_required, current_user, logout_user
from flask_mail import Message


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
    image_file = current_user.img_file
    return render_template("account.html", title="Account", image_file=image_file)


def send_reset_email(user):
    token = user.get_reset_token()
    body = f'''To reset your password, visit the following link:
{url_for("reset_token", token=token, _external=True)}
  
If you did not make this request then simply ignore this email.
'''
    msg = Message(
        "Password reset request",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user.email],
        body=body,
        )
    mail.send(msg)
 

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect("login")
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")    # not working
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
  
    image_file = current_user.img_file
    return render_template("account.html", title="Account", image_file=image_file)
    

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = UpdateAccountForm()
    if form.validate_on_submit():        
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.telegram_info = form.telegram_info.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.telegram_info.data = current_user.telegram_info
    image_file = current_user.img_file
    return render_template("settings.html", title="Account", image_file=image_file, form=form)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    pass

from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import SignUpForm, LoginForm


@app.route("/main", methods=["GET", "POST"])
def main():
    title = "Homepage"
    return render_template("layout.html", title=title)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        flash("Your account has been successfully created!", "success")
        return redirect(url_for("main"))
       
    return render_template("signup.html", title="Sign up", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for("main"))
    return render_template("login.html", title="Sign up", form=form)




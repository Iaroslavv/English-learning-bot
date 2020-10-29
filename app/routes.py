from app import app
from flask import render_template


@app.route("/main", methods=["GET", "POST"])
def main():
    title = "Homepage"
    return render_template("layout.html", title=title)

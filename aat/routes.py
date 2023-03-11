from flask import render_template, flash, request, redirect, url_for
from aat import app, db

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
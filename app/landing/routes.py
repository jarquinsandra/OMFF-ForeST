"""

AUTOR: jarquinsandra


"""

from flask import render_template, url_for
from . import landing

from app.models import Files

@landing.route("/files_indications")
def indications():
    return render_template("file_requirements.html")

@landing.route("/db_organization")
def db_organization():
    return render_template("db_organization.html")

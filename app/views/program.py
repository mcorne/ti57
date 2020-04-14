from flask import Blueprint, render_template
from flask_babel import _

bp = Blueprint("program", __name__)


@bp.route("/")
def index():
    return render_template("program/index.html")

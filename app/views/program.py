from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_babel import _

bp = Blueprint("program", __name__)


@bp.route("/")
def index():
    return render_template("program/index.html")

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

bp = Blueprint("proram", __name__)


@bp.route("/")
@bp.route("/page/<int:page>")
def index(page=1):
    # Not using the login_required decorator so the login message is not displayed.
    # The login message is unwanted when a user click on a link to the app.
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))

    issue_type = current_user.role.get_issue_type()
    filter_by = {"type": issue_type} if issue_type != "all" else {}

    issue_sort = Issue.get_issue_sort()
    # desc(func.ifnull("updated", "created")) does not actually sort result!
    if issue_sort == "status":
        order_by = ["status", text("IFNULL(updated, created)")]  # like download
    else:
        order_by = [text("IFNULL(updated, created) DESC")]

    issue_page = (
        Issue.query.filter_by(**filter_by)
        .order_by(*order_by)
        .paginate(page, per_page=20)
    )
    issue_id = request.args.get("issue_id")
    template = render_template(
        "issue/index.html", issue_page=issue_page, issue_id=issue_id
    )

    response = make_response(template)
    max_age = 3600 * 24 * 30  # 30 days
    response.set_cookie("issue_sort", issue_sort, max_age)
    response.set_cookie("issue_type", issue_type, max_age)
    return response

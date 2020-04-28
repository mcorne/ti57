import re

import jinja2
from flask import Blueprint
from jinja2 import Markup, escape

bp = Blueprint("filters", __name__)


@jinja2.contextfilter
@bp.app_template_filter()
def nl2br_and_nbsp(context, string):
    escaped = escape(string)
    fixed = re.sub(r"(\r\n|\r|\n)", "<br>", escaped)
    fixed = fixed.replace(" ", "&nbsp;")
    if context.eval_ctx.autoescape:
        fixed = Markup(fixed)
    return fixed

from flask import g, make_response, render_template, abort
from werkzeug.exceptions import HTTPException
from datetime import datetime
from cne import app
import os


@app.before_request
def define_globals():
    g.UNDER_MAINTENANCE = False


@app.before_request
def check_under_maintenance():
    if os.path.exists('maintenance'):
        g.UNDER_MAINTENANCE = True

        abort(503)


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(503)
def http_error_handler(error, without_code=False):
    if isinstance(error, HTTPException):
        error = error.code
    elif not isinstance(error, int):
        error = 500

    body = render_template('errors/{}.html'.format(error))

    if not without_code:
        return make_response(body, error)
    else:
        return make_response(body)

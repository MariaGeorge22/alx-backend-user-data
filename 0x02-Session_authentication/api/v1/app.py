#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
import os


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

app.debug = True

auth = None

AUTH_TYPE = getenv("AUTH_TYPE")
BASIC_AUTH = 'basic_auth'
SESSION_AUTH = 'session_auth'
SESSION_EXP_AUTH = 'session_exp_auth'
SESSION_DB_AUTH = 'session_db_auth'

if AUTH_TYPE:
    if AUTH_TYPE == BASIC_AUTH:
        from api.v1.auth.basic_auth import BasicAuth
        auth = BasicAuth()
    elif AUTH_TYPE == SESSION_AUTH:
        from api.v1.auth.session_auth import SessionAuth
        auth = SessionAuth()
    elif AUTH_TYPE == SESSION_EXP_AUTH:
        from api.v1.auth.session_exp_auth import SessionExpAuth
        auth = SessionExpAuth()
    elif AUTH_TYPE == SESSION_DB_AUTH:
        from api.v1.auth.session_db_auth import SessionDBAuth
        auth = SessionDBAuth()
    else:
        from api.v1.auth.auth import Auth
        auth = Auth()

excluded_paths = ['/api/v1/status/',
                  '/api/v1/unauthorized/',
                  '/api/v1/forbidden/',
                  '/api/v1/auth_session/login/']


@app.before_request
def auth_request():
    """ Auth Handler """
    if auth:
        path = request.path
        if auth.require_auth(path, excluded_paths):
            if not (auth.authorization_header(request)
                    or auth.session_cookie(request)):
                abort(401)
            if not auth.current_user(request):
                abort(403)
            request.current_user = auth.current_user(request)


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """ Unauthorized handler
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """ Forbidden handler
    """
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)

#!/usr/bin/env python3
""" Module of Session Auth views
"""
from os import getenv
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login():
    """ create a Session ID for the User ID """
    email = request.form.get("email")
    password = request.form.get("password")
    if not email:
        return jsonify({"error": "email missing"}), 400
    if not password:
        return jsonify({"error": "password missing"}), 400

    users = User.search({"email": email})
    if not users:
        return jsonify({"error": "no user found for this email"}), 404

    current_user = None
    for user in users:
        if user.is_valid_password(password):
            current_user = user
            break
    if not current_user:
        return jsonify({"error": "wrong password"}), 401

    from api.v1.app import auth
    session = auth.create_session(current_user.id)

    response = jsonify(current_user.to_json())
    session_name = getenv("SESSION_NAME")
    response.set_cookie(session_name, session)
    return response


@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def logout():
    """ deletes the user session / logout """
    from api.v1.app import auth
    if not auth.destroy_session(request):
        abort(404)
    return jsonify({}), 200

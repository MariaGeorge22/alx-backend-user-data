#!/usr/bin/env python3
""" integration test """

import requests

HOST = "http://localhost:5000"
EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


def register_user(email: str, password: str) -> None:
    """ register user """
    endpoint = "/users"
    method = "POST"
    data = {"email": email, "password": password}
    response = requests.request(method=method, url=HOST+endpoint, data=data)
    assert(response.status_code == 200)
    expected_response = {"email": email, "message": "user created"}
    assert(response.json() == expected_response)


def log_in_wrong_password(email: str, password: str) -> None:
    """ log in wrong password """
    endpoint = "/sessions"
    method = "POST"
    data = {"email": email, "password": password}
    response = requests.request(method=method, url=HOST+endpoint, data=data)
    assert(response.status_code == 401)


def log_in(email: str, password: str) -> str:
    """ log in """
    endpoint = "/sessions"
    method = "POST"
    data = {"email": email, "password": password}
    response = requests.request(method=method, url=HOST+endpoint, data=data)
    assert(response.status_code == 200)
    session_id = response.cookies.get("session_id")
    assert(session_id is not None)
    expected_response = {"email": email, "message": "logged in"}
    assert(response.json() == expected_response)
    return session_id


def profile_unlogged() -> None:
    """ profile unlogged """
    endpoint = "/profile"
    method = "GET"
    response = requests.request(method=method, url=HOST+endpoint)
    assert(response.status_code == 403)


def profile_logged(session_id: str) -> None:
    """ profile logged """
    endpoint = "/profile"
    method = "GET"
    cookies = {"session_id": session_id}
    response = requests.request(method=method, url=HOST+endpoint,
                                cookies=cookies)
    assert(response.status_code == 200)
    email = response.json().get("email")
    assert(email is not None)


def log_out(session_id: str) -> None:
    """ log out """
    endpoint = "/sessions"
    method = "DELETE"
    cookies = {"session_id": session_id}
    response = requests.request(method=method, url=HOST+endpoint,
                                cookies=cookies)
    assert(len(response.history) == 1)
    assert(response.history[0].status_code == 302)
    assert(response.status_code == 200)
    assert(response.url == HOST+"/")


def reset_password_token(email: str) -> str:
    """ reset password token """
    endpoint = "/reset_password"
    method = "POST"
    data = {"email": email}
    response = requests.request(method=method, url=HOST+endpoint, data=data)
    assert(response.status_code == 200)
    body = response.json()
    response_email = body.get("email")
    response_reset_token = body.get("reset_token")
    assert(response_email == email)
    assert(response_reset_token is not None)
    return response_reset_token


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """ update password """
    endpoint = "/reset_password"
    method = "PUT"
    data = {"email": email, "reset_token": reset_token,
            "new_password": new_password}
    response = requests.request(method=method, url=HOST+endpoint, data=data)
    assert(response.status_code == 200)
    expected_response = {"email": email, "message": "Password updated"}
    assert(response.json() == expected_response)


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)

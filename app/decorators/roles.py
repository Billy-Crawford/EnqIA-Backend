from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt
)

def admin_required():

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            if claims.get("role") != "admin":
                return jsonify({
                    "message": "Admin access required"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper

def researcher_required():

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            if claims.get("role") != "researcher":
                return jsonify({
                    "message": "Researcher access required"
                }), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper

def respondent_required():

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            if claims.get("role") != "respondent":
                return jsonify({
                    "message": "Respondent access required"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper


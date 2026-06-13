from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from app.extensions.db import db
from app.models.user import User
from werkzeug.security import check_password_hash

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.decorators.roles import (
    admin_required,
    researcher_required
)

from app.schemas import UserRegisterSchema

from flasgger import swag_from

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
register_schema = UserRegisterSchema()

@auth_bp.route("/register", methods=["POST"])
@swag_from({
    "tags": ["Authentication"],
    "responses": {
        201: {
            "description": "User created"
        }
    }
})

def register():

    try:
        data = register_schema.load(
            request.get_json(),
        )
    except ValidationError as err:
        return jsonify(err.messages), 400

    firstname = data.get("firstname")
    lastname = data.get("lastname")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    user = User(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    }), 201


@auth_bp.route("/login", methods=["POST"])
@swag_from({
    "tags": ["Authentication"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string"
                    },
                    "password": {
                        "type": "string"
                    }
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Login successful"
        },
        401: {
            "description": "Invalid credentials"
        }
    }
})
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "message": "Invalid credentials"
        }), 401

    if not check_password_hash(user.password, password):
        return jsonify({
            "message": "Invalid credentials"
        }), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "email": user.email
        }
    )

    refresh_token = create_refresh_token(
        identity=str(user.id),
    )

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    claims =get_jwt()

    return jsonify({
        "user_id": user_id,
        "email": claims.get("email"),
        "role": claims.get("role")
    }), 200

@auth_bp.route("/admin-test", methods=["GET"])
@admin_required()
def admin_test():

    return jsonify({
        "message": "Welcome Admin"
    })

@auth_bp.route("/researcher-test", methods=["GET"])
@researcher_required()
def researcher_test():

    return jsonify({
        "message": "Welcome Researcher"
    })






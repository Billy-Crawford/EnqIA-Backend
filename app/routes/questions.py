# app/routes/questions.py

from flask import Blueprint, jsonify, request
from flasgger import swag_from

from flask_jwt_extended import get_jwt_identity, get_jwt

from app.extensions.db import db
from app.models.question import Question
from app.models.survey import Survey

from app.decorators.roles import roles_required


questions_bp = Blueprint(
    "questions",
    __name__,
    url_prefix="/questions"
)


# ======================================================
# CREATE QUESTION
# ======================================================
@questions_bp.route("/survey/<int:survey_id>", methods=["POST"])
@roles_required(["admin", "researcher"])
def create_question(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()

    allowed_types = [
        "single_choice",
        "multiple_choice",
        "likert",
        "text"
    ]

    if data.get("type") not in allowed_types:
        return jsonify({"message": "Invalid question type"}), 400

    question = Question(
        survey_id=survey.id,
        title=data.get("title"),
        type=data.get("type"),
        options=data.get("options")
    )

    db.session.add(question)
    db.session.commit()

    return jsonify({
        "message": "Question created successfully",
        "question_id": question.id
    }), 201


# ======================================================
# GET QUESTIONS
# ======================================================
@questions_bp.route("/survey/<int:survey_id>", methods=["GET"])
def get_question(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    questions = Question.query.filter_by(survey_id=survey.id).all()

    return jsonify([
        {
            "id": q.id,
            "title": q.title,
            "type": q.type,
            "options": q.options
        }
        for q in questions
    ]), 200


# ======================================================
# UPDATE QUESTION
# ======================================================
@questions_bp.route("/<int:question_id>", methods=["PUT"])
@roles_required(["admin", "researcher"])
def update_question(question_id):

    question = Question.query.get(question_id)

    if not question:
        return jsonify({"message": "Question not found"}), 404

    survey = Survey.query.get(question.survey_id)

    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()

    question.title = data.get("title", question.title)
    question.type = data.get("type", question.type)
    question.options = data.get("options", question.options)

    db.session.commit()

    return jsonify({"message": "Question updated successfully"}), 200


# ======================================================
# DELETE QUESTION
# ======================================================
@questions_bp.route("/<int:question_id>", methods=["DELETE"])
@roles_required(["admin", "researcher"])
def delete_question(question_id):

    question = Question.query.get(question_id)

    if not question:
        return jsonify({"message": "Question not found"}), 404

    survey = Survey.query.get(question.survey_id)

    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(question)
    db.session.commit()

    return jsonify({"message": "Question deleted successfully"}), 200


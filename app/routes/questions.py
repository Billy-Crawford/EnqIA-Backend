from flask import Blueprint, jsonify, request

from flask_jwt_extended import get_jwt_identity
from sqlalchemy.ext.asyncio import result
from sqlalchemy.sql.functions import current_user

from app.extensions.db import db
from app.models.question import Question
from app.models.survey import Survey

from app.decorators.roles import researcher_required


questions_bp = Blueprint(
    "questions",
    __name__,
    url_prefix="/questions"
)

@questions_bp.route("/survey/<int:survey_id>", methods=["POST"])
@researcher_required()
def create_question(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }), 404

    current_user_id = int(get_jwt_identity())

    if survey.researcher_id != current_user_id:
        return jsonify({
            "message": "Unauthorized access"
        }), 403

    data = request.get_json()

    question_type = data.get("type")

    allowed_types =[
        "single_choice",
        "multiple_choice",
        "likert",
        "text"
    ]

    if question_type not in allowed_types:
        return jsonify({
            "message": "Invalid question type"
        }), 400

    question = Question(
        survey_id=survey.id,
        title=data.get("title"),
        type=question_type,
        options=data.get("options")
    )

    db.session.add(question)
    db.session.commit()

    return jsonify({
        "message": "Question created successfully",
        "question_id": question.id
    }), 201

@questions_bp.route("/survey/<int:survey_id>/", methods=["GET"])
def get_question(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }), 404

    questions = Question.query.filter_by(
        survey_id=survey.id
    ).all()

    result = []

    for question in questions:

        result.append({
            "id": question.id,
            "title": question.title,
            "type": question.type,
            "options": question.options
        })

    return jsonify(result), 200

@questions_bp.route("/<int:question_id>/", methods=["PUT"])
@researcher_required()
def update_question(question_id):

    question = Question.query.get(question_id)

    if not question:
        return jsonify({
            "message": "Question not found"
        }), 404

    survey = Survey.query.get(
        question.survey_id
    )

    current_user_id = int(
        get_jwt_identity()
    )

    if survey.researcher_id != current_user_id:
        return jsonify({
            "message": "Unauthorized access"
        }), 403

    data = request.get_json()

    question.title = data.get(
        "title",
        question.title
    )

    question.type = data.get(
        "type",
        question.type
    )

    question.options = data.get(
        "options",
        question.options
    )

    db.session.commit()

    return jsonify({
        "message": "Question updated successfully",
    })


@questions_bp.route("/<int:question_id>", methods=["DELETE"])
@researcher_required()
def delete_question(question_id):

    question = Question.query.get(question_id)


    if not question:
        return jsonify({
            "message": "Question not found"
        }),404


    survey = Survey.query.get(
        question.survey_id
    )


    current_user_id = int(
        get_jwt_identity()
    )


    if survey.researcher_id != current_user_id:
        return jsonify({
            "message": "Unauthorized"
        }),403


    db.session.delete(question)
    db.session.commit()


    return jsonify({
        "message": "Question deleted successfully"
    })




from flasgger import swag_from
from flask import Blueprint, jsonify, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from app.extensions.db import db

from app.models.answer import Answer
from app.models.answer_option import AnswerOption
from app.models.question import Question
from app.models.survey import Survey

from app.decorators.roles import respondent_required, researcher_required

answers_bp = Blueprint(
    "answers",
    __name__,
    url_prefix="/answers"
)

@swag_from({
    "tags": ["Answers"],
    "responses": {
        201: {
            "description": "Answers submitted"
        }
    }
})
@answers_bp.route(
    "/survey/<int:survey_id>",
    methods=["POST"]
)
@answers_bp.route(
    "/survey/<int:survey_id>",
    methods=["POST"]
)
@respondent_required()
def submit_answers(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }),404

    if survey.archived_at:
        return jsonify({
            "message":
                "Survey is archived"
        }), 400

    if not survey.is_published:
        return jsonify({
            "message":
                "Survey is not published"
        }), 400

    user_id = int(get_jwt_identity())

    # Vérifier si l'utilisateur a déjà répondu

    existing_answer = (
        Answer.query
        .join(Question)
        .filter(
            Question.survey_id == survey_id,
            Answer.user_id == user_id
        )
        .first()
    )

    if existing_answer:
        return jsonify({
            "message": "You already answered this survey"
        }), 400


    data = request.get_json()


    answers_data = data.get("answers")


    if not answers_data:

        return jsonify({
            "message": "No answers provided"
        }),400

    for item in answers_data:

        question = Question.query.get(
            item.get("question_id")
        )

        if not question:

            return jsonify({
                "message": "Question not found"
            }),404


        value = item.get("value")

        # Validation Likert

        if question.type == "likert":

            if int(value) not in [1,2,3,4,5]:

                return jsonify({
                    "message":
                    "Likert value must be between 1 and 5"
                }),400

        # Validation choix unique

        if question.type == "single_choice":

            if value not in question.options:

                return jsonify({
                    "message":
                    "Invalid option"
                }),400


        # Validation choix multiple

        if question.type == "multiple_choice":

            for option in value:

                if option not in question.options:

                    return jsonify({
                        "message":
                        "Invalid option"
                    }),400

        answer_value = None

        if question.type != "multiple_choice":
            answer_value = str(value)

        answer = Answer(
            question_id=question.id,
            user_id=user_id,
            value=answer_value
        )


        db.session.add(answer)

        db.session.flush()

        # Stockage des choix multiples

        if question.type == "multiple_choice":

            for option in value:

                answer_option = AnswerOption(
                    answer_id=answer.id,
                    option_value=option
                )

                db.session.add(answer_option)

    db.session.commit()

    return jsonify({
        "message":
        "Answers submitted successfully"
    }),201


@swag_from({
    "tags": ["Answers"],
    "responses": {
        201: {
            "description": "Answers submitted"
        }
    }
})
@answers_bp.route(
    "/survey/<int:survey_id>",
    methods=["GET"]
)
@jwt_required()
@researcher_required()
def get_survey_answers(survey_id):

    researcher_id = int(get_jwt_identity())

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }), 404

    # Vérifier que le chercheur possède cette enquête

    if survey.researcher_id != researcher_id:

        return jsonify({
            "message": "You cannot access this survey"
        }),403

    answers = Answer.query.join(
        Question
    ).filter(
        Question.survey_id == survey_id
    ).all()

    result = []

    for answer in answers:

        result.append({

            "answer_id": answer.id,
            "question_id": answer.question_id,
            "respondent_id": answer.user_id,
            "value": answer.value,
            "created_at": answer.created_at

        })

    return jsonify(result),200

@swag_from({
    "tags": ["Answers"],
    "responses": {
        200: {
            "description": "My answers"
        }
    }
})
@answers_bp.route(
    "/my",
    methods=["GET"]
)

@jwt_required()
def get_my_answers():

    user_id = int(get_jwt_identity())

    answers = Answer.query.filter_by(
        user_id=user_id
    ).all()

    result = []

    for answer in answers:

        result.append({

            "answer_id": answer.id,

            "question_id": answer.question_id,

            "value": answer.value,

            "created_at": answer.created_at

        })


    return jsonify(result), 200




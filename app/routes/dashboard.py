from flask import Blueprint, jsonify

from flask_jwt_extended import (
    get_jwt_identity
)

from app.decorators.roles import (
    researcher_required
)

from app.models.survey import Survey
from app.models.question import Question
from app.models.answer import Answer

from app.models.user import User
from app.decorators.roles import admin_required


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

@dashboard_bp.route(
    "/researcher",
    methods=["GET"]
)
@researcher_required()
def researcher_dashboard():

    researcher_id = int(
        get_jwt_identity()
    )

    surveys = Survey.query.filter_by(
        researcher_id=researcher_id
    ).all()

    survey_ids = [
        survey.id
        for survey in surveys
    ]

    survey_count = len(
        surveys
    )

    published_count = len([
        survey
        for survey in surveys
        if survey.is_published
    ])

    question_count = Question.query.filter(
        Question.survey_id.in_(
            survey_ids
        )
    ).count()

    answer_count = (
        Answer.query
        .join(Question)
        .filter(
            Question.survey_id.in_(
                survey_ids
            )
        )
        .count()
    )

    return jsonify({

        "surveys":
            survey_count,

        "published_surveys":
            published_count,

        "questions":
            question_count,

        "responses":
            answer_count

    }),200

@dashboard_bp.route(
    "/admin",
    methods=["GET"]
)
@admin_required()
def admin_dashboard():

    users_count = User.query.count()

    researchers_count = User.query.filter_by(
        role="researcher"
    ).count()

    respondents_count = User.query.filter_by(
        role="respondent"
    ).count()

    surveys_count = Survey.query.count()

    published_surveys_count = Survey.query.filter_by(
        is_published=True
    ).count()

    questions_count = Question.query.count()

    answers_count = Answer.query.count()

    return jsonify({

        "users": users_count,

        "researchers": researchers_count,

        "respondents": respondents_count,

        "surveys": surveys_count,

        "published_surveys": published_surveys_count,

        "questions": questions_count,

        "responses": answers_count

    }),200



from statistics import mean, median
from collections import Counter

from sqlalchemy import func

from app.models.question import Question
from app.models.answer import Answer
from app.models.user import User

from app.utils.filters import check_age_group


def generate_statistics(
    survey_id,
    gender=None,
    age_group=None,
    date=None
):

    questions = Question.query.filter_by(
        survey_id=survey_id
    ).all()


    statistics = []


    for question in questions:

        query = Answer.query.join(
            User,
            Answer.user_id == User.id
        ).filter(
            Answer.question_id == question.id
        )

        if gender:
            query = query.filter(
                User.gender == gender
            )

        if date:
            query = query.filter(
                func.date(Answer.created_at) == date
            )

        answers = query.all()

        if age_group:

            filtered_answers = []

            for answer in answers:

                if (
                        answer.user.age is not None
                        and
                        check_age_group(
                            answer.user.age,
                            age_group
                        )
                ):
                    filtered_answers.append(
                        answer
                    )

            answers = filtered_answers

        result = {
            "question_id": question.id,
            "question": question.title,
            "type": question.type
        }


        # =========================
        # Question texte libre
        # =========================

        if question.type == "text":

            result["responses"] = [
                answer.value
                for answer in answers
            ]


        # =========================
        # Question choix unique
        # =========================

        elif question.type == "single_choice":

            values = [
                answer.value
                for answer in answers
            ]

            result["distribution"] = dict(
                Counter(values)
            )


        # =========================
        # Question choix multiple
        # =========================

        elif question.type == "multiple_choice":

            values = []

            for answer in answers:

                for option in answer.options:
                    values.append(

                        option.option_value

                    )

            result["distribution"] = dict(

                Counter(values)

            )


        # =========================
        # Question Likert
        # =========================

        elif question.type == "likert":

            values = [
                int(answer.value)
                for answer in answers
            ]


            if values:

                result["average"] = round(
                    mean(values),
                    2
                )

                result["median"] = median(
                    values
                )


            result["distribution"] = dict(
                Counter(values)
            )


        statistics.append(result)


    return statistics


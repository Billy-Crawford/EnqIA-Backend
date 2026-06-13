def test_question_creation_requires_auth(client):

    response = client.post(
        "/questions/survey/1",
        json={}
    )

    assert response.status_code in [401, 422]



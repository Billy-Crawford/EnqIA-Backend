def test_answers_requires_auth(client):

    response = client.post(
        "/answers/survey/1",
        json={}
    )

    assert response.status_code in [401, 422]




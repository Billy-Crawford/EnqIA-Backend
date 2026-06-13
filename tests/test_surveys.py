def test_surveys_requires_auth(client):

    response = client.get("/surveys/")

    assert response.status_code in [401, 422]



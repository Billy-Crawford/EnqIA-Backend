def test_statistics_requires_auth(client):

    response = client.get(
        "/surveys/1/statistics"
    )

    assert response.status_code in [401, 422]


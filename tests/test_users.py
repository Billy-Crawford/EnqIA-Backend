def test_users_endpoint_requires_auth(client):

    response = client.get("/users/")

    assert response.status_code in [401, 422]


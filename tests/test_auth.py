def test_register(client):
    rsponse = client.post(
        "auth/register",
        json={
            "firstname": "Crawford",
            "lastname": "Lorenzo",
            "email": "crawford@test.com",
            "password": "123456",
            "role": "respondent"
        }
    )

    assert rsponse.status_code == 201

def test_login(client):

    client.post(
        "/auth/register",
        json={
            "firstname": "Crawford",
            "lastname": "Lorenzo",
            "email": "crawford@test.com",
            "password": "123456",
            "role": "respondent"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "crawford@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "access_token" in data

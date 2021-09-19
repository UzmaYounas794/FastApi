from os import access
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
def test_create_item():
    response = client.get(
        "/questions/1",
        headers={"X-Token": "coneofsilence"},
        # json={"question_text": "The Foo Barters"},
    )
    assert response.json() == {'detail': 'Question not found'}
    # assert response.status_code == 200
    # assert response.json() == {
    #
    #     "question_text": "The Foo Barters",
    #
    # }

#
# def test_create_user():
#     response = client.post(
#         "/signup/",
#         json={
#             "email": "user@example.com",
#             "full_name": "user",
#             "hashed_password": "password",
#         },
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["email"] == "user@example.com"
#     assert "id" in data
#     user_id = data["id"]
#
#
#
# good_credentials = {
#     "username": "deadpool@example.com",
#     "password": "chimichangas4life",
# }
#
# def test_unauthenticated_user_cant_create_posts():
#
#     post = dict(id=1, question="run a mile")
#     response = client.post("/questions/", data=post)
#     assert response.status_code == 401
#
#
#
#
# def test_user_can_obtain_auth_token():
#     response = client.post("/token/", data=good_credentials)
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert "token_type" in response.json()
#
#
#
# def test_security():
#     response = client.get("/questions/")
#     assert response.status_code == 200, response.text

#
# @pytest.mark.parametrize("routes, expected", [
#     ("/questions/", 200),
#     ("/questions/1", 401),
#
#
# ])
# def test_routes(routes,expected):
#     response = client.get(routes)
#     assert response.status_code == expected


# def test_post_question():
#
#     # access_token = create_access_token('testuser')
#     # access_token = create_access_token(
#     #     {"username": "user@example.com", "password": "password"}
#     # )
#     access_token = create_access_token(good_credentials)
#     headers = {"Authorization": "Bearer {}".format(access_token)}
#     response = client.get("/questions/1", headers=headers)
#
#     assert response.status_code == 200


# def test_create_item():
#     response = client.post(
#         "/questions/",
#         headers=headers,
#         json={"id": 1, "question_text": "i am a question"},
#     )
#     assert response.status_code == 200
#     assert response.json() == {"id": 1, "question_text": "i am a question"}




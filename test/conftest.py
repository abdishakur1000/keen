from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db, Base
from app.main import app
from app import models
from app.oauth2 import create_access_token
from alembic import command
from app.config import settings


# @pytest.fixture(scope='module')
@pytest.fixture()
def session():
    print('my session fixture ran')
    # drop all before we test
    Base.metadata.drop_all(bind=engine)
    # create new test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# @pytest.fixture(scope='module')
@pytest.fixture()
def client(session):
    # command.upgrade('head')# TODO WAA IN AAD SAMAYASAA ALEMBIC
    # command.downgrade('base')
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {'email': 'abdishakur0@gmail.com',
                 'password': 'agree101'}
    res = client.post('/users/', json=user_data)
    assert res.status_code == 201
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {'email': 'abdishakur12@gmail.com',
                 'password': 'agree101'}
    res = client.post('/users/', json=user_data)
    assert res.status_code == 201
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({'user_id': test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f'Bearer {token}'
    }
    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{
        'title': 'first title',
        'content': 'first content',
        'owner_id': test_user['id']
    },
        {
            "title": "2nd title",
            "content": "2nd content",
            "owner_id": test_user['id']
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user['id']
        },
        {
            "title": "4rd title",
            "content": "4rd content",
            "owner_id": test_user2['id']
        }
    ]
    # we can use the map function
    def creat_post_model(post):
        return models.Post(**post)
    post_map = map(creat_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts

    # # python way of doing this way
    # session.add_all([models.Post(title='first title', content='first content',
    # owner_id=test_user['id']),
    #              models.Post(title='2nd title', content='2nd content',
    #              owner_id=test_user['id']),
    #                  models.Post(title='3rd title', content='3rd content',
    #                  owner_id=test_user['id'])])
    # session.commit()
    # session.query(models.Post).all()
    # posts = session.query(models.Post).all()
    # return posts


SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:agree101@localhost:5432/test_abdi'
# SQLALCHEMY_DATABASE_URL =\
#     f'postgresql://{settings.D_username}:' \
#     f'{settings.D_password}@{settings.D_hostname}:' \
#     f'{settings.D_port}/{settings.D_name}_test'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from flask import g, session, Blueprint
from northwind.db import get_db
from northwind.auth import login_required

def test_register(client, app, auth):
    assert client.get('/auth/register').status_code == 200

    # Test invalid registration attempts
    response = auth.register(username='', password='test')
    response_text = response.data.decode('utf-8')
    assert 'User ID is required.' in response_text

    response = auth.register(username='', password='')
    response_text = response.data.decode('utf-8')
    assert 'User ID is required.' in response_text

    response = auth.register(username='test', password='')
    response_text = response.data.decode('utf-8')
    assert 'Password is required.' in response_text

    # Test successful registration and redirection
    response = auth.register()
    assert response.headers['Location'] == '/auth/login',  "Post register redirect location is incorrect."

    # Check if the user was added to the database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM Authentication WHERE UserID = 'test'",
        ).fetchone() is not None


def test_register_existing_user(auth):
    auth.register()
    response = auth.register()
    response_text = response.data.decode('utf-8')
    assert 'Customer already exists—try logging in!' in response_text


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    auth.register()

    # Test invalid login attempts
    response = auth.login(username='invalid', password='test')
    assert b'Incorrect user id.' in response.data

    response = auth.login(username='test', password='invalid')
    assert b'Incorrect password.' in response.data

    # Test successful login and redirection
    response = auth.login()
    assert response.headers['Location'] == '/', "Post login redirect location is incorrect."

    # Check if the user_id is stored in the session
    with client:
        client.get('/')
        assert session['user_id'] == 'test'


def test_logout(client, auth):
    auth.register()
    auth.login()
    with client:
        client.get('/')
        assert session['user_id'] == 'test'
        auth.logout()
        assert 'test' not in session


def test_load_logged_in_user(client, auth):
    auth.register()
    auth.login()
    with client:
        client.get('/')
        assert g.user['UserID'] == 'test'


def test_login_required(client, auth, app):
    # Create a temporary blueprint for testing
    test_bp = Blueprint('test_bp', __name__)

    # Currently no protected routes to test, so need to make a fake one to check authentication
    # TODO replace this with a real protected route when one is added.
    @test_bp.route('/protected')
    @login_required
    def protected():
        return 'Protected'
    app.register_blueprint(test_bp)

  
    auth.register()
    # Try accessing the protected route before logging in
    response = client.get('/protected')
    assert response.headers['Location'] == '/auth/login'

    # Test accessing the protected route after logging in
    auth.login()
    response = client.get('/protected')
    assert response.status_code == 200
    assert b'Protected' in response.data
import shutil
import os
import pytest
import sys 
from flask import session, Flask
from flask.testing import FlaskClient
from flask_wtf.csrf import generate_csrf
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from northwind import create_app, db
from northwind.db import get_db

TEST_DB = "test_northwind.sqlite"

@pytest.fixture(scope='function')
def app() -> Flask:
    shutil.copyfile('./northwind/northwind.sqlite', TEST_DB)

    app = create_app()
    app.config['DATABASE'] = TEST_DB
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing

    with app.app_context():
        db.init_db()
        yield app
    os.remove(TEST_DB)

@pytest.fixture(scope='function')
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app: Flask) -> 'FlaskCliRunner':
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client: FlaskClient) -> None:
        self._client = client

    def register(self, username: str = 'testtestingauth', password: str = 'testtestingauth', next: str = '/') -> 'Response':
        return self._client.post(
            'auth/register',
            data={'user_id': username, 'password': password, 'next': next}
        )

    def login(self, username: str = 'testtestingauth', password: str = 'testtestingauth', next: str = '/') -> 'Response':
        return self._client.post(
            'auth/login',
            data={'user_id': username, 'password': password, 'next': next}
        )

    def logout(self) -> 'Response':
        return self._client.get('auth/logout')


class SearchActions(object):
    def __init__(self, app: Flask) -> None:
        self._app = app

    def insert_supplier(self, company_name: str = 'TestSupplier') -> int:
        with self._app.app_context():
            db = get_db()
            db.execute("INSERT INTO Supplier (CompanyName) VALUES (?)", (company_name,))
            db.commit()
            return db.execute("SELECT Id FROM Supplier WHERE CompanyName = ?", (company_name,)).fetchone()[0]

    def insert_category(self, category_name: str = 'TestCategory') -> int:
        with self._app.app_context():
            db = get_db()
            db.execute("INSERT INTO Category (CategoryName) VALUES (?)", (category_name,))
            db.commit()
            return db.execute("SELECT Id FROM Category WHERE CategoryName = ?", (category_name,)).fetchone()[0]

    def insert_product(self, 
                       product_name: str = 'TestProduct', 
                       unit_price: float = 10.0, 
                       category_id: int = 1, 
                       supplier_id: int = 1, 
                       discontinued: int = 0, 
                       units_in_stock: int = 999, 
                       units_on_order: int = 999, 
                       reorder_level: int = 999) -> int:
        with self._app.app_context():
            db = get_db()
            db.execute("INSERT INTO Product (ProductName, UnitPrice, CategoryId, SupplierId, UnitsInStock, UnitsOnOrder, ReorderLevel, Discontinued) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (product_name, unit_price, category_id, supplier_id, units_in_stock, units_on_order, reorder_level, discontinued))
            db.commit()
            return db.execute("SELECT Id FROM Product WHERE ProductName = ?", (product_name,)).fetchone()[0]


class CartActions(object):
    def __init__(self, app: Flask) -> None:
        self._app = app

    def insert_shopping_cart(self, user_id: Optional[int] = None, session_id: str = "testtesttesttesttesttesttesttest") -> int:
        with self._app.app_context():
            db = get_db()
            if user_id is not None:
                db.execute("INSERT INTO Shopping_Cart (UserID, SessionID) VALUES (?, ?)", (user_id, session_id))
            else:
                db.execute("INSERT INTO Shopping_Cart (SessionID) VALUES (?)", (session_id,))
            db.commit()
            if user_id is not None:
                return db.execute("SELECT CartID FROM Shopping_Cart WHERE UserID = ?", (user_id,)).fetchone()[0]
            else:
                return db.execute("SELECT CartID FROM Shopping_Cart WHERE SessionID = ?", (session_id,)).fetchone()[0]

    def insert_cart_items(self, cart_id: int, product_id: int, quantity: int) -> None:
        with self._app.app_context():
            db = get_db()
            db.execute("INSERT INTO Cart_Items (CartID, ProductID, Quantity) VALUES (?, ?, ?)", (cart_id, product_id, quantity))
            db.commit()
     

@pytest.fixture(scope='function')
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)


@pytest.fixture
def search(app: Flask) -> SearchActions:
    return SearchActions(app)


@pytest.fixture
def cart(app: Flask) -> CartActions:
    return CartActions(app)
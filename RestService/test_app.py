import random
import string
import uuid
from datetime import datetime

import pytest
from flask import json
from hamcrest import *

from book_type import BookType
from books_rest_service import books as rest_service_books, books_app

MANIPULATION_PATH = "/v1/books/manipulation"
LATEST_PATH = "/v1/books/latest"
INFO_PATH = "/v1/books/info"
IDS_PATH = "/v1/books/ids"


def get_random_name(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def get_uuid():
    return str(uuid.uuid4())


@pytest.fixture()
def get_book():
    def _get_book(book_id=get_uuid(),
                  book_title=get_random_name(8),
                  book_type="Satire",
                  creation_date=datetime.now().strftime("%Y-%m-%d")):
        return {"ID": book_id,
                "Title": book_title,
                "Type": book_type,
                "Creation date": creation_date
                }

    return _get_book


@pytest.fixture(scope="function")
def client(request):
    books_app.config['TESTING'] = True
    client = books_app.test_client()

    yield client


@pytest.fixture
def book(get_book):
    return get_book()


# /v1/books/manipulation POST - Add book with no arguments but request payload as json contains fields  (type, title, creation date)
# /v1/books/manipulation DELETE - Delete book with arguments (id)
# /v1/books/manipulation PUT - Change the name of the book with arguments (id) (NOTE: updated time should be changed as well)
# /v1/books/manipulation GET - Returns “No implementation for `GET` method”
# /v1/books/latest GET - Get all the latest added books limited by some amount with arguments (limit)
# /v1/books/info GET - Get info(type, name etc …) about a book with arguments (ID)
# /v1/books/ids GET - Get all ID of books by title with arguments (title)

class TestBooksRestService:

    def teardown_method(self):
        rest_service_books.clear()

    def test_get_manipulation_returns_405(self, client):
        resp = client.get(MANIPULATION_PATH)

        assert_that(resp.status_code, is_(405))
        assert_that(str(resp.data), contains_string("No implementation for `GET` method."))

    def test_post_manipulation_when_creates_book_returns_201(self, client, book):
        resp = client.post(MANIPULATION_PATH, json=book)

        assert_that(resp.status_code, is_(201))
        assert_that(str(resp.data), contains_string("Book with id: {} is created.".format(book["ID"])))

    def test_post_manipulation_when_duplicate_returns_400(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        resp = client.post(MANIPULATION_PATH, json=book)

        assert_that(resp.status_code, is_(400))
        assert_that(str(resp.data), contains_string("Book with id: {} is already created.".format(book["ID"])))

    def test_put_manipulation_when_updates_returns_200(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        resp = client.put(MANIPULATION_PATH + "?uuid4={}&name={}".format(book["ID"], "Alice"))

        assert_that(resp.status_code, is_(200))
        assert_that(str(resp.data), contains_string("Book with id: {} has new name: {}.".format(book["ID"], "Alice")))

    def test_put_manipulation_when_book_is_absent_returns_404(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        new_uuid = get_uuid()
        resp = client.put(MANIPULATION_PATH + "?uuid4={}&name={}".format(new_uuid, "Alice"))

        assert_that(resp.status_code, is_(404))
        assert_that(str(resp.data), contains_string("Book with id: {} is not found.".format(new_uuid)))

    def test_delete_manipulation_when_deletes_returns_200(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        resp = client.delete(MANIPULATION_PATH + "?uuid4={}".format(book["ID"]))

        assert_that(resp.status_code, is_(200))
        assert_that(str(resp.data), contains_string("Book with id: {} is deleted.".format(book["ID"])))

    def test_delete_manipulation_when_book_is_absent_returns_404(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        new_uuid = get_uuid()
        resp = client.delete(MANIPULATION_PATH + "?uuid4={}".format(new_uuid))

        assert_that(resp.status_code, is_(404))
        assert_that(str(resp.data), contains_string("Book with id: {} is not found.".format(new_uuid)))

    def test_get_ids_when_ok_returns_200(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        resp = client.get(IDS_PATH + "?title={}".format(book["Title"]))

        assert_that(resp.status_code, is_(200))
        assert_that(json.loads(resp.data), contains(book["ID"]))

    def test_get_ids_when_books_are_absent_returns_200(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        resp = client.get(IDS_PATH + "?title={}".format(get_random_name(8)))

        assert_that(resp.status_code, is_(200))
        assert_that(json.loads(resp.data), empty())

    def test_get_latest_when_ok_returns_200(self, client, get_book):
        for i in range(10):
            client.post(MANIPULATION_PATH, json=get_book(book_id=get_uuid()))
        resp = client.get(LATEST_PATH + "?amount={}".format(5))

        assert_that(resp.status_code, is_(200))
        assert_that(len(json.loads(resp.data)), is_(5))

    def test_get_latest_when_books_are_absent_returns_200(self, client):
        resp = client.get(LATEST_PATH + "?amount={}".format(5))

        assert_that(resp.status_code, is_(200))
        assert_that(len(json.loads(resp.data)), is_(0))

    def test_get_info_when_ok_returns_200(self, client, book):
        client.post(MANIPULATION_PATH, json=book)

        resp = client.get(INFO_PATH + "?uuid4={}".format(book["ID"]))

        assert_that(resp.status_code, is_(200))
        assert_that(json.loads(resp.data),
                    has_entries({"ID": book["ID"], "Title": book["Title"], "Type": book["Type"]}))

    def test_get_info_when_book_is_absent_returns_404(self, client, book):
        client.post(MANIPULATION_PATH, json=book)
        id_ = get_uuid()
        resp = client.get(INFO_PATH + "?uuid4={}".format(id_))

        assert_that(resp.status_code, is_(404))
        assert_that(str(resp.data), "Book with id: {} is not found.".format(id_))

    @pytest.mark.parametrize("book_type", [book_type.value for book_type in BookType])
    def test_post_manipulation_accepts_all_book_types(self, client, get_book, book_type):
        book = get_book(book_type=book_type)
        resp = client.post(MANIPULATION_PATH, json=book)

        assert_that(resp.status_code, is_(201))
        assert_that(str(resp.data), contains_string("Book with id: {} is created.".format(book["ID"])))

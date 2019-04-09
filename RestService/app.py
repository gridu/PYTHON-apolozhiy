import json
import logging

from flask import Flask
from flask import request
from flask import jsonify
from flask_restful import Api, reqparse
from book_type import BookType, BookEncoder
from datetime import datetime

#         /v1/books/manipulation POST - Add book with no arguments but request payload as json contains fields  (type, title, creation date)
#         /v1/books/manipulation DELETE - Delete book with arguments (id)
#         /v1/books/manipulation PUT - Change the name of the book with arguments (id) (NOTE: updated time should be changed as well)
#         /v1/books/manipulation GET - Returns “No implementation for `GET` method”
#         /v1/books/latest GET - Get all the latest added books limited by some amount with arguments (limit)
#         /v1/books/info GET - Get info(type, name etc …) about a book with arguments (ID)
#         /v1/books/ids GET - Get all ID of books by title with arguments (title)


books = []
app = Flask(__name__)
api = Api(app)


@app.route("/v1/books/latest", methods=['GET'])
def latest():
    logger.info("Method '{}' was called at endpoint: {}".format(request.method, request.path))
    amount = int(request.args.get('amount'))

    books.sort(key=lambda book: book["Creation date"], reverse=True)
    return json.dumps(books[:amount], cls=BookEncoder), 200


@app.route("/v1/books/info", methods=['GET'])
def info():
    logger.info("Method '{}' was called at endpoint: {}".format(request.method, request.path))
    uuid4 = request.args.get('uuid4')

    try:
        return json.dumps(next(filter(lambda book: book["ID"] == uuid4, books)), cls=BookEncoder), 200
    except StopIteration:
        logger.warning("Book with id: {} is not found.".format(uuid4))
        return "Book with id: {} is not found.".format(uuid4), 404


@app.route("/v1/books/ids", methods=['GET'])
def ids():
    logger.info("Method '{}' was called at endpoint: {}".format(request.method, request.path))
    title = request.args.get('title')

    return jsonify(
        list(
            map(lambda book: book["ID"],
                filter(lambda book: title in book["Title"], books)))) \
        , 200


@app.route("/v1/books/manipulation", methods=['GET'])
def get():
    logger.warning("Method 'GET' is not allowed for endpoint: {}".format(request.path))
    return "No implementation for `GET` method.", 405


@app.route("/v1/books/manipulation", methods=['POST'])
def post():
    logger.info("Method '{}' was called at endpoint: {}".format(request.method, request.path))
    parser = reqparse.RequestParser()
    parser.add_argument("ID")
    parser.add_argument("Title")
    parser.add_argument("Type")
    parser.add_argument("Creation date")
    args = parser.parse_args()

    for book in books:
        if args["ID"] == book["ID"]:
            logger.warning("Book with id: {} is already created.".format(args["ID"]))
            return "Book with id: {} is already created.".format(args["ID"]), 400

    book = {
        "ID": args["ID"].strip(),
        "Title": args["Title"].strip(),
        "Type": BookType(args["Type"]),
        "Creation date": datetime.strptime(args["Creation date"], "%Y-%m-%d"),
        "Updated datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    books.append(book)

    logger.info("Book with id: {} is created.".format(args["ID"]))
    return "Book with id: {} is created.".format(args["ID"]), 201


@app.route("/v1/books/manipulation", methods=['PUT'])
def put():
    logger.info("Method '{}' was called at endpoint: {}".format(request.method, request.path))
    uuid4 = request.args.get('uuid4')
    name = request.args.get('name')

    try:
        updated_book = next(filter(lambda book: book["ID"] == uuid4, books))
        updated_book["Title"] = name
        updated_book["Updated datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Book with id: {} has new name: {}.".format(uuid4, name))
        return "Book with id: {} has new name: {}.".format(uuid4, name), 200
    except StopIteration:
        logger.warning("Book with id: {} is not found.".format(uuid4))
        return "Book with id: {} is not found.".format(uuid4), 404


@app.route("/v1/books/manipulation", methods=['DELETE'])
def delete():
    logger.info("Method '{}' was called at endpoint: {}".format(request.method, request.path))
    uuid4 = request.args.get('uuid4')

    try:
        books.remove(next(filter(lambda book: book["ID"] == uuid4, books)))
        logger.info("Book with id: {} is deleted.".format(uuid4))
        return "Book with id: {} is deleted.".format(uuid4), 200
    except StopIteration:
        logger.warning("Book with id: {} is not found.".format(uuid4))
        return "Book with id: {} is not found.".format(uuid4), 204


def define_logger():
    global logger
    logger = logging.getLogger("BookManipulationService")
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


if __name__ == '__main__':
    define_logger()
    app.run(debug=True)

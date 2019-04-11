import random
import string
from datetime import datetime, timedelta

from mysql.connector import (connection)


def get_random_name(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

config = {"user": "root",
          "password": "my-secret-pw",
          "host": "127.0.0.1",
          "port": "3306",
          "database": "mysql"}

cnx = connection.MySQLConnection(**config)
cursor = cnx.cursor()

delete_data = "delete from test_data"
cursor.execute(delete_data)

add_data = ("insert into test_data"
            "(date, title, author)"
            "values (%s, %s, %s)")

for i in range(50):
    date = datetime.now().date() - timedelta(days=random.randint(0,999))
    title = get_random_name(10)
    author = get_random_name(30)
    cursor.execute(add_data, (date, title, author))

cnx.commit()

cursor.close()
cnx.close()

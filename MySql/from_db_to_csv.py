import csv

from mysql.connector import (connection)

config = {"user": "root",
          "password": "my-secret-pw",
          "host": "127.0.0.1",
          "port": "3306",
          "database": "mysql"}

cnx = connection.MySQLConnection(**config)
cursor = cnx.cursor()

query = "select date, title, author from test_data"
cursor.execute(query)

with open("data_from_table.csv", "w") as csvfile:
    data_writer = csv.writer(csvfile, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
    data_writer.writerow(['date', 'title', 'author'])
    for (date, title, author) in cursor:
        data_writer.writerow([date, title, author])

cursor.close()
cnx.close()

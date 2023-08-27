import mysql.connector

# ESTABLISH A CONNECTION WITH MYSQL
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
)

# PREPARE A CURSOR OBJECT
cursor = db.cursor()

# CREATE A DATABASE FOR PROJECT
cursor.execute('CREATE DATABASE importDB')

print("Database created successfully")

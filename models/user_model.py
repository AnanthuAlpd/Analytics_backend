from db import mysql

def find_user_by_email(email):
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()

def insert_user(username, email, password):
    with mysql.connection.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        mysql.connection.commit()
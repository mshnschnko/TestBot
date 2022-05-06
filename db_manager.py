import os
import psycopg2

# DATABASE_URL = URL
db_name = "DBNAME"

def con_to_db():
    connection = psycopg2.connect(user="USER",
                                      # пароль, который указали при установке PostgreSQL
                                      password="PASSWORD",
                                      host="HOST",
                                      port="5432",
                                      database=db_name)
    return connection

def create_table_users(connection):
    cursor = connection.cursor()
    check_query = f"SELECT * FROM pg_catalog.pg_tables WHERE tablename = 'users';"
    cursor.execute(check_query)
    connection.commit()
    res = cursor.fetchall()
    if (len(res) == 0):
        create_table_query = """CREATE TABLE users
                                (
                                    ID integer PRIMARY KEY,
                                    LINE CHARACTER VARYING(30),
                                    PROCESS_ID integer
                                );"""
        cursor.execute(create_table_query)
        connection.commit()
    else:
        check_query = f"SELECT * FROM users"
        cursor.execute(check_query)
        connection.commit()
        res = cursor.fetchall()
    cursor.close()

def add_active_user(connection, user_id, line, process_id, last_command):
    cursor = connection.cursor()
    add_user_query = f"INSERT INTO users (ID, LINE, PROCESS_ID, LAST_COMMAND) VALUES ({user_id}, '{line}', {process_id}, '{last_command}')"
    cursor.execute(add_user_query)
    connection.commit()

def delete_user(connection, user_id):
    cursor = connection.cursor()
    del_user_query = f"DELETE FROM users WHERE ID = {user_id}"
    cursor.execute(del_user_query)
    connection.commit()

def search_user(connection, user_id):
    cursor = connection.cursor()
    search_query = f"SELECT * FROM users WHERE ID = {user_id}"
    cursor.execute(search_query)
    connection.commit()
    res = cursor.fetchall()
    if (len(res) != 0):
        return res[0]
    else:
        return 0

def is_logged(connection, user_id):
    cursor = connection.cursor()
    query = f"SELECT LOG_IN FROM users WHERE ID = {user_id}"
    cursor.execute(query)
    connection.commit()
    res = cursor.fetchall()
    return (res[0])[0]

def update_log_in(connection, user_id, status):
    cursor = connection.cursor()
    update_query = f"UPDATE users SET LOG_IN = '{status}' WHERE ID = {user_id}"
    cursor.execute(update_query)
    connection.commit()

def is_tried_to_log(connection, user_id):
    cursor = connection.cursor()
    query = f"SELECT TRIED_TO_LOG FROM users WHERE ID = {user_id}"
    cursor.execute(query)
    connection.commit()
    res = cursor.fetchall()
    return (res[0])[0]

def update_tried_to_log(connection, user_id, status):
    cursor = connection.cursor()
    update_query = f"UPDATE users SET TRIED_TO_LOG = '{status}' WHERE ID = {user_id}"
    cursor.execute(update_query)
    connection.commit()

def clear_table_users(connection):
    cursor = connection.cursor()
    query = f"DELETE FROM users WHERE ID > 1"
    cursor.execute(query)
    connection.commit()

def update_status(connection, user_id, line, process_id, last_command):
    cursor = connection.cursor()
    update_query = f"UPDATE users SET LINE = '{line}', PROCESS_ID = {process_id}, LAST_COMMAND = '{last_command}' WHERE ID = {user_id}"
    cursor.execute(update_query)
    connection.commit()

def add_column_to_users(connection):
    cursor = connection.cursor()
    query = "ALTER TABLE users ADD LAST_COMMAND CHARACTER VARYING(30);"
    cursor.execute(query)
    connection.commit()
    print('added')

def select_efficiency(connection, line):
    cursor = connection.cursor()
    if (line != 'Обе линии'):
        query = f"SELECT * FROM lines WHERE line_desc = '{line}';"
    else:
        query = f"SELECT * FROM lines WHERE line_desc = 'HANKY' OR line_desc = 'FACIAL';"
    cursor.execute(query)
    connection.commit
    res = cursor.fetchall()
    # print(res)
    if (len(res) != 0):
        return res
    else:
        return 0
import os
import psycopg2

# DATABASE_URL = os.environ['DBURL']
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
    # print('pizda')
    check_query = f"SELECT * FROM pg_catalog.pg_tables WHERE tablename = 'users';"
    cursor.execute(check_query)
    connection.commit()
    res = cursor.fetchall()
    # print('NEpizda')
    if (len(res) == 0):
        create_table_query = """CREATE TABLE users
                                (
                                    ID integer PRIMARY KEY,
                                    REGION CHARACTER VARYING(30),
                                    PROCESS_ID integer
                                );"""
        cursor.execute(create_table_query)
        connection.commit()
    else:
        check_query = f"SELECT * FROM users"
        cursor.execute(check_query)
        connection.commit()
        res = cursor.fetchall()
        # print(res)
    cursor.close()

def add_active_user(connection, user_id, region, process_id):
    cursor = connection.cursor()
    add_user_query = f"INSERT INTO users (ID, REGION, PROCESS_ID) VALUES ({user_id}, '{region}', {process_id})"
    cursor.execute(add_user_query)
    connection.commit()

def delete_user(connection, user_id):
    # print('bef del')
    cursor = connection.cursor()
    del_user_query = f"DELETE FROM users WHERE ID = {user_id}"
    cursor.execute(del_user_query)
    connection.commit()
    # print('af del')

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

def clear_table():
    conn = con_to_db()
    cursor = conn.cursor()
    query = f"DELETE FROM users WHERE ID > 1"
    cursor.execute(query)
    conn.commit()

def update_status(user_id, last_command):
    conn = con_to_db()
    cursor = conn.cursor()
    update_query = f"UPDATE users SET LAST_COMMAND = '{last_command}' WHERE ID = {user_id}"
    cursor.execute(update_query)
    conn.commit()

def add_column():
    conn = con_to_db()
    cursor = conn.cursor()
    query = "ALTER TABLE users ADD LAST_COMMAND CHARACTER VARYING(30);"
    cursor.execute(query)
    conn.commit()
    print('added')
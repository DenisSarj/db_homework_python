import psycopg2

import time

time.sleep(2)
connect = psycopg2.connect(database='my_db', user='DenisSarj', password='30125916', port=5433)
with connect.cursor() as curs:
    def create_table(cursor):
        curs.execute('DROP TABLE telephone_numbers_users;')
        curs.execute('DROP TABLE telephone_numbers;')
        curs.execute('DROP TABLE users;')

        curs.execute(
            "CREATE TABLE users (user_id SERIAL PRIMARY KEY, mail VARCHAR(60) NOT NULL UNIQUE, name VARCHAR(60) NOT NULL, last_name  VARCHAR(60) NOT NULL);")
        curs.execute(
            'CREATE TABLE telephone_numbers (number_id SERIAL PRIMARY KEY, number VARCHAR(60) NOT NULL UNIQUE);')
        curs.execute(
            'CREATE TABLE telephone_numbers_users (user_id int, number_id int, FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE, FOREIGN KEY (number_id) REFERENCES telephone_numbers (number_id) ON DELETE CASCADE, CONSTRAINT pk PRIMARY KEY (user_id, number_id));')
        connect.commit()


    def add_client(u_name: str, last_name: str, email: str, cursor, number=''):
        cursor.execute('''INSERT INTO users (name, last_name, mail) VALUES
            (%s, %s, %s);''', (u_name, last_name, email))
        cursor.execute('''INSERT INTO telephone_numbers (number) VALUES
                    (%s);''', (number,))
        connect.commit()
        cursor.execute('''SELECT user_id FROM users WHERE mail = %s''', (email,))
        user_id = int(str(curs.fetchone()).replace('(', '').replace(',)', ''))
        cursor.execute('''SELECT number_id FROM telephone_numbers WHERE number = %s''', (number,))
        number_id = int(str(curs.fetchone()).replace('(', '').replace(',)', ''))
        cursor.execute('''INSERT INTO telephone_numbers_users (user_id, number_id) VALUES
                            (%s, %s);''', (user_id, number_id))
        connect.commit()


    def add_number_to_exist_client(client_id: int, number: str, cursor):
        cursor.execute('''UPDATE telephone_numbers SET number = %s
                          WHERE number_id in (SELECT number_id FROM telephone_numbers_users WHERE user_id = %s);''',
                       (number, client_id))
        connect.commit()


    def update_users(user_id, cursor, u_name: str = None, last_name: str = None, email: str = None, number=''):
        if u_name is not None:
            cursor.execute('''UPDATE users SET name = %s
                              WHERE user_id = %s;''', (u_name, user_id))
        if last_name is not None:
            cursor.execute('''UPDATE users SET last_name = %s
                              WHERE user_id = %s;''', (last_name, user_id))
        if email is not None:
            cursor.execute('''UPDATE users SET mail = %s
                              WHERE user_id = %s;''', (email, user_id))
        if number != '':
            cursor.execute('''UPDATE telephone_numbers SET number = %s
                              WHERE number_id in (SELECT number_id FROM telephone_numbers_users WHERE user_id = %s);''',
                           (number, user_id))
        connect.commit()


    def delete_number(user_id: int, number: str, cursor):
        cursor.execute('''SELECT user_id FROM users
                       WHERE user_id = %s;''', (user_id,))
        id = cursor.fetchone()
        if id is not None:
            cursor.execute('''DELETE FROM telephone_numbers_users
                           WHERE number_id in (SELECT number_id FROM telephone_numbers_users WHERE user_id = %s);''',
                           (user_id,))
            cursor.execute('''DELETE FROM telephone_numbers
                                       WHERE number = %s;''', (number,))
            connect.commit()
        else:
            print(f'Пользователя с id {user_id} не существует!')


    def delete_user(user_id: int, cursor):
        cursor.execute('''SELECT user_id FROM users
                       WHERE user_id = %s;''', (user_id,))
        id = cursor.fetchone()
        if id is not None:
            cursor.execute(
                '''DELETE FROM telephone_numbers WHERE number_id in (SELECT number_id FROM telephone_numbers_users WHERE user_id = %s);''',
                (user_id,))
            cursor.execute('''DELETE FROM users WHERE user_id = %s''', (user_id,))
            connect.commit()
        else:
            print(f'Пользователя с id {user_id} не существует!')


    def find_client(cursor, email: str = None, name: str = None, last_name: str = None, number: str = None):
        if email is not None:
            cursor.execute('''SELECT user_id FROM users
                           WHERE mail = %s;''', (email,))
            e = cursor.fetchone()
            if e is not None:
                cursor.execute('''SELECT users.user_id, name, last_name, mail, number 
                                  FROM users
                                  LEFT JOIN telephone_numbers_users ON users.user_id = telephone_numbers_users.user_id
                                  LEFT JOIN telephone_numbers ON telephone_numbers_users.number_id = telephone_numbers.number_id
                                  WHERE mail = %s;''', (email,))
                response = cursor.fetchall()
                return response
            else:
                return 'Пользователь не найден'

        if name is not None:
            cursor.execute('''SELECT user_id FROM users
                           WHERE name = %s;''', (name,))
            e = cursor.fetchone()
            if e is not None:
                cursor.execute('''SELECT users.user_id, name, last_name, mail, number 
                                  FROM users
                                  LEFT JOIN telephone_numbers_users ON users.user_id = telephone_numbers_users.user_id
                                  LEFT JOIN telephone_numbers ON telephone_numbers_users.number_id = telephone_numbers.number_id
                                  WHERE name = %s;''', (name,))
                response = cursor.fetchall()
                return response
            else:
                return 'Пользователь не найден'

        if last_name is not None:
            cursor.execute('''SELECT user_id FROM users
                           WHERE last_name = %s;''', (last_name,))
            e = cursor.fetchone()
            if e is not None:
                cursor.execute('''SELECT users.user_id, name, last_name, mail, number 
                                  FROM users
                                  LEFT JOIN telephone_numbers_users ON users.user_id = telephone_numbers_users.user_id
                                  LEFT JOIN telephone_numbers ON telephone_numbers_users.number_id = telephone_numbers.number_id
                                  WHERE last_name = %s;''', (last_name,))
                response = cursor.fetchall()
                return response
            else:
                return 'Пользователь не найден'

        if number is not None:
            cursor.execute('''SELECT number_id FROM telephone_numbers
                              WHERE number = %s;''', (number,))
            e = cursor.fetchone()
            if e is not None:
                cursor.execute('''SELECT users.user_id, name, last_name, mail, number 
                                  FROM users
                                  LEFT JOIN telephone_numbers_users ON users.user_id = telephone_numbers_users.user_id
                                  LEFT JOIN telephone_numbers ON telephone_numbers_users.number_id = telephone_numbers.number_id
                                  WHERE telephone_numbers.number_id in (SELECT number_id 
                                  FROM telephone_numbers_users 
                                  WHERE number = %s);''', (number,))
                response = cursor.fetchone()
                return response
            else:
                return 'Пользователь не найден'


    print(find_client(curs, number='8918146691'))
connect.close()

import psycopg2
from pprint import pprint


def client_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id SERIAL PRIMARY KEY,
        name VARCHAR(20),
        lastname VARCHAR(30),
        email VARCHAR(254)
        );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonenumbers(
        number VARCHAR(11) PRIMARY KEY,
        client_id INTEGER REFERENCES clients(id)
        );
    """)
    return


def delete_db(cur):
    cur.execute("""
        DROP TABLE clients, phonenumbers CASCADE;
        """)


def insert_tel(cur, client_id, tel):
    cur.execute("""
        INSERT INTO phonenumbers(number, client_id)
        VALUES (%s, %s)
        """, (tel, client_id))
    return client_id


def insert_client(cur, name=None, surname=None, email=None, tel=None):
    cur.execute("""
        INSERT INTO clients(name, lastname, email)
        VALUES (%s, %s, %s)
        """, (name, surname, email))
    cur.execute("""
        SELECT id from clients
        ORDER BY id DESC
        LIMIT 1
        """)
    id = cur.fetchone()[0]
    if tel is None:
        return id
    else:
        insert_tel(cur, id, tel)
        return id


def update_client(cur, id, name=None, surname=None, email=None):
    cur.execute("""
        SELECT * from clients
        WHERE id = %s
        """, (id, ))
    info = cur.fetchone()
    if name is None:
        name = info[1]
    if surname is None:
        surname = info[2]
    if email is None:
        email = info[3]
    cur.execute("""
        UPDATE clients
        SET name = %s, lastname = %s, email =%s 
        where id = %s
        """, (name, surname, email, id))
    return id


def delete_phone(cur, number):
    cur.execute("""
        DELETE FROM phonenumbers 
        WHERE number = %s
        """, (number, ))
    return number


def delete_client(cur, id):
    cur.execute("""
        DELETE FROM phonenumbers
        WHERE client_id = %s
        """, (id, ))
    cur.execute("""
        DELETE FROM clients 
        WHERE id = %s
       """, (id,))
    return id


def find_client(cur, name=None, surname=None, email=None, tel=None):
    if name is None:
        name = '%'
    else:
        name = '%' + name + '%'
    if surname is None:
        surname = '%'
    else:
        surname = '%' + surname + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if tel is None:
        cur.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
            LEFT JOIN phonenumbers p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.lastname LIKE %s
            AND c.email LIKE %s
            """, (name, surname, email))
    else:
        cur.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
            LEFT JOIN phonenumbers p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.lastname LIKE %s
            AND c.email LIKE %s AND p.number like %s
            """, (name, surname, email, tel))
    return cur.fetchall()


if __name__ == '__main__':
    with psycopg2.connect(database="1", user="postgres",
                          password="12345678") as conn:
        with conn.cursor() as curs:
            delete_db(curs)
            client_db(curs)
            print("Добавлен клиент id: ",
                  insert_client(curs, "Вася", "Пупкин", "Pupkin@gmail.com", 88001001010))
            print("Добавлен клиент id: ",
                  insert_client(curs, "Иван", "Иванов", "Ivanov@gmail.com", 89218008080))
            print("Добавлен клиент id: ",
                  insert_client(curs, "Петр", "Петров", "Petrov@gmail.com", 89113202020))
            print("Добавлен клиент id: ", insert_client(curs, "Васильев", "Василий", "Vasilev@gmail.com"))
            print("Добавлена клиент id: ", insert_client(curs, "Брэд", "Питт", "Pitt@gmail.com"))
            curs.execute("""
                SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                ORDER by c.id
                """)
            pprint(curs.fetchall())
            
            print("Телефон добавлен клиенту id: ", insert_tel(curs, 2, 89213333333))
            print("Телефон добавлен клиенту id: ", insert_tel(curs, 1, 88004004040))
           
            curs.execute("""
                SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                ORDER by c.id
                """)
            pprint(curs.fetchall())
            print("Изменены данные клиента id: ", update_client(curs, 4, "Джони", None, 'JD@gmail.com'))
            print("Телефон удалён c номером: ", delete_phone(curs, '79621994802'))
            
            curs.execute("""
                SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                ORDER by c.id
                """)
            pprint(curs.fetchall())
            
            print("Клиент удалён с id: ", delete_client(curs, 2))
            curs.execute("""
                            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
                            LEFT JOIN phonenumbers p ON c.id = p.client_id
                            ORDER by c.id
                            """)
            pprint(curs.fetchall())
           
            print('Найденный клиент по имени:')
            pprint(find_client(curs, "Брэд"))

            print('Найденный клиент по email:')
            pprint(find_client(curs, None, None, "Pitt@gmail.com"))

            print('Найденный клиент по имени, фамилии и email:')
            pprint(find_client(curs, "Вася", "Пупкин", "Pupkin@gmail.com"))

            print('Найденный клиент по имени, фамилии, телефону и email:')
            pprint(find_client(curs,  "Иван", "Иванов", "Ivanov@gmail.com", '89218008080'))

            print('Найденный клиент по имени, фамилии, телефону:')
            pprint(find_client(curs, None, None, None, '89113202020'))
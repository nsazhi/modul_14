import sqlite3

connection = sqlite3.connect('not_telegram.db')
cursor = connection.cursor()


def initiate_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INT PRIMARY KEY,
    username NEXT NOT NULL,
    email TEXT NOT NULL,
    age INT NOT NULL,
    balance INT NOT NULL
    )
    ''')


def add_product(id, title, description, price):
    check_product = cursor.execute("SELECT * FROM Products WHERE id = ?", (id,))
    if check_product.fetchone() is None:
        cursor.execute(f'''
        INSERT INTO Products VALUES('{id}', '{title}', '{description}', '{price}')
''')
        connection.commit()


def get_all_products():
    cursor.execute("SELECT * FROM Products")
    connection.commit()
    return cursor.fetchall()


def add_user(username, email, age):
    cursor.execute("INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)",
                   (username, email, age, 1000))
    connection.commit()


def is_included(username):
    isincluded = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    connection.commit()
    if isincluded.fetchone() is None:
        return False
    else:
        return True

# connection.commit()
# connection.close()

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


def add_product(id, title, description, price):
    check_product = cursor.execute("SELECT * FROM Products WHERE id = ?", (id,))
    if check_product.fetchone() is None:
        cursor.execute(f'''
        INSERT INTO Products VALUES('{id}', '{title}', '{description}', '{price}')
''')
        connection.commit()


def get_all_products():
    cursor.execute("SELECT * FROM Products")
    return cursor.fetchall()

# initiate_db()

# for i in range(4):
#     i +=1
#     add_product(i, f'Продукт {i}', f'Описание {i}', i * 100)

# connection.commit()
# connection.close()

import psycopg2

# Подключение к PostgreSQL с правами администратора
connection = psycopg2.connect(
    dbname="postgres",  # Сначала подключаемся к базе postgres
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

connection.autocommit = True  # Устанавливаем автокоммит для создания базы данных
cursor = connection.cursor()

# Создание новой базы данных
try:
    cursor.execute("CREATE DATABASE test_db;")
    print("База данных test_db успешно создана.")
except psycopg2.errors.DuplicateDatabase:
    print("База данных test_db уже существует.")

# Закрытие соединения с админской базой
cursor.close()
connection.close()

# Подключение к новой базе данных
connection = psycopg2.connect(
    dbname="test_db",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cursor = connection.cursor()

# Создание таблицы customers
create_customers_table = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);
"""
cursor.execute(create_customers_table)

# Создание таблицы orders
create_orders_table = """
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product VARCHAR(50)
);
"""
cursor.execute(create_orders_table)

# Добавление данных в таблицу customers
insert_customers = """
INSERT INTO customers (customer_id, name) VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie')
ON CONFLICT (customer_id) DO NOTHING;
"""
cursor.execute(insert_customers)

# Добавление данных в таблицу orders (без заказа с customer_id=4)
insert_orders = """
INSERT INTO orders (order_id, customer_id, product) VALUES
(101, 1, 'Laptop'),
(102, 2, 'Tablet'),
(103, 1, 'Monitor')
ON CONFLICT (order_id) DO NOTHING;
"""
cursor.execute(insert_orders)

# Фиксация изменений
connection.commit()

print("Таблицы созданы, и данные добавлены.")

print("Table customers:")
cursor.execute("SELECT * FROM customers;")
customers = cursor.fetchall()
for row in customers:
    print(row)

print("Table orders:")
cursor.execute("SELECT * FROM orders;")
orders = cursor.fetchall()
for row in orders:
    print(row)

# LEFT JOIN
print("\n LEFT JOIN (все клиенты и заказы если есть):")
cursor.execute("""
    SELECT customers.name, orders.product
    FROM customers
    LEFT JOIN orders ON customers.customer_id = orders.customer_id;
""")
left_join_result = cursor.fetchall()
for row in left_join_result:
    print(row)

# RIGHT JOIN
print("\n RIGHT JOIN (все клиенты и заказы если есть):")
cursor.execute("""
    SELECT customers.name, orders.product
    FROM customers
    RIGHT JOIN orders ON customers.customer_id = orders.customer_id;
""")
right_join_result = cursor.fetchall()
for row in right_join_result:
    print(row)

# FULL JOIN
print("\n FULL JOIN (все клиенты и заказы если есть):")
cursor.execute("""
    SELECT customers.name, orders.product
    FROM customers
    FULL JOIN orders ON customers.customer_id = orders.customer_id;
""")
full_join_result = cursor.fetchall()
for row in full_join_result:
    print(row)

# CROSS JOIN
print("\n CROSS JOIN (все клиенты и заказы если есть):")
cursor.execute("""
    SELECT customers.name, orders.product
    FROM customers
    CROSS JOIN orders;
""")
cross_join_result = cursor.fetchall()
for row in cross_join_result:
    print(row)

# Закрытие соединения
cursor.close()
connection.close()

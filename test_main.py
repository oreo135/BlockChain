from sqlalchemy import create_engine, text

# Параметры подключения
DB_USER = "my_database_user"
DB_PASS = "my_database_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "blockchain_db"

# Создаём строку подключения
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Проверяем подключение
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Connected to the database!")
        # Проверяем наличие схем и таблиц
        result = connection.execute(text("SELECT schema_name FROM information_schema.schemata"))
        print("Schemas:", [row[0] for row in result])
        result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        print("Tables in 'public':", [row[0] for row in result])
except Exception as e:
    print(f"Database connection failed: {e}")

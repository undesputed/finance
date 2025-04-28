import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from mysql.connector import Error
from mysql import connector
from app.schemas import SCHEMA_SQL

def create_mysql_connection():
    """
    Create and return a MySQL database connection.
    Returns:
        connection (mysql.connector.connection.MySQLConnection): MySQL connection object or None if failed.
    """
    try:
        connection = connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print('Connected to MySQL database')
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

def initialize_schema():
    """
    Create the finance schema with required tables if they do not exist.
    """
    conn = create_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for statement in SCHEMA_SQL.strip().split(';'):
                if statement.strip():
                    cursor.execute(statement)
            conn.commit()
            print('Database schema initialized.')
        except Exception as e:
            print(f"Error initializing schema: {e}")
        finally:
            cursor.close()
            conn.close()
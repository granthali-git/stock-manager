import os
import sqlite3
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load env variables
load_dotenv()

SQLITE_DB = 'stock_manager.db'
POSTGRES_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/stock_manager')

def migrate():
    print("Starting database migration from SQLite to PostgreSQL...")
    
    # 1. Initialize PostgreSQL database tables first via Flask application
    from app import app, init_db
    print("Initializing PostgreSQL tables schema...")
    try:
        init_db()
        print("PostgreSQL tables checked/created.")
    except Exception as e:
        print("Failed to run schema initialization. Make sure your PostgreSQL server is online.")
        print(f"Error: {e}")
        return

    # 2. Establish connections
    if not os.path.exists(SQLITE_DB):
        print(f"Error: Local SQLite file '{SQLITE_DB}' was not found. Nothing to migrate.")
        return

    lite_conn = sqlite3.connect(SQLITE_DB)
    lite_conn.row_factory = sqlite3.Row
    lite_cursor = lite_conn.cursor()

    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_conn.autocommit = True
    pg_cursor = pg_conn.cursor()

    tables = [
        ('users', ['id', 'username', 'password', 'role']),
        ('warehouses', ['id', 'name', 'location', 'manager_name']),
        ('products', ['id', 'name', 'category', 'quantity', 'price', 'image', 'min_stock_threshold', 'expiry_date', 'warehouse_id', 'barcode']),
        ('stock_movements', ['id', 'product_id', 'movement_type', 'quantity', 'note', 'user_id', 'created_at', 'warehouse_id']),
        ('suppliers', ['id', 'name', 'contact_number', 'email', 'address']),
        ('purchase_orders', ['id', 'supplier_id', 'product_id', 'quantity', 'order_date', 'payment_status', 'order_status']),
        ('invoices', ['id', 'product_id', 'quantity', 'unit_price', 'total_amount', 'customer_name', 'date', 'created_by']),
        ('settings', ['key', 'value'])
    ]

    for table, columns in tables:
        print(f"Migrating table '{table}'...")
        
        # Read from SQLite
        lite_cursor.execute(f"SELECT {', '.join(columns)} FROM {table}")
        rows = lite_cursor.fetchall()
        print(f"Found {len(rows)} rows to copy.")

        if not rows:
            continue

        # In PostgreSQL, clean up existing data first to prevent conflict errors if run multiple times
        pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")

        # Prepare insert query
        col_list = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

        # Convert rows to lists of values
        values_to_insert = []
        for row in rows:
            val_row = []
            for col in columns:
                val = row[col]
                # Convert empty string dates to None (Null) for PostgreSQL compatibility
                if col == 'expiry_date' and val == '':
                    val = None
                val_row.append(val)
            values_to_insert.append(val_row)

        # Batch insert into Postgres
        psycopg2.extras.execute_batch(pg_cursor, insert_query, values_to_insert)
        print(f"Successfully copied {len(values_to_insert)} rows to '{table}'.")

        # Update sequences for serial columns
        if table != 'settings':
            print(f"Updating sequence for table '{table}'...")
            seq_name = f"{table}_id_seq"
            pg_cursor.execute(f"SELECT setval('{seq_name}', (SELECT COALESCE(MAX(id), 0) FROM {table}) + 1, false)")

    # Close connections
    lite_cursor.close()
    lite_conn.close()
    pg_cursor.close()
    pg_conn.close()

    print("\nDatabase migration completed successfully!")

if __name__ == '__main__':
    migrate()

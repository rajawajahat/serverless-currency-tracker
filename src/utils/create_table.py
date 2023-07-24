import mysql.connector

# Database connection configuration
db_config = {
    "host": "mydb-rds.ci36p2p5xaob.us-east-1.rds.amazonaws.com",
    "user": "gauthier",
    "password": "kolweziYetu",
    "database": "kolwezidb",
}

# SQL query to create the currency table
create_table_query = """
CREATE TABLE currency (
    currency VARCHAR(10) PRIMARY KEY,
    today FLOAT,
    yesterday FLOAT,
    difference FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""


def create_currency_table():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Drop the previous table if it exists
        cursor.execute("DROP TABLE IF EXISTS currency")

        # Execute the create table query
        cursor.execute(create_table_query)

        # Commit the changes
        conn.commit()

        print("Currency table created successfully.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    create_currency_table()

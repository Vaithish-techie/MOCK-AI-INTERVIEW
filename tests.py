import psycopg2

# Database connection details
DB_HOST = "localhost"  # Example: 'localhost' or '127.0.0.1'
DB_PORT = "5432"  # Default PostgreSQL port: '5432'
DB_NAME = "interview_db"
DB_USER = "postgres"
DB_PASSWORD = "VaiSQL$$#"

try:
    # Establish the connection
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    # Create a cursor object
    cursor = connection.cursor()
    
    # Execute a simple query to check the connection
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    
    print("✅ Successfully connected to the database!")
    print("PostgreSQL version:", db_version)
    
    # Close the cursor and connection
    cursor.close()
    connection.close()

except Exception as e:
    print("❌ Database connection failed!")
    print("Error:", e)

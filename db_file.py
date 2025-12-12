import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        """MySQL DB credentials"""
        self.host = "mysql-convenientshop-conveniencestore01.b.aivencloud.com"
        self.user = "avnadmin"
        self.password = "SECRET"
        self.port = 24122
        self.database = "conv_shop_db"
        self.connection = None
        self.cursor = None
        
        # Try to connect and ensure the announcement table exists for demo purposes
        self.DB_Connection()
        self.create_announcement_table()

    def DB_Connection(self):
        """Creating the connection to MySQL"""
        try:
            # Establish a new connection
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connection to MySQL is successful.")
                self.cursor = self.connection.cursor(dictionary=True)  # Use dictionary cursor
            return self.connection

        except Error as e:
            print(f"Connection Failed to MySQL!: {e}")
            self.connection = None
            self.cursor = None
            return None

    def ensure_connection(self):
        """Ensure that the connection is still active, and reconnect if necessary."""
        if not self.connection or not self.connection.is_connected():
            print("Reconnecting to the database...")
            self.DB_Connection()
        
    def create_announcement_table(self):
        """Creates the announcement table if it doesn't exist."""
        self.ensure_connection()
        if not self.cursor: return
        
        # SQL to create the table based on your schema
        create_table_query = """
        CREATE TABLE IF NOT EXISTS announcement (
            annou_id INT AUTO_INCREMENT PRIMARY KEY,
            img_url VARCHAR(200),
            name VARCHAR(50),
            discount_price DECIMAL(10,2),
            discount_deadline DATE,
            product_id INT NULL, 
            status VARCHAR(30)
        );
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("Announcement table checked/created successfully.")
        except Error as e:
            print(f"Error creating table: {e}")

    def fetchall(self, query, params=None):
        """Fetch all rows from a query with optional parameters"""
        self.ensure_connection()  
        if not self.cursor:
            print("Error: Database cursor is not initialized. Connection likely failed.")
            return []  
            
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error executing fetchall query: {e}")
            return []
    
    def fetchone(self, query, params=None):
        """Fetch a single row from a query with optional parameters"""
        self.ensure_connection()  # Ensure connection is open
        if not self.cursor:
            print("Error: Database cursor is not initialized. Connection likely failed.")
            return None  
            
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f"Error executing fetchone query: {e}")
            return None

    def execute_commit(self, query, params=None):
        """Execute a query (INSERT, UPDATE, DELETE) and commit the changes."""
        self.ensure_connection()
        if not self.connection or not self.cursor:
            print("Error: Database connection/cursor is not initialized.")
            return False
            
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error executing and committing query: {e}")
            self.connection.rollback() # Rollback on error
            return False

    def close(self):
        """Close the database connection and cursor"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("MySQL connection closed")

# Create a global database instance
db = Database()
db.DB_Connection()
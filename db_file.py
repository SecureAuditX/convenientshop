import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        """MySQL DB credentials"""
        self.host = "localhost"
        self.user = "root"
        self.password = "zxcvbnm"
        self.port = 3306
        self.database = "convenient_shop"
        self.connection = None
        self.cursor = None

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
    
    
    def fetchall(self, query, params=None):
        #Fetch all rows from a query with optional parameters
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
            print(f"Error executing query: {e}")
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
            print(f"Error executing query: {e}")
            return None

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

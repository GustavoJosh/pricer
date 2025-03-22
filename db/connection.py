"""
Database connection management for the Sign Business application.
"""
import mysql.connector
from mysql.connector import Error
import tkinter.messagebox as messagebox
import os
from dotenv import load_dotenv
import sys


load_dotenv()

# Singleton pattern for database connection
class DatabaseConnection:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance
    
    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish a connection to the MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),  
                password=os.getenv("DB_PASSWORD"),  
                database=os.getenv("DB_NAME"),
                consume_results=True  # Auto-consume unread results
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                return True
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to MySQL database: {e}")
            print(f"Error connecting to database: {e}")
            return False
    
    def get_connection(self):
        """Get the database connection, reconnecting if necessary"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()
            return self.connection
        except Error as e:
            messagebox.showerror("Database Error", f"Error reconnecting to database: {e}")
            return None
    
    def execute_query(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        """Execute a query with optional parameters and return results"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            result = None
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                # Consume results explicitly
                while cursor.nextset():
                    pass  # Exhaust all result sets
            
            if commit:
                connection.commit()
                
            return result
        except Error as e:
            if commit:
                connection.rollback()
            messagebox.showerror("Database Error", f"Error executing query: {e}")
            print(f"Error executing query: {e}")
            return None
        finally:
            if cursor:
                # Make sure to exhaust any remaining result sets before closing the cursor
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass  # Ignore any errors during cleanup
                cursor.close()
    
    def close(self):
        """Close the database connection"""
        try:
            if self.connection:
                # Make sure we catch any connection errors during close
                try:
                    if self.connection.is_connected():
                        # Ensure all cursors are closed and results consumed
                        self.connection.cmd_reset_connection()
                        self.connection.close()
                        print("Database connection closed")
                except Error as e:
                    print(f"Error while closing connection: {e}")
        except Exception as e:
            print(f"Error closing database connection: {e}")
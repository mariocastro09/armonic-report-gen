import sqlite3
import pandas as pd
from typing import List, Optional
import streamlit as st

class DatabaseHandler:
    """Handle SQLite database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except sqlite3.Error as e:
            st.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_table_names(self) -> List[str]:
        """Get all table names from database"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            return tables
        except sqlite3.Error as e:
            st.error(f"Error fetching table names: {e}")
            return []
    
    def read_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """Read data from a specific table"""
        if not self.connection:
            return None
        
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{table_name}";', self.connection)
            return df
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            st.warning(f"Error reading table {table_name}: {e}")
            return None
    
    def get_table_info(self, table_name: str) -> dict:
        """Get information about a table"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f'PRAGMA table_info("{table_name}");')
            columns = cursor.fetchall()
            
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
            row_count = cursor.fetchone()[0]
            
            return {
                'columns': [col[1] for col in columns],
                'row_count': row_count,
                'column_info': columns
            }
        except sqlite3.Error as e:
            st.warning(f"Error getting table info for {table_name}: {e}")
            return {} 
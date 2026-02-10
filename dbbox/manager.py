"""Database manager for DBBox"""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional
from confbox import get_app_data_dir


class DBManager:
    """SQLite database manager using ConfBox for storage"""

    def __init__(self, db_name: str):
        """Initialize database manager

        Args:
            db_name: Name of the database (without .db extension)
        """
        # Use ConfBox to get the app data directory
        self.db_dir = get_app_data_dir("dbbox")
        self.db_path = self.db_dir / f"{db_name}.db"
        self.db_name = db_name
        self.conn = None

    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def list_tables(self) -> List[str]:
        """List all tables in the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

    def table_info(self, table: str) -> Optional[List[Tuple]]:
        """Get table schema information"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            return cursor.fetchall()
        except sqlite3.OperationalError:
            return None

    def create_table(self, table: str, schema: List[str]) -> bool:
        """Create table with schema

        Args:
            table: Table name
            schema: List of column definitions like ["id:INTEGER", "name:TEXT"]

        Returns:
            True if successful, False otherwise
        """
        # Parse schema
        columns = []
        for col_def in schema:
            if ':' not in col_def:
                raise ValueError(f"Invalid schema format '{col_def}'. Use 'column:TYPE'")

            col_name, col_type = col_def.split(':', 1)
            columns.append(f"{col_name} {col_type.upper()}")

        # Always add id as primary key if not specified
        if not any(c.lower().startswith('id ') for c in columns):
            columns.insert(0, "id INTEGER PRIMARY KEY AUTOINCREMENT")

        schema_sql = ", ".join(columns)
        cursor = self.conn.cursor()

        try:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({schema_sql})")
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Error creating table: {e}")

    def insert(self, table: str, values: List[str]) -> int:
        """Insert a row into the table

        Args:
            table: Table name
            values: List of values to insert

        Returns:
            The ID of the inserted row
        """
        # Get table info to determine number of columns (excluding id)
        info = self.table_info(table)
        if not info:
            raise ValueError(f"Table '{table}' does not exist. Create it first with --schema")

        # Get column names (excluding id which is auto-increment)
        columns = [col[1] for col in info if col[1] != 'id']

        if len(values) != len(columns):
            raise ValueError(f"Expected {len(columns)} values for columns {columns}, got {len(values)}")

        placeholders = ", ".join(["?" for _ in values])
        columns_str = ", ".join(columns)

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})", values)
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Error inserting row: {e}")

    def select(self, table: str, row_id: Optional[int] = None) -> List[sqlite3.Row]:
        """Select rows from the table

        Args:
            table: Table name
            row_id: Optional specific row ID to select

        Returns:
            List of rows
        """
        cursor = self.conn.cursor()

        try:
            if row_id is not None:
                cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
            else:
                cursor.execute(f"SELECT * FROM {table}")

            return cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error selecting rows: {e}")

    def update(self, table: str, row_id: int, values: List[str]) -> int:
        """Update a row in the table

        Args:
            table: Table name
            row_id: ID of row to update
            values: New values for the row

        Returns:
            Number of rows updated
        """
        # Get table info to determine column names
        info = self.table_info(table)
        if not info:
            raise ValueError(f"Table '{table}' does not exist")

        # Get column names (excluding id)
        columns = [col[1] for col in info if col[1] != 'id']

        if len(values) != len(columns):
            raise ValueError(f"Expected {len(columns)} values for columns {columns}, got {len(values)}")

        set_clause = ", ".join([f"{col} = ?" for col in columns])

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values + [row_id])
            self.conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            raise RuntimeError(f"Error updating row: {e}")

    def delete(self, table: str, row_id: int) -> int:
        """Delete a row from the table

        Args:
            table: Table name
            row_id: ID of row to delete

        Returns:
            Number of rows deleted
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
            self.conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            raise RuntimeError(f"Error deleting row: {e}")

    def drop_table(self, table: str) -> bool:
        """Drop (delete) a table from the database

        Args:
            table: Table name to drop

        Returns:
            True if successful
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Error dropping table: {e}")

    def drop_database(self) -> bool:
        """Drop (delete) the entire database file

        Returns:
            True if successful
        """
        # Close connection first
        self.close()

        # Delete the database file
        if self.db_path.exists():
            self.db_path.unlink()
            return True
        return False

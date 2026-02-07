"""
DBBox - Simple SQLite database utility

Part of the Box Suite - a modular Python CLI application framework.

DBBox provides a simple command-line interface for managing SQLite databases
with CRUD operations, schema management, and more.
"""

__version__ = "0.1.0"
__author__ = "Jeff Mirabile"
__license__ = "MIT"

from .manager import DBManager

__all__ = ["DBManager"]

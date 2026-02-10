#!/usr/bin/env python3
"""
DBBox CLI - Command-line interface for SQLite database management

Part of the Box Suite.
"""

import argparse
import sys
import json
from pathlib import Path
from confbox import get_app_data_dir
from .manager import DBManager


def print_table(rows, cursor_description):
    """Pretty print table results"""
    if not rows:
        print("No rows found")
        return

    # Get column names
    columns = [description[0] for description in cursor_description]

    # Print header
    header = " | ".join(f"{col:15}" for col in columns)
    print(header)
    print("-" * len(header))

    # Print rows
    for row in rows:
        print(" | ".join(f"{str(val):15}" for val in row))

    print(f"\n{len(rows)} row(s) returned")


def format_json(rows, cursor_description):
    """Format rows as JSON array"""
    if not rows:
        return "[]"

    columns = [description[0] for description in cursor_description]
    result = []
    for row in rows:
        row_dict = {col: val for col, val in zip(columns, row)}
        result.append(row_dict)

    return json.dumps(result, indent=2, ensure_ascii=False)


def format_jsonl(rows, cursor_description):
    """Format rows as JSON Lines (one object per line)"""
    if not rows:
        return ""

    columns = [description[0] for description in cursor_description]
    lines = []
    for row in rows:
        row_dict = {col: val for col, val in zip(columns, row)}
        lines.append(json.dumps(row_dict, ensure_ascii=False))

    return "\n".join(lines)


def format_csv(rows, cursor_description):
    """Format rows as CSV"""
    if not rows:
        return ""

    columns = [description[0] for description in cursor_description]

    # Header
    lines = [",".join(columns)]

    # Rows
    for row in rows:
        values = []
        for val in row:
            val_str = str(val) if val is not None else ""
            # Escape commas and quotes
            if "," in val_str or '"' in val_str or "\n" in val_str:
                val_str = '"' + val_str.replace('"', '""') + '"'
            values.append(val_str)
        lines.append(",".join(values))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="DBBox - Simple SQLite database utility (Part of the Box Suite)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all databases (four equivalent ways)
  dbbox databases                    # Positional command (recommended)
  dbbox -l                           # Short flag
  dbbox --databases                  # Explicit flag
  dbbox --list                       # Long flag alias

  # List tables in a database (four equivalent ways)
  dbbox mydb tables                  # Positional command (recommended)
  dbbox mydb -l                      # Short flag
  dbbox mydb --tables                # Explicit flag
  dbbox mydb --list                  # Long flag alias

  # Create table with schema
  dbbox mydb users --schema name:TEXT age:INTEGER email:TEXT

  # Insert data
  dbbox mydb users -c 'John Doe' 30 'john@example.com'

  # Read all rows
  dbbox mydb users -r

  # Read specific row
  dbbox mydb users -r 1

  # Update row
  dbbox mydb users -u 1 'Jane Doe' 31 'jane@example.com'

  # Delete row
  dbbox mydb users -d 1

  # Drop table (with confirmation)
  dbbox mydb users --drop-table

  # Drop database (with confirmation)
  dbbox mydb --drop-database

  # Import from stdin
  cat data.txt | dbbox mydb users --import
  echo "Alice 30 alice@example.com" | dbbox mydb users --import

Database storage location (via ConfBox):
  Linux: ~/.local/share/dbbox/
  macOS: ~/Library/Application Support/dbbox/
  Windows: %APPDATA%\\dbbox\\
"""
    )

    parser.add_argument("database", nargs='?', help="Database name (without .db extension)")
    parser.add_argument("table", nargs='?', help="Table name")

    # CRUD operations
    parser.add_argument("-c", "--create", nargs='+', metavar="VALUE", help="Insert row with values")
    parser.add_argument("-r", "--read", nargs='?', const=True, metavar="ID", help="Read rows (optionally by ID)")
    parser.add_argument("-u", "--update", nargs='+', metavar="VALUE", help="Update row: -u <id> <val1> <val2> ...")
    parser.add_argument("-d", "--delete", type=int, metavar="ID", help="Delete row by ID")
    parser.add_argument("--import", action="store_true", dest="import_data", help="Import data from stdin (one record per line, space/tab separated)")

    # Database management
    parser.add_argument("--databases", action='store_true', help="List all databases")
    parser.add_argument("-l", "--list", action='store_true', help="List databases (if no db specified) or tables (if db specified)")

    # Table management
    parser.add_argument("--schema", nargs='+', metavar="COL:TYPE", help="Create table with schema")
    parser.add_argument("--tables", action='store_true', help="List all tables")
    parser.add_argument("--info", action='store_true', help="Show table information")
    parser.add_argument("--drop-table", action='store_true', help="Drop (delete) a table")
    parser.add_argument("--path", action='store_true', help="Show database file path")
    parser.add_argument("--drop-database", action='store_true', help="Drop (delete) entire database")

    # Output formats
    parser.add_argument("--json", action='store_true', help="Output as JSON")
    parser.add_argument("--jsonl", action='store_true', help="Output as JSON Lines (one object per line)")
    parser.add_argument("--csv", action='store_true', help="Output as CSV")

    args = parser.parse_args()

    # Support positional commands (like NoBox)
    # "dbbox databases" -> same as "dbbox --databases"
    if args.database == "databases":
        args.databases = True
        args.database = None

    # "dbbox mydb tables" -> same as "dbbox mydb --tables"
    if args.table == "tables":
        args.tables = True
        args.table = None

    # Handle list databases (no specific database needed)
    # Both --databases and --list (without db name) work the same way
    if args.databases or (args.list and not args.database):
        db_dir = get_app_data_dir("dbbox")

        if not db_dir.exists():
            print(f"No databases directory found at: {db_dir}")
            print("Create a database first with: dbbox <name> <table> --schema ...")
            return 0

        # Find all .db files
        db_files = sorted(db_dir.glob("*.db"))

        if not db_files:
            print(f"No databases found in: {db_dir}")
            print("Create a database first with: dbbox <name> <table> --schema ...")
            return 0

        print(f"Databases in {db_dir}:")
        for db_file in db_files:
            db_name = db_file.stem  # filename without extension
            db_size = db_file.stat().st_size
            # Format size
            if db_size < 1024:
                size_str = f"{db_size}B"
            elif db_size < 1024 * 1024:
                size_str = f"{db_size / 1024:.1f}KB"
            else:
                size_str = f"{db_size / (1024 * 1024):.1f}MB"
            print(f"  - {db_name:<20} ({size_str})")

        print(f"\nTotal: {len(db_files)} database(s)")
        return 0

    # Require database name for other operations
    if not args.database:
        parser.error("database name is required for this operation (or use --databases/--list to list all)")

    # Handle database path
    if args.path:
        db_dir = get_app_data_dir("dbbox")
        db_path = db_dir / f"{args.database}.db"
        print(f"Database directory: {db_dir}")
        print(f"Database path: {db_path}")
        print(f"Exists: {db_path.exists()}")
        return 0

    # Handle drop database
    if args.drop_database:
        db_dir = get_app_data_dir("dbbox")
        db_path = db_dir / f"{args.database}.db"

        if not db_path.exists():
            print(f"Database '{args.database}' does not exist")
            return 1

        # Confirmation prompt
        response = input(f"Are you sure you want to drop database '{args.database}'? This cannot be undone. (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled")
            return 0

        with DBManager(args.database) as db:
            db.drop_database()

        print(f"✓ Dropped database '{args.database}'")
        return 0

    # Use context manager for database connection
    try:
        with DBManager(args.database) as db:

            # List tables
            # Both --tables and --list (with db name) work the same way
            if args.tables or args.list:
                tables = db.list_tables()
                if tables:
                    print(f"Tables in '{args.database}':")
                    for table in tables:
                        print(f"  - {table}")
                else:
                    print(f"No tables in '{args.database}'")
                return 0

            # Require table name for other operations
            if not args.table:
                parser.error("table name is required for this operation")

            # Show table info
            if args.info:
                info = db.table_info(args.table)
                if not info:
                    print(f"Table '{args.table}' does not exist")
                    return 1

                print(f"Table: {args.table}")
                print(f"{'Column':<20} {'Type':<15} {'NotNull':<10} {'PK':<5}")
                print("-" * 50)
                for col in info:
                    print(f"{col[1]:<20} {col[2]:<15} {bool(col[3])!s:<10} {bool(col[5])!s:<5}")
                return 0

            # Drop table
            if args.drop_table:
                info = db.table_info(args.table)
                if not info:
                    print(f"Table '{args.table}' does not exist")
                    return 1

                # Confirmation prompt
                response = input(f"Are you sure you want to drop table '{args.table}' from database '{args.database}'? This cannot be undone. (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Cancelled")
                    return 0

                db.drop_table(args.table)
                print(f"✓ Dropped table '{args.table}'")
                return 0

            # Create table
            if args.schema:
                db.create_table(args.table, args.schema)
                print(f"✓ Table '{args.table}' created successfully")
                return 0

            # CRUD operations
            if args.create:
                row_id = db.insert(args.table, args.create)
                print(f"✓ Inserted row with id={row_id}")

            elif args.read is not None:
                if args.read is True:
                    rows = db.select(args.table)
                else:
                    try:
                        row_id = int(args.read)
                        rows = db.select(args.table, row_id)
                    except ValueError:
                        print(f"Error: Invalid ID '{args.read}'")
                        return 1

                # Get cursor description for column names
                cursor = db.conn.cursor()
                cursor.execute(f"SELECT * FROM {args.table} LIMIT 0")

                # Format output based on flags
                if args.json:
                    output = format_json(rows, cursor.description)
                    print(output)
                elif args.jsonl:
                    output = format_jsonl(rows, cursor.description)
                    print(output)
                elif args.csv:
                    output = format_csv(rows, cursor.description)
                    print(output)
                else:
                    # Default: pretty table
                    print_table(rows, cursor.description)

            elif args.update:
                if len(args.update) < 2:
                    print("Error: Update requires at least ID and one value")
                    return 1

                try:
                    row_id = int(args.update[0])
                    values = args.update[1:]
                    count = db.update(args.table, row_id, values)

                    if count == 0:
                        print(f"No row with id={row_id} found")
                    else:
                        print(f"✓ Updated row id={row_id}")
                except ValueError:
                    print(f"Error: Invalid ID '{args.update[0]}'")
                    return 1

            elif args.delete:
                count = db.delete(args.table, args.delete)

                if count == 0:
                    print(f"No row with id={args.delete} found")
                else:
                    print(f"✓ Deleted row id={args.delete}")

            elif args.import_data:
                # Import data from stdin
                # Format: one record per line, values separated by spaces or tabs
                # Values must match table schema (excluding auto-increment id)

                # Check if table exists
                info = db.table_info(args.table)
                if not info:
                    print(f"Error: Table '{args.table}' does not exist. Create it first with --schema", file=sys.stderr)
                    return 1

                # Get expected number of columns (excluding id)
                expected_cols = len([col for col in info if col[1] != 'id'])

                imported_count = 0
                error_count = 0

                print(f"Importing data into '{args.table}' (expecting {expected_cols} values per line)...", file=sys.stderr)

                for line_num, line in enumerate(sys.stdin, 1):
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Split by whitespace (handles both spaces and tabs)
                    values = line.split()

                    if len(values) != expected_cols:
                        error_count += 1
                        print(f"Warning line {line_num}: Expected {expected_cols} values, got {len(values)} - skipping", file=sys.stderr)
                        continue

                    try:
                        db.insert(args.table, values)
                        imported_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Error line {line_num}: {e}", file=sys.stderr)

                # Summary
                if error_count > 0:
                    print(f"✓ Imported {imported_count} row(s), {error_count} error(s)")
                else:
                    print(f"✓ Imported {imported_count} row(s)")

                if imported_count == 0 and error_count == 0:
                    print("No data provided on stdin", file=sys.stderr)
                    return 1

            else:
                parser.error("No operation specified. Use -c, -r, -u, -d, --import, --schema, --list, or --info")

    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAborted")
        return 130

    return 0


if __name__ == "__main__":
    sys.exit(main())

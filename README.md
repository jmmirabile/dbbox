# DBBox

**Simple SQLite database utility with CRUD operations via CLI**

Part of the [Box Suite](https://github.com/jmmirabile/confbox) - a modular Python CLI application framework.

## Features

- **Simple CRUD operations** via command-line flags (`-c`, `-r`, `-u`, `-d`)
- **Schema management** with type-safe column definitions
- **Cross-platform storage** using [ConfBox](https://pypi.org/project/confbox/) for OS-specific directories
- **Pretty-printed output** for SELECT queries
- **Auto-increment IDs** by default
- **Zero configuration** - just install and use

## Installation

```bash
pip install dbbox
```

Or install from source:

```bash
git clone https://github.com/jmmirabile/dbbox.git
cd dbbox
pip install -e .
```

## Storage Location

DBBox uses ConfBox to store databases in OS-specific data directories:

| OS | Storage Location |
|----|-----------------|
| Linux | `~/.local/share/dbbox/` |
| macOS | `~/Library/Application Support/dbbox/` |
| Windows | `%APPDATA%\dbbox\` |

## Quick Start

```bash
# Create a table with schema
dbbox mydb users --schema name:TEXT age:INTEGER email:TEXT

# Insert data
dbbox mydb users -c 'John Doe' 30 'john@example.com'
dbbox mydb users -c 'Jane Smith' 25 'jane@example.com'

# Read all rows
dbbox mydb users -r

# Read specific row by ID
dbbox mydb users -r 1

# Update a row
dbbox mydb users -u 1 'John Updated' 31 'john.new@example.com'

# Delete a row
dbbox mydb users -d 2

# Show table info
dbbox mydb users --info

# List all tables
dbbox mydb --list

# Show database path
dbbox mydb --path
```

## Listing Databases and Tables

DBBox provides multiple ways to list databases and tables for flexibility:

### List All Databases

```bash
# Three equivalent ways:
dbbox databases         # Positional command (recommended)
dbbox --databases       # Explicit flag
dbbox --list            # Context-aware shortcut
```

### List Tables in a Database

```bash
# Three equivalent ways:
dbbox mydb tables       # Positional command (recommended)
dbbox mydb --tables     # Explicit flag
dbbox mydb --list       # Context-aware shortcut
```

**The `--list` flag is context-aware:**
- Without database name: lists databases
- With database name: lists tables

## Usage

### Create Table

```bash
dbbox <dbname> <table> --schema <col:type> <col:type> ...
```

**Example:**
```bash
dbbox mydb products --schema name:TEXT price:REAL stock:INTEGER
```

**Note:** An `id INTEGER PRIMARY KEY AUTOINCREMENT` column is added automatically.

**Supported SQLite types:** `TEXT`, `INTEGER`, `REAL`, `BLOB`, `NUMERIC`

### Insert (Create)

```bash
dbbox <dbname> <table> -c <value1> <value2> ...
```

**Example:**
```bash
dbbox mydb products -c 'Widget' 19.99 100
```

### Select (Read)

```bash
# Read all rows
dbbox <dbname> <table> -r

# Read specific row by ID
dbbox <dbname> <table> -r <id>
```

**Examples:**
```bash
dbbox mydb products -r           # All rows
dbbox mydb products -r 5         # Row with id=5
```

### Update

```bash
dbbox <dbname> <table> -u <id> <value1> <value2> ...
```

**Example:**
```bash
dbbox mydb products -u 5 'Super Widget' 24.99 150
```

### Delete

```bash
dbbox <dbname> <table> -d <id>
```

**Example:**
```bash
dbbox mydb products -d 5
```

### Database Management

```bash
# List all tables in a database
dbbox <dbname> --list

# Show table schema/info
dbbox <dbname> <table> --info

# Show database file path
dbbox <dbname> --path
```

## Complete Example

```bash
# Create a contacts database
dbbox contacts people --schema name:TEXT phone:TEXT email:TEXT

# Add some contacts
dbbox contacts people -c 'Alice Smith' '555-1234' 'alice@example.com'
dbbox contacts people -c 'Bob Jones' '555-5678' 'bob@example.com'

# View all contacts
dbbox contacts people -r

# Output:
# id              | name            | phone           | email
# --------------------------------------------------------------------------
# 1               | Alice Smith     | 555-1234        | alice@example.com
# 2               | Bob Jones       | 555-5678        | bob@example.com
#
# 2 row(s) returned

# Update a contact
dbbox contacts people -u 2 'Robert Jones' '555-5678' 'robert@example.com'

# Delete a contact
dbbox contacts people -d 1

# Show table structure
dbbox contacts people --info

# List all tables
dbbox contacts --list
```

## Use Cases

- **Quick data storage** for scripts and automation
- **Prototyping** database schemas
- **Data tracking** for personal projects
- **Testing** SQL queries and table designs
- **Simple CRUD apps** without writing database code
- **Local caching** of data

## The Box Suite

DBBox is part of the Box Suite - a collection of modular Python packages for building CLI applications:

- **[ConfBox](https://pypi.org/project/confbox/)** ✅ - Cross-platform configuration management
- **DBBox** ✅ - SQLite database utility (this package)
- **PlugBox** 🔨 - Plugin system (planned)
- **CLIBox** 🔨 - Complete CLI framework (planned)
- **RestBox** 🔨 - REST API testing tool (planned)

Each package can be used independently or together for maximum flexibility.

## Python API

DBBox can also be used as a Python library:

```python
from dbbox import DBManager

# Create database manager
with DBManager("mydb") as db:
    # Create table
    db.create_table("users", ["name:TEXT", "age:INTEGER"])

    # Insert data
    user_id = db.insert("users", ["John Doe", 30])

    # Select data
    rows = db.select("users")
    for row in rows:
        print(dict(row))

    # Update data
    db.update("users", user_id, ["Jane Doe", 31])

    # Delete data
    db.delete("users", user_id)
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## Requirements

- Python 3.8+
- [confbox](https://pypi.org/project/confbox/) >= 0.1.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **PyPI:** https://pypi.org/project/dbbox/ (coming soon)
- **GitHub:** https://github.com/jmmirabile/dbbox
- **ConfBox:** https://github.com/jmmirabile/confbox
- **Box Suite Design:** See ConfBox repository for the full Box Suite vision

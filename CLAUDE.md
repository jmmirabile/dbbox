# DBBox Project

## Project Overview
DBBox - SQLite database management utility with CRUD operations via CLI.

Part of the [Box Suite](https://github.com/jmmirabile/confbox) - a modular Python CLI utility framework.

## Project Structure
```
dbbox/
├── dbbox/
│   ├── __init__.py
│   ├── manager.py        # DBManager - database operations
│   └── cli.py            # CLI command parser and executor
├── tests/
├── docs/
├── setup.py
├── pyproject.toml
├── README.md
├── SUMMARY.md            # Project summary and overview
├── CLAUDE.md             # This file - project context
└── LICENSE
```

## Commands Provided

**Installation:**
```bash
pip install dbbox
```

**Provides command:**
- `dbbox` (alias: `db`) - SQLite database management

## Quick Reference

```bash
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

# Import from stdin
cat data.txt | dbbox mydb users --import
echo "Alice 30 alice@example.com" | dbbox mydb users --import

# List all databases
dbbox --databases

# Output formats
dbbox mydb users -r --json       # JSON array
dbbox mydb users -r --jsonl      # JSON Lines
dbbox mydb users -r --csv        # CSV for Excel

# Show table info
dbbox mydb users --info

# List tables
dbbox mydb --tables

# Database path
dbbox mydb --path
```

## Storage Location

Uses ConfBox for cross-platform directories:

| OS | Storage Location |
|----|------------------|
| Linux | `~/.local/share/dbbox/` |
| macOS | `~/Library/Application Support/dbbox/` |
| Windows | `%APPDATA%\dbbox\` |

**Structure:**
```
~/.local/share/dbbox/
├── mydb.db
├── inventory.db
└── todos.db
```

## Python API

DBBox can be used programmatically in Python scripts:

```python
from dbbox import DBManager

# Using context manager (recommended)
with DBManager("mydb") as db:
    # Create table
    db.create_table("users", ["name:TEXT", "age:INTEGER", "email:TEXT"])

    # Insert
    row_id = db.insert("users", ["Alice", 30, "alice@example.com"])

    # Select all
    rows = db.select("users")
    for row in rows:
        print(row)

    # Select by ID
    row = db.select("users", row_id)

    # Update
    db.update("users", row_id, ["Alice Smith", 31, "asmith@example.com"])

    # Delete
    db.delete("users", row_id)

    # Table operations
    tables = db.list_tables()
    info = db.table_info("users")
```

## Development Information

### Build Commands
```bash
pip install -e .               # Development install
pip install -e ".[dev]"        # With dev dependencies
```

### Test Commands
```bash
pytest                         # Run all tests
pytest -v                      # Verbose output
pytest tests/test_manager.py   # Specific test file
```

### Git Repository
```bash
# Current status
git remote -v                  # Show GitHub remote
git log --oneline              # View commit history
```

## Dependencies

- **Python 3.8+**
- **confbox** >= 0.1.0 - Cross-platform directory management

## Key Features

1. **CRUD Operations** - Create, Read, Update, Delete rows
2. **Schema Definition** - Define table schemas via CLI
3. **Stdin Import** - Bulk import from pipes/files
4. **Multiple Output Formats** - JSON, JSON Lines, CSV, pretty table
5. **Database Management** - List databases, tables, show info
6. **Python API** - Use programmatically in scripts
7. **Cross-platform** - Works on Linux, macOS, Windows

## Use Cases

### Operational Use Cases
- Command history tracking across servers
- Change log / audit trails
- SSL certificate inventory and expiration tracking
- Incident response logging during outages
- Deployment tracking (what's deployed where)

### Developer/DevOps Workflows
- API response caching (avoid rate limits)
- Script data backend for automation
- Pipeline data aggregation (collect from multiple sources)
- Quick data correlation and analysis
- Time-series data collection

### Personal Productivity
- Todo/task tracking
- Bookmark/link management with tags
- Password rotation tracking (metadata only)
- Note-taking and snippet storage

### Advanced Patterns
- Integration testing data/fixtures
- Configuration snapshot storage
- Metrics collection over time
- Server inventory management

See README.md for detailed examples and use cases.

## Box Suite Architecture Decision: Monorepo vs Separate Repos

### Discussion (2026-02-07)

Considered consolidating all Box Suite tools into a single monorepo but decided to **keep separate repos during initial development**.

### Options Considered

**Option 1: Python Monorepo with Separate Packages**
```
box-suite/
├── packages/
│   ├── confbox/
│   ├── dbbox/
│   ├── nobox/
│   └── plugbox/
├── docs/
└── README.md
```
- Pros: Single clone, unified CI/CD, easier to share code, cross-package refactoring
- Cons: More complex setup, need independent versioning, larger repo size

**Option 2: Namespace Packages**
```
from box.conf import get_app_data_dir
from box.db import DBManager
from box.no import DictStore
```
- Pros: Professional structure, import consistency, easy code sharing
- Cons: Breaking change for published ConfBox, more complex packaging

**Option 3: Keep Separate + Meta Repo**
- Keep individual repos, create meta repo with git submodules
- Pros: Independent versioning, clone just what you need
- Cons: Submodules are clunky, shared code harder

### Decision: Keep Separate During Development ✅

**Rationale:**
1. **Focus and Simplicity** - Each tool can evolve independently without monorepo complexity
2. **Independent Maturity** - Each tool reaches v1.0 at its own pace
3. **Natural Pattern Discovery** - Shared patterns will emerge organically as more tools are built
4. **Publishing Flexibility** - Publish to PyPI independently as each becomes ready
5. **Easier to Consolidate Later** - Moving separate → monorepo is straightforward; reverse is hard

**Current State:**
```
Documents/dev/
├── confbox/     ✅ Published to PyPI (v0.1.0)
├── dbbox/       ✅ Complete, ready for PyPI
├── nobox/       ✅ Complete, ready for PyPI
├── plugbox/     🔨 Future
├── clibox/      🔨 Future
└── restbox/     🔨 Future
```

**When to Reconsider Consolidation:**
- Significant code duplication across multiple tools
- Shared utilities that need to be synced
- All or most tools are stable (v1.0+)
- Coordinated releases becoming necessary
- Contributors working across multiple tools

Until then, keep the flexibility of independent repos during the creative/exploratory phase.

## Related Projects

### Box Suite
- **[ConfBox](https://pypi.org/project/confbox/)** ✅ - Config management (published)
- **[DBBox](https://github.com/jmmirabile/dbbox)** ✅ - SQLite utility (this project)
- **[NoBox](https://github.com/jmmirabile/nobox)** ✅ - JSON/YAML key-value storage (complete)
- **PlugBox** 🔨 - Plugin system (planned)
- **CLIBox** 🔨 - CLI framework (planned)
- **RestBox** 🔨 - REST API client framework (planned)

### Comparison: DBBox vs NoBox

**Use DBBox when:**
- Structured, relational data
- Fixed schema
- SQL queries needed
- Flat tabular data
- Need data integrity constraints

**Use NoBox when:**
- Nested, complex data structures
- Variable/flexible fields
- No schema needed
- JSON/YAML natural format
- Key-value lookups

## Development Status

- **Current Phase:** Complete and production-ready
- **Version:** 0.1.0
- **Status:** All core features implemented and tested
- **Git Status:** Initialized, committed (e0d71ff)
- **Next Steps:**
  1. Publish to PyPI
  2. Add pytest test suite
  3. Add shell completion
  4. Expand Python API examples in README

## Recent Enhancements (2026-02-06/07)

### Stdin Import Feature
- Added `--import` flag for bulk data import
- Format: one record per line, space/tab separated
- Error handling for malformed lines
- Summary report with import/error counts

### Multiple Output Formats
- `--json` - JSON array format (pipe to jq)
- `--jsonl` - JSON Lines format (one object per line)
- `--csv` - CSV format (import to Excel)
- Default: Pretty table output

### Database Listing
- Added `--databases` flag to list all databases
- Shows database names and sizes (B/KB/MB)
- Works without specifying database name
- Critical feature that was initially missed

## Notes

- Single user tool - no concurrent access handling
- Complements NoBox (schema-based vs schema-less)
- Part of Box Suite ecosystem
- Follows Box Suite principles: modular, independent, complementary, professional
- Alias suggestion: `alias db='dbbox'`

---

**Project Started:** 2026-02-06
**Working Directory:** /home/jeffmira/Documents/dev/dbbox
**Git Repository:** Initialized (commit e0d71ff)
**GitHub Repository:** Not yet created

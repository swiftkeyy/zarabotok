#!/usr/bin/env python3
"""
Database migration helper script
Provides easy commands to manage database migrations
"""

import os
import sys
import subprocess


def run_command(cmd):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def main():
    if len(sys.argv) < 2:
        print("""
Database Migration Helper

Usage:
  python migrate.py upgrade    - Apply all pending migrations
  python migrate.py downgrade  - Rollback one migration
  python migrate.py current    - Show current database version
  python migrate.py history    - Show migration history
  python migrate.py stamp      - Mark database as up-to-date without running migrations
  python migrate.py create <name> - Create a new migration file

Environment Variables:
  DATABASE_URL - PostgreSQL connection string (for Railway)
  DB_PATH      - SQLite database path (for bothost.ru, default: /app/data/bot_data.db)

Examples:
  # Apply all migrations
  python migrate.py upgrade

  # Rollback one migration
  python migrate.py downgrade

  # Mark existing database as up-to-date
  python migrate.py stamp

  # Create new migration
  python migrate.py create add_goals_table
""")
        return 1

    command = sys.argv[1]

    if command == "upgrade":
        return run_command("alembic upgrade head")
    elif command == "downgrade":
        return run_command("alembic downgrade -1")
    elif command == "current":
        return run_command("alembic current")
    elif command == "history":
        return run_command("alembic history")
    elif command == "stamp":
        return run_command("alembic stamp head")
    elif command == "create":
        if len(sys.argv) < 3:
            print("Error: Please provide a migration name")
            print("Usage: python migrate.py create <name>")
            return 1
        name = sys.argv[2]
        return run_command(f"alembic revision -m \"{name}\"")
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

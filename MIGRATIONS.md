# Database Migrations Guide

This project uses Alembic for database schema versioning and migrations.

## Overview

The migration system supports both:
- **PostgreSQL** (Railway deployment)
- **SQLite** (bothost.ru deployment)

The database type is automatically detected from the `DATABASE_URL` environment variable.

## Configuration

### PostgreSQL (Railway)
Set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### SQLite (bothost.ru)
Set the `DB_PATH` environment variable (optional, defaults to `/app/data/bot_data.db`):
```bash
export DB_PATH="/path/to/bot_data.db"
```

## Common Commands

### Apply all pending migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

### View current database version
```bash
alembic current
```

### Create a new migration
```bash
alembic revision -m "description_of_changes"
```

## Initial Setup

If you're setting up a new database, run:
```bash
alembic upgrade head
```

This will create all tables defined in the migrations.

## Existing Database

If you already have a database with the existing schema (users, stats, forced_channels), you need to mark the initial migration as applied without actually running it:

```bash
alembic stamp head
```

This tells Alembic that your database is already at the latest version.

## Migration Files

Migration files are located in `alembic/versions/`. Each file contains:
- `upgrade()` - SQL operations to apply the migration
- `downgrade()` - SQL operations to rollback the migration

## Current Schema

The initial migration (`857954c0ffeb_initial_schema.py`) creates:

### users table
- `user_id` (BIGINT, PRIMARY KEY)
- `username` (TEXT)
- `first_name` (TEXT)
- `joined_at` (TIMESTAMP)
- `last_active` (TIMESTAMP)

### stats table
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `user_id` (BIGINT)
- `month` (TEXT)
- `work_days` (INTEGER)
- `earnings` (INTEGER)
- `rate` (INTEGER)
- `passive_rate` (INTEGER)
- `saved_at` (TIMESTAMP)

### forced_channels table
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `channel_id` (BIGINT, UNIQUE)
- `channel_username` (TEXT)
- `title` (TEXT)
- `added_by` (BIGINT)
- `added_at` (TIMESTAMP)

## Best Practices

1. **Always test migrations** on a development database first
2. **Backup your database** before running migrations in production
3. **Review migration files** before applying them
4. **Never edit applied migrations** - create a new migration instead
5. **Use descriptive names** for migrations

## Troubleshooting

### "Can't locate revision identified by 'head'"
This means Alembic can't find any migrations. Make sure you're in the correct directory and the `alembic/versions/` folder contains migration files.

### "Target database is not up to date"
Run `alembic upgrade head` to apply pending migrations.

### "Multiple head revisions are present"
This happens when there are conflicting migration branches. Use `alembic merge` to resolve.

## Integration with main.py

The current `main.py` creates tables using raw SQL in the `init_db()` function. Once you've applied the initial migration, you can optionally remove the table creation code from `init_db()` and rely solely on Alembic for schema management.

However, for backward compatibility, you can keep both approaches - Alembic will skip creating tables that already exist.

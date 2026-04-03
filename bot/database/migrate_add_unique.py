"""
Migration: Add UNIQUE constraint on (message_id, chat_id) to payments_in and payments_out.

This script:
1. Finds and removes duplicate records (keeps the earliest by `id`)
2. Adds UNIQUE constraint on (message_id, chat_id)

Safe to run multiple times — checks if constraint already exists.

Usage:
    python -m bot.database.migrate_add_unique
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text

from bot.config import settings
from bot.database.models import Database


async def remove_duplicates(session, table_name: str) -> int:
    """Remove duplicate records, keeping the one with the smallest id."""
    # Find duplicates
    result = await session.execute(text(f"""
        SELECT message_id, chat_id, COUNT(*) as cnt, MIN(id) as keep_id
        FROM {table_name}
        GROUP BY message_id, chat_id
        HAVING COUNT(*) > 1
    """))
    duplicates = result.fetchall()

    total_deleted = 0
    for row in duplicates:
        message_id, chat_id, cnt, keep_id = row
        # Delete all duplicates except the one with the smallest id
        result = await session.execute(text(f"""
            DELETE FROM {table_name}
            WHERE message_id = :message_id AND chat_id = :chat_id AND id != :keep_id
        """), {"message_id": message_id, "chat_id": chat_id, "keep_id": keep_id})
        deleted = result.rowcount
        total_deleted += deleted
        print(f"  [{table_name}] message_id={message_id}, chat_id={chat_id}: "
              f"removed {deleted} duplicate(s), kept id={keep_id}")

    return total_deleted


async def add_unique_constraint(session, table_name: str, constraint_name: str):
    """Add UNIQUE constraint if it doesn't exist (SQLite)."""
    # SQLite doesn't support ALTER TABLE ADD CONSTRAINT, so we need to check
    # if a unique index exists
    result = await session.execute(text(f"""
        SELECT name FROM sqlite_master
        WHERE type='index' AND tbl_name='{table_name}' AND sql LIKE '%UNIQUE%'
    """))
    existing = result.fetchall()

    # Also check for our specific constraint name
    for row in existing:
        if constraint_name in row[0]:
            print(f"  [{table_name}] Constraint '{constraint_name}' already exists, skipping")
            return

    # For SQLite, create a unique index instead of ALTER TABLE
    await session.execute(text(f"""
        CREATE UNIQUE INDEX IF NOT EXISTS {constraint_name}
        ON {table_name} (message_id, chat_id)
    """))
    print(f"  [{table_name}] Created unique index '{constraint_name}'")


async def main():
    print("=" * 60)
    print("Migration: Add UNIQUE(message_id, chat_id)")
    print("=" * 60)

    db = Database(settings.database_url)

    async with db.engine.begin() as conn:
        # Wrap in a raw connection for direct SQL
        session = conn

        # Step 1: Remove duplicates
        print("\n--- Step 1: Removing duplicates ---")
        for table in ["payments_in", "payments_out"]:
            deleted = await remove_duplicates(session, table)
            if deleted == 0:
                print(f"  [{table}] No duplicates found ✓")
            else:
                print(f"  [{table}] Removed {deleted} duplicate(s) total")

        # Step 2: Add unique constraints
        print("\n--- Step 2: Adding unique constraints ---")
        await add_unique_constraint(
            session, "payments_in", "uq_payments_in_message_chat"
        )
        await add_unique_constraint(
            session, "payments_out", "uq_payments_out_message_chat"
        )

    await db.close()

    print("\n✅ Migration completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

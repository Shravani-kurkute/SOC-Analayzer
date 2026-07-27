#!/usr/bin/env python3
"""Seed the database with a default admin user."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.database.session import async_session_factory
from app.models.user import User
from sqlalchemy import select


async def seed():
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@sentinelai.dev")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("Admin user already exists (id=%s)", existing.id)
            return

        admin = User(
            email="admin@sentinelai.dev",
            full_name="System Administrator",
            password_hash=hash_password("Admin@123"),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print("Created admin user: admin@sentinelai.dev / Admin@123 (role=admin)")


if __name__ == "__main__":
    asyncio.run(seed())

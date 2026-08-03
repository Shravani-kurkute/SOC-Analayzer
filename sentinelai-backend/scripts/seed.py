#!/usr/bin/env python3
"""Seed the database with default users."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.database.session import async_session_factory
from app.models.user import User
from sqlalchemy import select

USERS = [
    {
        "email": "admin@sentinelai.dev",
        "full_name": "System Administrator",
        "password": "Admin@123",
        "role": "admin",
    },
    {
        "email": "analyst@sentinelai.dev",
        "full_name": "Security Analyst",
        "password": "Analyst@123",
        "role": "analyst",
    },
    {
        "email": "viewer@sentinelai.dev",
        "full_name": "Viewer User",
        "password": "Viewer@123",
        "role": "viewer",
    },
]


async def seed():
    async with async_session_factory() as session:
        for user_data in USERS:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                if existing.password_hash != hash_password(user_data["password"]):
                    existing.password_hash = hash_password(user_data["password"])
                    existing.full_name = user_data["full_name"]
                    existing.role = user_data["role"]
                    existing.is_active = True
                    print(f"Updated user: {user_data['email']} (role={user_data['role']})")
                else:
                    print(f"User already exists: {user_data['email']} (role={user_data['role']})")
            else:
                user = User(
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                )
                session.add(user)
                print(f"Created user: {user_data['email']} / {user_data['password']} (role={user_data['role']})")

        await session.commit()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())

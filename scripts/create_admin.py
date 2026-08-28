import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import argparse
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, engine
from models.user import User
from services.auth import get_password_hash
from sqlalchemy import select

async def create_admin(email: str, password: str):
    async with engine.begin() as conn:
        from models.base import Base
        import models.user
        import models.project
        import models.service_item
        import models.contact_message
        await conn.run_sync(Base.metadata.create_all)
        
        # Check if is_admin column exists in SQLite table and add it if missing
        from sqlalchemy import text
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
        except Exception:
            pass  # Column already exists or table freshly created

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            print(f"User {email} already exists. Updating to admin and changing password...")
            user.is_admin = True
            user.hashed_password = get_password_hash(password)
        else:
            print(f"Creating new admin user {email}...")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                is_admin=True,
                is_active=True
            )
            session.add(user)
        
        await session.commit()
        print(f"Admin user {email} successfully created/updated!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an admin user for the Signal backend.")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password")
    
    args = parser.parse_args()
    asyncio.run(create_admin(args.email, args.password))

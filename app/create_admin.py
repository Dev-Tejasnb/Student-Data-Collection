import asyncio
import getpass
from datetime import datetime, timezone
from pymongo import AsyncMongoClient
from app.config import get_settings
from app.auth.security import get_password_hash


async def create_admin():
    settings = get_settings()

    print("=" * 50)
    print("  Create User Account")
    print("=" * 50)
    print()

    username = input("Username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return

    if len(username) < 3:
        print("Error: Username must be at least 3 characters")
        return

    password = getpass.getpass("Password: ")
    if not password:
        print("Error: Password cannot be empty")
        return

    if len(password) < 6:
        print("Error: Password must be at least 6 characters")
        return

    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        print("Error: Passwords do not match")
        return

    role = input("Role (admin/staff) [admin]: ").strip().lower()
    if role not in ["admin", "staff"]:
        role = "admin"

    client = AsyncMongoClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]

    try:
        await client.admin.command('ping')
        print("\nConnected to MongoDB")
    except Exception as e:
        print(f"\nError: Failed to connect to MongoDB: {e}")
        return

    existing_user = await db.users.find_one({"username": username})
    if existing_user:
        print(f"\nError: User '{username}' already exists")
        return

    user_doc = {
        "username": username,
        "password_hash": get_password_hash(password),
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }

    try:
        result = await db.users.insert_one(user_doc)
        print(f"\nSuccess! {role.capitalize()} account created with ID: {result.inserted_id}")
        print(f"Username: {username}")
        print(f"Role: {role}")
        print()
        print("You can now log in at http://localhost:8000/login")
    except Exception as e:
        print(f"\nError: Failed to create {role} account: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(create_admin())
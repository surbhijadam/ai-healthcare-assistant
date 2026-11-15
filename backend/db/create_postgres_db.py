import sys
import getpass
import asyncio
import asyncpg


async def create_database():
    print("=" * 60)
    print("MediCare AI — PostgreSQL Database Creator")
    print("=" * 60)
    
    password = sys.argv[1] if len(sys.argv) > 1 else None
    if not password:
        password = input("Enter your PostgreSQL 'postgres' user password: ")

    try:
        # Connect to default system 'postgres' maintenance database
        conn = await asyncpg.connect(
            user="postgres",
            password=password,
            database="postgres",
            host="localhost",
            port=5432,
        )
        print("Connected to PostgreSQL service successfully!")

        # Check if healthcare_db already exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'healthcare_db'"
        )
        if not exists:
            await conn.execute("CREATE DATABASE healthcare_db;")
            print("Database 'healthcare_db' created successfully!")
        else:
            print("Database 'healthcare_db' already exists!")

        await conn.close()

        # Update .env file automatically with user's verified password
        env_path = ".env"
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                content = f.read()
            import re
            content = re.sub(
                r"DATABASE_URL=postgresql\+asyncpg://postgres:[^@]+@localhost:5432/healthcare_db",
                f"DATABASE_URL=postgresql+asyncpg://postgres:{password}@localhost:5432/healthcare_db",
                content,
            )
            content = re.sub(
                r"SYNC_DATABASE_URL=postgresql://postgres:[^@]+@localhost:5432/healthcare_db",
                f"SYNC_DATABASE_URL=postgresql://postgres:{password}@localhost:5432/healthcare_db",
                content,
            )
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("Updated .env with your PostgreSQL credentials.")
        except Exception as e:
            print(f"Note: Please update your password in .env manually: {e}")

        print("\nNext step: Run 'python -m backend.db.init_db' to create all tables!")
        print("=" * 60)

    except asyncpg.exceptions.InvalidPasswordError:
        print("\n[ERROR] Incorrect password! Please re-run and enter the password set during PostgreSQL installation.")
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(create_database())

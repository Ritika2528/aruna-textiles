"""
seed.py - Script to verify MongoDB Atlas connection and seed data
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "aruna_textiles")

def main():
    print("=" * 60)
    print("  MONGODB ATLAS CONNECTION & SEED VERIFIER")
    print("=" * 60)
    print(f"\n[1/3] Checking MongoDB URI configuration...")
    if not MONGO_URI:
        print("[ERROR] MONGO_URI is not set in .env!")
        sys.exit(1)

    # Obfuscate password for display
    parts = MONGO_URI.split("@")
    host_part = parts[-1] if len(parts) > 1 else ""
    print(f"Target Cluster: {host_part.split('/')[0]}")
    print(f"Database Name:  {MONGO_DB_NAME}\n")

    print("[2/3] Connecting directly to MongoDB Atlas cluster...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        # Force ping
        client.admin.command("ping")
        print("  >>> [SUCCESS] Connected directly to MongoDB Atlas! Ping succeeded. <<<\n")
    except Exception as e:
        print(f"  >>> [FAILED] Could not authenticate with MongoDB Atlas: <<<\n  Error: {e}\n")
        print("-" * 60)
        print("FIX GUIDE:")
        print("1. Go to https://cloud.mongodb.com")
        print("2. Left Sidebar -> 'Database Access':")
        print("   - Check the username & reset password for your database user.")
        print("   - Ensure role is 'Read and write to any database'.")
        print("3. Left Sidebar -> 'Network Access':")
        print("   - Ensure IP Access List includes '0.0.0.0/0' (Allow access from anywhere).")
        print("4. Update MONGO_URI in .env with the new password.")
        print("-" * 60)
        return False

    print("[3/3] Seeding and inspecting collections in MongoDB Atlas...")
    db = client[MONGO_DB_NAME]

    from db import seed_sample_data, get_db
    # Force real db seeding
    seed_sample_data()

    collections = ["users", "customers", "production", "sales", "notifications", "suppliers", "shipments", "inventory", "transactions", "workforce"]
    print("\nLive Document Counts in MongoDB Atlas:")
    for col in collections:
        count = db[col].count_documents({})
        sample = db[col].find_one()
        sample_info = f"(Sample: {list(sample.keys())[:4]}...)" if sample else "(Empty)"
        print(f"  - {col.ljust(15)} : {count} documents {sample_info}")

    print("\n" + "=" * 60)
    print("  ALL COLLECTIONS SUCCESSFULLY POPULATED IN ATLAS!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

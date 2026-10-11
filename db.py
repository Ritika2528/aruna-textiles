"""
db.py - MongoDB Atlas connection module for Aruna Textiles Production System
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "aruna_textiles")

_client = None
_db = None


def get_db():
    """Get the MongoDB database instance (singleton)."""
    global _client, _db
    if _db is None:
        try:
            if not MONGO_URI:
                raise ConnectionFailure("MONGO_URI is not set")
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Verify connection
            _client.admin.command("ping")
            _db = _client[MONGO_DB_NAME]
            print(f"[OK] Connected to MongoDB Atlas - database: '{MONGO_DB_NAME}'")
        except Exception as e:
            print(f"[!] MongoDB Atlas connection failed: {e}. Falling back to local in-memory database (mongomock)...")
            try:
                import mongomock
                _client = mongomock.MongoClient()
                _db = _client[MONGO_DB_NAME]
                print(f"[OK] Initialized fallback database: '{MONGO_DB_NAME}'")
            except Exception as fallback_err:
                print(f"[ERROR] Fallback failed: {fallback_err}")
                raise
    return _db


def get_collection(name):
    """Return a named collection from the database."""
    return get_db()[name]


# ── Collection helpers ──────────────────────────────────────────────────────

def seed_sample_data():
    """Seed sample records into MongoDB if collections are empty."""
    db = get_db()

    # Users (RBAC & Authentication)
    if db.users.count_documents({}) == 0:
        db.users.insert_one({
            "id": 1,
            "username": "admin",
            "password_hash": generate_password_hash("admin123"),
            "role": "admin",
            "full_name": "System Administrator",
            "created_at": "2026-03-15T00:00:00Z",
            "failed_attempts": 0,
            "lockout_until": 0
        })
        print("  [OK] Seeded users collection with secure hashed admin account")

    # Customers
    if db.customers.count_documents({}) == 0:
        db.customers.insert_many([
            {"id": 1, "customer_id": "CUST001", "customer_name": "Rajesh Kumar",
             "company_name": "TechSpun Ltd", "phone_number": "9876543210",
             "product_type": "Cotton Yarn", "order_quantity": 500,
             "order_status": "Completed", "created_at": "2026-03-15"},
            {"id": 2, "customer_id": "CUST002", "customer_name": "Priya Singh",
             "company_name": "TextiCorp Industries", "phone_number": "9876543211",
             "product_type": "Polyester Blend", "order_quantity": 750,
             "order_status": "Processing", "created_at": "2026-03-16"},
            {"id": 3, "customer_id": "CUST003", "customer_name": "Vikram Patel",
             "company_name": "Global Fabrics", "phone_number": "9876543212",
             "product_type": "Silk Blend", "order_quantity": 300,
             "order_status": "Pending", "created_at": "2026-03-17"},
            {"id": 4, "customer_id": "CUST004", "customer_name": "Anita Sharma",
             "company_name": "Deccan Textiles", "phone_number": "9876543213",
             "product_type": "Cotton Yarn", "order_quantity": 420,
             "order_status": "Completed", "created_at": "2026-04-02"},
            {"id": 5, "customer_id": "CUST005", "customer_name": "Suresh Reddy",
             "company_name": "South Weave Co.", "phone_number": "9876543214",
             "product_type": "Wool Blend", "order_quantity": 280,
             "order_status": "Processing", "created_at": "2026-04-10"},
            {"id": 6, "customer_id": "CUST006", "customer_name": "Kavitha Nair",
             "company_name": "Kerala Fabrics Ltd", "phone_number": "9876543215",
             "product_type": "Linen Yarn", "order_quantity": 350,
             "order_status": "Completed", "created_at": "2026-05-01"},
            {"id": 7, "customer_id": "CUST007", "customer_name": "Mohan Das",
             "company_name": "Bengal Cotton Works", "phone_number": "9876543216",
             "product_type": "Cotton Yarn", "order_quantity": 600,
             "order_status": "Pending", "created_at": "2026-05-15"},
            {"id": 8, "customer_id": "CUST008", "customer_name": "Lakshmi Iyer",
             "company_name": "Coimbatore Spun Ltd", "phone_number": "9876543217",
             "product_type": "Polyester Blend", "order_quantity": 480,
             "order_status": "Completed", "created_at": "2026-06-01"},
        ])
        print("  [OK] Seeded customers collection")

    # Production
    if db.production.count_documents({}) == 0:
        db.production.insert_many([
            {"id": 1, "production_id": "PROD001", "machine_id": "M001",
             "machine_type": "Ring Frame", "production_quantity": 320,
             "production_status": "Completed", "created_at": "2026-03-15"},
            {"id": 2, "production_id": "PROD002", "machine_id": "M002",
             "machine_type": "Carding Machine", "production_quantity": 280,
             "production_status": "Completed", "created_at": "2026-03-16"},
            {"id": 3, "production_id": "PROD003", "machine_id": "M003",
             "machine_type": "Spinning Frame", "production_quantity": 195,
             "production_status": "Processing", "created_at": "2026-04-05"},
            {"id": 4, "production_id": "PROD004", "machine_id": "M004",
             "machine_type": "Winding Machine", "production_quantity": 240,
             "production_status": "Completed", "created_at": "2026-04-10"},
            {"id": 5, "production_id": "PROD005", "machine_id": "M005",
             "machine_type": "Roving Frame", "production_quantity": 160,
             "production_status": "Incomplete", "created_at": "2026-04-15"},
            {"id": 6, "production_id": "PROD006", "machine_id": "M001",
             "machine_type": "Ring Frame", "production_quantity": 305,
             "production_status": "Completed", "created_at": "2026-05-02"},
            {"id": 7, "production_id": "PROD007", "machine_id": "M002",
             "machine_type": "Carding Machine", "production_quantity": 260,
             "production_status": "Processing", "created_at": "2026-05-10"},
            {"id": 8, "production_id": "PROD008", "machine_id": "M003",
             "machine_type": "Spinning Frame", "production_quantity": 210,
             "production_status": "Completed", "created_at": "2026-06-01"},
        ])
        print("  [OK] Seeded production collection")

    # Sales — spread across 6 months for a meaningful trend chart
    if db.sales.count_documents({}) == 0:
        db.sales.insert_many([
            {"id": 1,  "product_id": "P001", "product_name": "Cotton Yarn",
             "units_sold": 480, "sale_price": 32000, "sale_date": "2026-01-15", "cost": 21000},
            {"id": 2,  "product_id": "P002", "product_name": "Polyester Blend",
             "units_sold": 350, "sale_price": 24500, "sale_date": "2026-01-28", "cost": 16000},
            {"id": 3,  "product_id": "P003", "product_name": "Silk Blend",
             "units_sold": 120, "sale_price": 18000, "sale_date": "2026-02-10", "cost": 11500},
            {"id": 4,  "product_id": "P004", "product_name": "Wool Blend",
             "units_sold": 200, "sale_price": 21000, "sale_date": "2026-02-20", "cost": 14000},
            {"id": 5,  "product_id": "P005", "product_name": "Linen Yarn",
             "units_sold": 160, "sale_price": 14000, "sale_date": "2026-02-25", "cost": 9000},
            {"id": 6,  "product_id": "P001", "product_name": "Cotton Yarn",
             "units_sold": 520, "sale_price": 36400, "sale_date": "2026-03-05", "cost": 24000},
            {"id": 7,  "product_id": "P002", "product_name": "Polyester Blend",
             "units_sold": 380, "sale_price": 26600, "sale_date": "2026-03-15", "cost": 17500},
            {"id": 8,  "product_id": "P003", "product_name": "Silk Blend",
             "units_sold": 140, "sale_price": 21000, "sale_date": "2026-03-20", "cost": 13500},
            {"id": 9,  "product_id": "P001", "product_name": "Cotton Yarn",
             "units_sold": 550, "sale_price": 38500, "sale_date": "2026-04-08", "cost": 25000},
            {"id": 10, "product_id": "P004", "product_name": "Wool Blend",
             "units_sold": 220, "sale_price": 23100, "sale_date": "2026-04-18", "cost": 15000},
            {"id": 11, "product_id": "P005", "product_name": "Linen Yarn",
             "units_sold": 180, "sale_price": 15750, "sale_date": "2026-04-25", "cost": 10000},
            {"id": 12, "product_id": "P002", "product_name": "Polyester Blend",
             "units_sold": 410, "sale_price": 28700, "sale_date": "2026-05-10", "cost": 18500},
            {"id": 13, "product_id": "P001", "product_name": "Cotton Yarn",
             "units_sold": 600, "sale_price": 42000, "sale_date": "2026-05-20", "cost": 27000},
            {"id": 14, "product_id": "P003", "product_name": "Silk Blend",
             "units_sold": 150, "sale_price": 22500, "sale_date": "2026-05-28", "cost": 14500},
            {"id": 15, "product_id": "P001", "product_name": "Cotton Yarn",
             "units_sold": 640, "sale_price": 44800, "sale_date": "2026-06-05", "cost": 29000},
            {"id": 16, "product_id": "P004", "product_name": "Wool Blend",
             "units_sold": 240, "sale_price": 25200, "sale_date": "2026-06-15", "cost": 16500},
        ])
        print("  [OK] Seeded sales collection")

    # Notifications
    if db.notifications.count_documents({}) == 0:
        import time
        db.notifications.insert_many([
            {"id": 1, "type": "success", "title": "System Initialized",
             "message": "Production Monitoring System is running.",
             "timestamp": "09:00 AM", "read": True,
             "created_at": "2026-07-06T09:00:00Z"},
            {"id": 2, "type": "info", "title": "Maintenance Complete",
             "message": "Machine M001 has been serviced and is online.",
             "timestamp": "09:15 AM", "read": True,
             "created_at": "2026-07-06T09:15:00Z"},
            {"id": 3, "type": "warning", "title": "Low Stock Warning",
             "message": "Cotton Inventory is below the minimum threshold (15 bales remaining).",
             "timestamp": "10:30 AM", "read": False,
             "created_at": "2026-07-06T10:30:00Z"},
            {"id": 4, "type": "success", "title": "Production Target Met",
             "message": "Ring Frame M001 has completed its daily target of 320 units.",
             "timestamp": "02:45 PM", "read": False,
             "created_at": "2026-07-06T14:45:00Z"},
        ])
        print("  [OK] Seeded notifications collection")

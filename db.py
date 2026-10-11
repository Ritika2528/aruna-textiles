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

    # Suppliers
    if db.suppliers.count_documents({}) == 0:
        db.suppliers.insert_many([
            {"id": 1, "supplier_name": "Sri Textile Suppliers", "supplier_category": "Raw Material", "material_type": "Cotton", "contact_person": "Ramesh Kumar", "email_address": "ramesh@sritextile.com", "phone_number": "9876543211", "gst_id": "33AAAAA0000A1Z5", "payment_terms": "Net 30", "city": "Coimbatore", "created_at": "2026-01-10"},
            {"id": 2, "supplier_name": "Deccan Yarn Works", "supplier_category": "Yarn", "material_type": "Polyester", "contact_person": "Suresh Reddy", "email_address": "suresh@deccan.com", "phone_number": "9876543212", "gst_id": "36BBBBB0000B2Z6", "payment_terms": "Net 15", "city": "Hyderabad", "created_at": "2026-01-15"},
            {"id": 3, "supplier_name": "Bengal Cotton Co.", "supplier_category": "Raw Material", "material_type": "Cotton", "contact_person": "Mohan Das", "email_address": "mohan@bengal.com", "phone_number": "9876543213", "gst_id": "19CCCCC0000C3Z7", "payment_terms": "Net 30", "city": "Kolkata", "created_at": "2026-02-01"},
            {"id": 4, "supplier_name": "Surat Fabric Suppliers", "supplier_category": "Fabric", "material_type": "Silk", "contact_person": "Priya Shah", "email_address": "priya@surat.com", "phone_number": "9876543214", "gst_id": "24DDDDD0000D4Z8", "payment_terms": "Net 60", "city": "Surat", "created_at": "2026-02-10"},
            {"id": 5, "supplier_name": "Ludhiana Thread House", "supplier_category": "Yarn", "material_type": "Wool", "contact_person": "Harpal Singh", "email_address": "harpal@ludhiana.com", "phone_number": "9876543215", "gst_id": "03EEEEE0000E5Z9", "payment_terms": "Advance Payment", "city": "Ludhiana", "created_at": "2026-03-01"},
            {"id": 6, "supplier_name": "South India Fibers", "supplier_category": "Raw Material", "material_type": "Cotton", "contact_person": "Anand Kumar", "email_address": "anand@southfibers.com", "phone_number": "9876543216", "gst_id": "32FFFFF0000F6Z0", "payment_terms": "Net 30", "city": "Chennai", "created_at": "2026-03-15"}
        ])
        print("  [OK] Seeded suppliers collection")

    # Shipments
    if db.shipments.count_documents({}) == 0:
        db.shipments.insert_many([
            {"id": 1, "customer_name": "Rajesh Kumar", "company_name": "TechSpun Ltd", "product_name": "Cotton Yarn", "completed_batch": "BATCH-001", "batches_shipped": 2, "shipment_measurement": 500, "measurement_unit": "KG", "expiry_date": "2026-12-31", "created_at": "2026-03-16"},
            {"id": 2, "customer_name": "Priya Singh", "company_name": "TextiCorp Industries", "product_name": "Polyester Blend", "completed_batch": "BATCH-002", "batches_shipped": 3, "shipment_measurement": 750, "measurement_unit": "KG", "expiry_date": "2026-11-30", "created_at": "2026-03-17"},
            {"id": 3, "customer_name": "Anita Sharma", "company_name": "Deccan Textiles", "product_name": "Cotton Yarn", "completed_batch": "BATCH-003", "batches_shipped": 1, "shipment_measurement": 420, "measurement_unit": "KG", "expiry_date": "2027-01-15", "created_at": "2026-04-03"},
            {"id": 4, "customer_name": "Kavitha Nair", "company_name": "Kerala Fabrics Ltd", "product_name": "Linen Yarn", "completed_batch": "BATCH-004", "batches_shipped": 2, "shipment_measurement": 350, "measurement_unit": "KG", "expiry_date": "2027-02-28", "created_at": "2026-05-02"}
        ])
        print("  [OK] Seeded shipments collection")

    # Inventory (Cotton, Yarn, and Consumption)
    if db.inventory.count_documents({}) == 0:
        db.inventory.insert_many([
            {"category": "cotton", "id": "COT001", "type": "Raw Cotton Grade A", "stock": 1200, "minLevel": 400, "location": "Warehouse A", "status": "In Stock"},
            {"category": "cotton", "id": "COT002", "type": "Short Staple Cotton", "stock": 450, "minLevel": 500, "location": "Warehouse B", "status": "Low Stock"},
            {"category": "cotton", "id": "COT003", "type": "Egyptian Cotton", "stock": 800, "minLevel": 300, "location": "Warehouse A", "status": "In Stock"},
            {"category": "cotton", "id": "COT004", "type": "Organic Cotton", "stock": 250, "minLevel": 300, "location": "Warehouse C", "status": "Low Stock"},
            {"category": "yarn", "id": "YRN001", "type": "Cotton Yarn (30s Count)", "stock": 950, "minLevel": 400, "location": "Warehouse B", "status": "In Stock"},
            {"category": "yarn", "id": "YRN002", "type": "Polyester Blend Yarn", "stock": 620, "minLevel": 350, "location": "Warehouse A", "status": "In Stock"},
            {"category": "yarn", "id": "YRN003", "type": "Silk Blend Yarn", "stock": 180, "minLevel": 250, "location": "Warehouse C", "status": "Low Stock"},
            {"category": "yarn", "id": "YRN004", "type": "Linen Yarn (40s)", "stock": 310, "minLevel": 200, "location": "Warehouse B", "status": "In Stock"},
            {"category": "consumption", "date": "2026-06-28", "material": "Cotton", "type": "Raw Cotton Grade A", "consumed": 120, "machine": "M001"},
            {"category": "consumption", "date": "2026-06-29", "material": "Cotton", "type": "Short Staple Cotton", "consumed": 95, "machine": "M002"},
            {"category": "consumption", "date": "2026-06-30", "material": "Yarn", "type": "Cotton Yarn (20s)", "consumed": 200, "machine": "M003"},
            {"category": "consumption", "date": "2026-07-01", "material": "Cotton", "type": "Egyptian Cotton", "consumed": 60, "machine": "M001"},
            {"category": "consumption", "date": "2026-07-01", "material": "Yarn", "type": "Polyester Blend", "consumed": 180, "machine": "M004"},
            {"category": "consumption", "date": "2026-07-02", "material": "Cotton", "type": "Organic Cotton", "consumed": 75, "machine": "M002"}
        ])
        print("  [OK] Seeded inventory collection")

    # Transactions
    if db.transactions.count_documents({}) == 0:
        db.transactions.insert_many([
            {"id": 1, "txn_id": "TXN-001", "customer_name": "Rajesh Kumar", "customer_id": "CUST001", "material": "Cotton", "yarn_type": "Combed", "quality": "Grade A", "quantity_meters": 5000, "yarn_weight_kg": 650, "new_stock": 2400, "amount": 85000, "recorded_by": "Shift Incharge", "datetime": "2026-09-01T10:30:00", "remarks": "First batch of September"},
            {"id": 2, "txn_id": "TXN-002", "customer_name": "Priya Singh", "customer_id": "CUST002", "material": "Polyester", "yarn_type": "Carded", "quality": "Standard", "quantity_meters": 3500, "yarn_weight_kg": 480, "new_stock": 1920, "amount": 54000, "recorded_by": "Floor Supervisor", "datetime": "2026-09-01T14:15:00", "remarks": "Urgent order dispatch"},
            {"id": 3, "txn_id": "TXN-003", "customer_name": "Vikram Patel", "customer_id": "CUST003", "material": "Silk Blend", "yarn_type": "Compact", "quality": "Premium", "quantity_meters": 2000, "yarn_weight_kg": 290, "new_stock": 1630, "amount": 92000, "recorded_by": "Quality Manager", "datetime": "2026-09-02T09:45:00", "remarks": "Export quality inspected"},
            {"id": 4, "txn_id": "TXN-004", "customer_name": "Ananya Roy", "customer_id": "CUST004", "material": "Viscose", "yarn_type": "Rotor", "quality": "Standard", "quantity_meters": 4200, "yarn_weight_kg": 540, "new_stock": 1090, "amount": 47500, "recorded_by": "Store Officer", "datetime": "2026-09-02T16:00:00", "remarks": "Partial delivery completed"},
            {"id": 5, "txn_id": "TXN-005", "customer_name": "Suresh Reddy", "customer_id": "CUST005", "material": "Wool Blend", "yarn_type": "Combed", "quality": "Grade A", "quantity_meters": 1800, "yarn_weight_kg": 310, "new_stock": 780, "amount": 76000, "recorded_by": "Shift Incharge", "datetime": "2026-09-03T11:20:00", "remarks": "Winter collection supply"},
            {"id": 6, "txn_id": "TXN-006", "customer_name": "Anita Sharma", "customer_id": "CUST006", "material": "Linen", "yarn_type": "Carded", "quality": "Standard", "quantity_meters": 3000, "yarn_weight_kg": 450, "new_stock": 1800, "amount": 62000, "recorded_by": "Accountant", "datetime": "2026-09-04T08:30:00", "remarks": "Monthly bulk order"}
        ])
        print("  [OK] Seeded transactions collection")

    # Workforce
    if db.workforce.count_documents({}) == 0:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        shifts_pattern = ["A", "B", "A", "B", "A", "OFF"]
        operators = [
            {"id": "OP001", "name": "Ramesh Kumar", "role": "Senior Operator", "dept": "Spinning", "shift": "A", "skill": "Ring Frame", "status": "Active", "efficiency": 94, "target": 350, "phone": "+91 98765 43210"},
            {"id": "OP002", "name": "Suresh Patil", "role": "Machine Tech", "dept": "Carding", "shift": "A", "skill": "Carding", "status": "Active", "efficiency": 88, "target": 300, "phone": "+91 98765 43211"},
            {"id": "OP003", "name": "Anil Verma", "role": "Operator", "dept": "Roving", "shift": "B", "skill": "Roving Frame", "status": "Active", "efficiency": 91, "target": 280, "phone": "+91 98765 43212"},
            {"id": "OP004", "name": "Dinesh Shah", "role": "Junior Tech", "dept": "Winding", "shift": "B", "skill": "Auto Coner", "status": "On Leave", "efficiency": 79, "target": 260, "phone": "+91 98765 43213"},
            {"id": "OP005", "name": "Mohan Lal", "role": "Master Spinner", "dept": "Spinning", "shift": "A", "skill": "Ring Frame", "status": "Active", "efficiency": 96, "target": 380, "phone": "+91 98765 43214"},
            {"id": "OP006", "name": "Prakash Rao", "role": "Operator", "dept": "Drawing", "shift": "C", "skill": "Draw Frame", "status": "Active", "efficiency": 85, "target": 290, "phone": "+91 98765 43215"},
            {"id": "OP007", "name": "Vijay Nair", "role": "Maintenance Tech", "dept": "Maintenance", "shift": "General", "skill": "All Machines", "status": "Active", "efficiency": 92, "target": 200, "phone": "+91 98765 43216"},
            {"id": "OP008", "name": "Kiran Joshi", "role": "Junior Operator", "dept": "Carding", "shift": "C", "skill": "Carding", "status": "Active", "efficiency": 83, "target": 270, "phone": "+91 98765 43217"}
        ]
        attendance = [
            {"opId": "OP001", "date": "Today", "checkin": "06:03", "status": "Present"},
            {"opId": "OP002", "date": "Today", "checkin": "06:12", "status": "Present"},
            {"opId": "OP003", "date": "Today", "checkin": "—", "status": "Absent"},
            {"opId": "OP004", "date": "Today", "checkin": "—", "status": "Leave"},
            {"opId": "OP005", "date": "Today", "checkin": "06:00", "status": "Present"},
            {"opId": "OP006", "date": "Today", "checkin": "14:05", "status": "Present"},
            {"opId": "OP007", "date": "Today", "checkin": "06:45", "status": "Half Day"},
            {"opId": "OP008", "date": "Today", "checkin": "14:10", "status": "Present"}
        ]
        shifts = []
        for i, op in enumerate(operators):
            sched = {day: shifts_pattern[(i + di) % len(shifts_pattern)] for di, day in enumerate(days)}
            shifts.append({"opId": op["id"], "schedule": sched})

        db.workforce.insert_one({
            "type": "master_workforce",
            "operators": operators,
            "attendance": attendance,
            "shifts": shifts
        })
        print("  [OK] Seeded workforce collection")

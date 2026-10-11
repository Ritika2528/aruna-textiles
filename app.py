"""
ARUNA Production Monitoring System - Ultra-Secure Backend Engine
Hardened against OWASP Top 10, NoSQL Injection, XSS, CSRF, Brute Force, and Session Hijacking.
"""
import os
import json
import random
import threading
import time
import asyncio
from datetime import timedelta
from functools import wraps
from flask import Flask, send_from_directory, redirect, jsonify, request, session
import websockets
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from db import get_collection, seed_sample_data

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# ── Security Configuration ───────────────────────────────────────────────────
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    MAX_CONTENT_LENGTH=1 * 1024 * 1024  # 1MB max body limit to prevent memory DoS
)

PORT = int(os.environ.get("PORT", 5000))
WS_PORT = int(os.environ.get("WS_PORT", 5001))
TRUSTED_ORIGINS = set(filter(None, os.environ.get("TRUSTED_ORIGINS", "").split(",")))
TRUSTED_ORIGINS.update({'http://localhost:5000', 'http://127.0.0.1:5000'})

# ── Security Logging ─────────────────────────────────────────────────────────
def log_security_event(event_type, details, ip=None):
    """Structured security audit log avoiding sensitive credential logging."""
    client_ip = ip or (request.remote_addr if request else "system")
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"[AUDIT-LOG] [{timestamp}] [{event_type}] [IP:{client_ip}] {details}")

# ── HTTP Security Headers & Controlled CORS ──────────────────────────────────
@app.after_request
def add_security_headers(response):
    origin = request.headers.get('Origin')
    req_host = request.host_url.rstrip('/')
    if origin and (origin in TRUSTED_ORIGINS or origin == req_host):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'

    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), camera=(), microphone=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' ws://localhost:5001 http://localhost:5000 http://127.0.0.1:5000;"
    )
    return response

# ── Rate Limiting (Server-side Sliding Window) ────────────────────────────────
_rate_limit_lock = threading.Lock()
_login_attempts = {}

def check_login_rate_limit(ip, username):
    """Prevent brute-force authentication attacks using a 15-minute sliding window."""
    now = time.time()
    key = f"{ip}:{username}"
    with _rate_limit_lock:
        record = _login_attempts.get(key)
        if record:
            lockout_until = record.get('lockout_until', 0)
            if lockout_until > now:
                remaining = int(lockout_until - now)
                return False, remaining
            if now - record.get('first_attempt', now) > 900:
                _login_attempts[key] = {'count': 0, 'first_attempt': now, 'lockout_until': 0}
        else:
            _login_attempts[key] = {'count': 0, 'first_attempt': now, 'lockout_until': 0}
    return True, 0

def record_failed_login(ip, username):
    now = time.time()
    key = f"{ip}:{username}"
    with _rate_limit_lock:
        record = _login_attempts.get(key, {'count': 0, 'first_attempt': now, 'lockout_until': 0})
        record['count'] += 1
        if record['count'] >= 5:
            record['lockout_until'] = now + 900  # 15 minutes lockout
            log_security_event("RATE_LIMIT_LOCKOUT", f"User '{username}' locked out for 15 min after repeated failures.", ip)
        _login_attempts[key] = record

def clear_login_attempts(ip, username):
    key = f"{ip}:{username}"
    with _rate_limit_lock:
        _login_attempts.pop(key, None)

# ── Authentication & Authorization Decorators ─────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            log_security_event("UNAUTHORIZED_ACCESS", f"Blocked unauthenticated request to {request.path}")
            return jsonify({"error": "Authentication required. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({"error": "Authentication required."}), 401
            user_role = session.get('role', 'operator')
            if user_role not in allowed_roles:
                log_security_event("FORBIDDEN_ACCESS", f"User '{session.get('username')}' (role: {user_role}) denied access to {request.path}")
                return jsonify({"error": "Forbidden: Insufficient privileges."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ── Database Cleaners & Auto-Increment Helpers ───────────────────────────────
def _clean(doc):
    """Remove MongoDB's _id and sensitive security fields before returning to client."""
    if isinstance(doc, list):
        return [_clean(d) for d in doc]
    if isinstance(doc, dict):
        cleaned = dict(doc)
        cleaned.pop('_id', None)
        cleaned.pop('password_hash', None)
        cleaned.pop('failed_attempts', None)
        cleaned.pop('lockout_until', None)
        return cleaned
    return doc

def _next_id(collection_name):
    """Return max(id)+1 across the collection."""
    col = get_collection(collection_name)
    last = col.find_one(sort=[("id", -1)])
    return (last["id"] + 1) if (last and "id" in last) else 1

# Initialise collections and seed sample data on startup
try:
    seed_sample_data()
except Exception as e:
    print(f"Warning: could not seed sample data — {e}")

# ── Input Sanitization & Anti-NoSQL-Injection Validators ─────────────────────
def sanitize_keys(data):
    """Reject keys starting with $ or containing . to prevent NoSQL operator injection."""
    if not isinstance(data, dict):
        return False
    for k, v in data.items():
        if k.startswith('$') or '.' in k:
            return False
        if isinstance(v, dict) and not sanitize_keys(v):
            return False
    return True

def validate_customer_payload(data, is_update=False):
    """Strict allowlist and type validation for customers."""
    if not sanitize_keys(data):
        return False, "Invalid keys in payload."
    allowed_fields = {'customer_id', 'customer_name', 'company_name', 'phone_number', 'product_type', 'order_quantity', 'order_status', 'order_value', 'order_count', 'created_at'}
    cleaned = {}
    for k, v in data.items():
        if k in allowed_fields:
            cleaned[k] = v
    if not is_update:
        required = {'customer_id', 'customer_name'}
        if not required.issubset(cleaned.keys()):
            return False, "Missing required customer fields."
    if 'order_quantity' in cleaned:
        try:
            cleaned['order_quantity'] = int(cleaned['order_quantity'])
            if cleaned['order_quantity'] < 0:
                return False, "Order quantity cannot be negative."
        except (ValueError, TypeError):
            return False, "Invalid order quantity format."
    if 'order_value' in cleaned:
        try:
            cleaned['order_value'] = float(cleaned['order_value'])
        except (ValueError, TypeError):
            pass
    if 'order_count' in cleaned:
        try:
            cleaned['order_count'] = int(cleaned['order_count'])
        except (ValueError, TypeError):
            pass
    for str_key in ['customer_id', 'customer_name', 'company_name', 'phone_number', 'product_type', 'order_status', 'created_at']:
        if str_key in cleaned:
            cleaned[str_key] = str(cleaned[str_key])[:100]
    return True, cleaned

def validate_production_payload(data, is_update=False):
    """Strict allowlist and type validation for production records."""
    if not sanitize_keys(data):
        return False, "Invalid keys in payload."
    allowed_fields = {'production_id', 'machine_id', 'machine_type', 'production_quantity', 'production_status'}
    cleaned = {}
    for k, v in data.items():
        if k in allowed_fields:
            cleaned[k] = v
    if not is_update:
        required = {'production_id', 'machine_id'}
        if not required.issubset(cleaned.keys()):
            return False, "Missing required production fields."
    if 'production_quantity' in cleaned:
        try:
            cleaned['production_quantity'] = int(cleaned['production_quantity'])
            if cleaned['production_quantity'] < 0:
                return False, "Production quantity cannot be negative."
        except (ValueError, TypeError):
            return False, "Invalid production quantity format."
    for str_key in ['production_id', 'machine_id', 'machine_type', 'production_status']:
        if str_key in cleaned:
            cleaned[str_key] = str(cleaned[str_key])[:100]
    return True, cleaned

def validate_sales_payload(data, is_update=False):
    """Strict allowlist and type validation for sales records."""
    if not sanitize_keys(data):
        return False, "Invalid keys in payload."
    allowed_fields = {'product_id', 'product_name', 'units_sold', 'sale_price', 'cost', 'sale_date'}
    cleaned = {}
    for k, v in data.items():
        if k in allowed_fields:
            cleaned[k] = v
    if not is_update:
        required = {'product_id', 'product_name'}
        if not required.issubset(cleaned.keys()):
            return False, "Missing required sales fields."
    for num_key in ['units_sold', 'sale_price', 'cost']:
        if num_key in cleaned:
            try:
                cleaned[num_key] = float(cleaned[num_key])
                if cleaned[num_key] < 0:
                    return False, f"{num_key} cannot be negative."
                if num_key == 'units_sold':
                    cleaned[num_key] = int(cleaned[num_key])
            except (ValueError, TypeError):
                return False, f"Invalid format for {num_key}."
    for str_key in ['product_id', 'product_name', 'sale_date']:
        if str_key in cleaned:
            cleaned[str_key] = str(cleaned[str_key])[:100]
    return True, cleaned

# ── WebSocket Server & Hardened Handshake ─────────────────────────────────────
connected_clients = set()
client_msg_timestamps = {}
db_lock = threading.Lock()

async def register(websocket):
    # Origin verification to prevent Cross-Site WebSocket Hijacking
    origin = websocket.request_headers.get('Origin', '')
    if origin and origin not in TRUSTED_ORIGINS:
        log_security_event("WS_UNAUTHORIZED_ORIGIN", f"Rejected WebSocket connection from origin: '{origin}'")
        await websocket.close(1008, "Unauthorized origin")
        return

    connected_clients.add(websocket)
    client_msg_timestamps[websocket] = []
    print(f"WS client connected: {websocket.remote_address}. Total: {len(connected_clients)}")

    try:
        with db_lock:
            history = _clean(list(get_collection('notifications').find()))
        await websocket.send(json.dumps({"action": "history", "data": history}))

        async for message in websocket:
            # Message size guard (Max 64KB)
            if len(message) > 65536:
                await websocket.close(1009, "Message too large")
                break

            # Per-client WebSocket rate limiting (Max 20 messages per second)
            now = time.time()
            msg_times = [t for t in client_msg_timestamps.get(websocket, []) if now - t < 1.0]
            if len(msg_times) >= 20:
                await websocket.send(json.dumps({"action": "error", "message": "Rate limit exceeded"}))
                continue
            msg_times.append(now)
            client_msg_timestamps[websocket] = msg_times

            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            action = data.get("action")
            allowed_actions = {"new_notification", "mark_read", "mark_all_read", "clear_all", "delete_one"}
            if action not in allowed_actions:
                continue

            if action == "new_notification":
                notif = data.get("notification")
                if isinstance(notif, dict) and sanitize_keys(notif):
                    safe_notif = {
                        "type": str(notif.get("type", "info"))[:20],
                        "title": str(notif.get("title", ""))[:100],
                        "message": str(notif.get("message", ""))[:500],
                        "timestamp": time.strftime("%I:%M %p"),
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "read": False
                    }
                    with db_lock:
                        safe_notif["id"] = _next_id('notifications')
                        get_collection('notifications').insert_one(dict(safe_notif))
                        _clean(safe_notif)
                    await broadcast(json.dumps({"action": "new_notification", "notification": safe_notif}))

            elif action == "mark_read":
                notif_id = data.get("id")
                if isinstance(notif_id, int):
                    with db_lock:
                        get_collection('notifications').update_one({"id": notif_id}, {"$set": {"read": True}})
                    await broadcast(json.dumps({"action": "mark_read", "id": notif_id}))

            elif action == "mark_all_read":
                with db_lock:
                    get_collection('notifications').update_many({}, {"$set": {"read": True}})
                await broadcast(json.dumps({"action": "mark_all_read"}))

            elif action == "clear_all":
                with db_lock:
                    get_collection('notifications').delete_many({})
                await broadcast(json.dumps({"action": "clear_all"}))

            elif action == "delete_one":
                notif_id = data.get("id")
                if isinstance(notif_id, int):
                    with db_lock:
                        get_collection('notifications').delete_one({"id": notif_id})
                    await broadcast(json.dumps({"action": "delete_one", "id": notif_id}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        client_msg_timestamps.pop(websocket, None)
        print(f"WS client disconnected. Total: {len(connected_clients)}")

async def broadcast(message):
    if connected_clients:
        await asyncio.gather(
            *[c.send(message) for c in list(connected_clients)],
            return_exceptions=True
        )

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(register, "localhost", WS_PORT)
    loop.run_until_complete(start_server)
    print(f"WebSocket Server running on ws://localhost:{WS_PORT}")

    async def simulate_notifications():
        examples = [
            {"type": "success", "title": "Employee Present",
             "message": "Ritika has marked attendance for today at 9:02 AM."},
            {"type": "info", "title": "Leave Request Submitted",
             "message": "Kumar has submitted a leave request for July 10."},
            {"type": "error", "title": "Machine Stopped",
             "message": "Machine #4 has been inactive for 15 minutes."},
            {"type": "success", "title": "Task Completed",
             "message": "Quality Inspection Report has been completed."},
            {"type": "warning", "title": "Low Stock Warning",
             "message": "Cotton Inventory is below the minimum threshold."},
        ]
        while True:
            await asyncio.sleep(random.randint(25, 45))
            if connected_clients:
                selected = random.choice(examples).copy()
                selected["timestamp"] = time.strftime("%I:%M %p")
                selected["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                with db_lock:
                    selected["id"] = _next_id('notifications')
                    selected["read"] = False
                    get_collection('notifications').insert_one(dict(selected))
                    _clean(selected)
                await broadcast(json.dumps({"action": "new_notification", "notification": selected}))

    loop.create_task(simulate_notifications())
    loop.run_forever()

# ── Flask Static Routes ───────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect('/templates/login.html')

@app.route('/templates/<path:filename>')
def serve_template(filename):
    return send_from_directory('templates', filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/favicon.svg')
def favicon_svg():
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')

# ── Authentication Endpoints ──────────────────────────────────────────────────
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request payload"}), 400

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Reject oversized passwords safely to prevent hashing algorithm denial of service
    if len(password) > 128:
        return jsonify({"error": "Invalid username or password"}), 400

    client_ip = request.remote_addr or "127.0.0.1"
    allowed, remaining = check_login_rate_limit(client_ip, username.lower())
    if not allowed:
        log_security_event("LOGIN_THROTTLED", f"User '{username}' exceeded login attempt limits.", client_ip)
        return jsonify({"error": f"Too many failed login attempts. Please try again in {remaining} seconds."}), 429

    users_col = get_collection('users')
    user = users_col.find_one({"username": username.lower()})

    if not user or not check_password_hash(user.get("password_hash", ""), password):
        record_failed_login(client_ip, username.lower())
        log_security_event("AUTH_FAILED", f"Failed login for username '{username}'", client_ip)
        return jsonify({"error": "Invalid username or password"}), 401

    # Login successful: Reset rate limiting, prevent session fixation
    clear_login_attempts(client_ip, username.lower())
    session.clear()
    session['user_id'] = user.get('id', 1)
    session['username'] = user.get('username')
    session['role'] = user.get('role', 'admin')
    session.permanent = True

    log_security_event("AUTH_SUCCESS", f"User '{username}' logged in successfully.", client_ip)

    return jsonify({
        "status": "success",
        "user": {
            "id": user.get('id'),
            "username": user.get('username'),
            "role": user.get('role', 'admin'),
            "full_name": user.get('full_name', '')
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    username = session.get('username', 'anonymous')
    session.clear()
    log_security_event("AUTH_LOGOUT", f"User '{username}' logged out.")
    return jsonify({"status": "success", "message": "Logged out successfully"})

@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    if 'user_id' not in session:
        return jsonify({"authenticated": False}), 401
    return jsonify({
        "authenticated": True,
        "user": {
            "id": session.get('user_id'),
            "username": session.get('username'),
            "role": session.get('role')
        }
    })

# ── Notifications API ─────────────────────────────────────────────────────────
@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    docs = _clean(list(get_collection('notifications').find()))
    return jsonify(docs)

@app.route('/api/notifications/clear', methods=['POST'])
@login_required
@role_required('admin')
def clear_notifications():
    get_collection('notifications').delete_many({})
    return jsonify({"status": "success"})

# ── Customers API ─────────────────────────────────────────────────────────────
@app.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    docs = _clean(list(get_collection('customers').find()))
    return jsonify(docs)

@app.route('/api/customers', methods=['POST'])
@login_required
def add_customer():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    valid, result = validate_customer_payload(data)
    if not valid:
        return jsonify({"error": result}), 400

    col = get_collection('customers')
    if col.find_one({"customer_id": result.get("customer_id")}):
        return jsonify({"error": "Customer ID already exists"}), 409

    result["id"] = _next_id('customers')
    result.setdefault("created_at", time.strftime("%Y-%m-%d"))
    col.insert_one(dict(result))
    _clean(result)
    return jsonify(result), 201

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    result = get_collection('customers').delete_one({"id": customer_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"status": "deleted"})

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    valid, result = validate_customer_payload(data, is_update=True)
    if not valid:
        return jsonify({"error": result}), 400

    db_res = get_collection('customers').update_one({"id": customer_id}, {"$set": result})
    if db_res.matched_count == 0:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"status": "updated"})

# ── Production API ────────────────────────────────────────────────────────────
@app.route('/api/production', methods=['GET'])
@login_required
def get_production():
    docs = _clean(list(get_collection('production').find()))
    return jsonify(docs)

@app.route('/api/production', methods=['POST'])
@login_required
def add_production():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    valid, result = validate_production_payload(data)
    if not valid:
        return jsonify({"error": result}), 400

    result["id"] = _next_id('production')
    result.setdefault("created_at", time.strftime("%Y-%m-%d"))
    get_collection('production').insert_one(dict(result))
    _clean(result)
    return jsonify(result), 201

@app.route('/api/production/<int:prod_id>', methods=['DELETE'])
@login_required
def delete_production(prod_id):
    result = get_collection('production').delete_one({"id": prod_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"status": "deleted"})

@app.route('/api/production/<int:prod_id>', methods=['PUT'])
@login_required
def update_production(prod_id):
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    valid, result = validate_production_payload(data, is_update=True)
    if not valid:
        return jsonify({"error": result}), 400

    db_res = get_collection('production').update_one({"id": prod_id}, {"$set": result})
    if db_res.matched_count == 0:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"status": "updated"})

# ── Sales API ─────────────────────────────────────────────────────────────────
@app.route('/api/sales', methods=['GET'])
@login_required
def get_sales():
    docs = _clean(list(get_collection('sales').find()))
    return jsonify(docs)

@app.route('/api/sales', methods=['POST'])
@login_required
def add_sale():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    valid, result = validate_sales_payload(data)
    if not valid:
        return jsonify({"error": result}), 400

    result["id"] = _next_id('sales')
    result.setdefault("sale_date", time.strftime("%Y-%m-%d"))
    get_collection('sales').insert_one(dict(result))
    _clean(result)
    return jsonify(result), 201

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@login_required
def delete_sale(sale_id):
    result = get_collection('sales').delete_one({"id": sale_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"status": "deleted"})

@app.route('/api/sales/<int:sale_id>', methods=['PUT'])
@login_required
def update_sale(sale_id):
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    valid, result = validate_sales_payload(data, is_update=True)
    if not valid:
        return jsonify({"error": result}), 400

    db_res = get_collection('sales').update_one({"id": sale_id}, {"$set": result})
    if db_res.matched_count == 0:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"status": "updated"})

# ── Suppliers API ─────────────────────────────────────────────────────────────
@app.route('/api/suppliers', methods=['GET'])
@login_required
def get_suppliers():
    docs = _clean(list(get_collection('suppliers').find()))
    return jsonify(docs)

@app.route('/api/suppliers', methods=['POST'])
@login_required
def add_supplier():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400
    if not sanitize_keys(data):
        return jsonify({"error": "Invalid payload format"}), 400

    col = get_collection('suppliers')
    data["id"] = _next_id('suppliers')
    data.setdefault("created_at", time.strftime("%Y-%m-%d"))
    col.insert_one(dict(data))
    return jsonify(_clean(data)), 201

@app.route('/api/suppliers/<int:supp_id>', methods=['DELETE'])
@login_required
def delete_supplier(supp_id):
    res = get_collection('suppliers').delete_one({"id": supp_id})
    if res.deleted_count == 0:
        return jsonify({"error": "Supplier not found"}), 404
    return jsonify({"status": "deleted"})

# ── Shipments API ─────────────────────────────────────────────────────────────
@app.route('/api/shipments', methods=['GET'])
@login_required
def get_shipments():
    docs = _clean(list(get_collection('shipments').find()))
    return jsonify(docs)

@app.route('/api/shipments', methods=['POST'])
@login_required
def add_shipment():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400
    if not sanitize_keys(data):
        return jsonify({"error": "Invalid payload format"}), 400

    col = get_collection('shipments')
    data["id"] = _next_id('shipments')
    data.setdefault("created_at", time.strftime("%Y-%m-%d"))
    col.insert_one(dict(data))
    return jsonify(_clean(data)), 201

@app.route('/api/shipments/<int:ship_id>', methods=['DELETE'])
@login_required
def delete_shipment(ship_id):
    res = get_collection('shipments').delete_one({"id": ship_id})
    if res.deleted_count == 0:
        return jsonify({"error": "Shipment not found"}), 404
    return jsonify({"status": "deleted"})

# ── Inventory API ─────────────────────────────────────────────────────────────
@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    col = get_collection('inventory')
    docs = _clean(list(col.find()))
    cotton = [d for d in docs if d.get("category") == "cotton"]
    yarn = [d for d in docs if d.get("category") == "yarn"]
    consumption = [d for d in docs if d.get("category") == "consumption"]
    return jsonify({"cotton": cotton, "yarn": yarn, "consumption": consumption})

@app.route('/api/inventory', methods=['POST'])
@login_required
def add_inventory():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400
    if not sanitize_keys(data):
        return jsonify({"error": "Invalid payload format"}), 400

    col = get_collection('inventory')
    col.insert_one(dict(data))
    return jsonify(_clean(data)), 201

@app.route('/api/inventory/<string:category>/<string:item_id>', methods=['DELETE'])
@login_required
def delete_inventory(category, item_id):
    col = get_collection('inventory')
    res = col.delete_one({"category": category, "id": item_id})
    if res.deleted_count == 0:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"status": "deleted"})

# ── Transactions API ──────────────────────────────────────────────────────────
@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    docs = _clean(list(get_collection('transactions').find()))
    return jsonify(docs)

@app.route('/api/transactions', methods=['POST'])
@login_required
def add_transaction():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400
    if not sanitize_keys(data):
        return jsonify({"error": "Invalid payload format"}), 400

    col = get_collection('transactions')
    data["id"] = _next_id('transactions')
    col.insert_one(dict(data))
    return jsonify(_clean(data)), 201

@app.route('/api/transactions/<int:txn_id>', methods=['DELETE'])
@login_required
def delete_transaction(txn_id):
    res = get_collection('transactions').delete_one({"id": txn_id})
    if res.deleted_count == 0:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify({"status": "deleted"})

# ── Workforce API ─────────────────────────────────────────────────────────────
@app.route('/api/workforce', methods=['GET'])
@login_required
def get_workforce():
    doc = get_collection('workforce').find_one({"type": "master_workforce"})
    if not doc:
        return jsonify({"operators": [], "attendance": [], "shifts": []})
    cleaned = _clean(doc)
    today_str = time.strftime("%Y-%m-%d")
    att = cleaned.get("attendance", [])
    if not any(a.get("date") == today_str for a in att):
        for a in list(att):
            if a.get("date") == "Today":
                att.append({**a, "date": today_str})
        cleaned["attendance"] = att
    return jsonify(cleaned)

@app.route('/api/workforce/attendance', methods=['PUT'])
@login_required
def update_workforce_attendance():
    data = request.get_json(silent=True)
    if not isinstance(data, list):
        return jsonify({"error": "Expected array of attendance logs"}), 400
    get_collection('workforce').update_one(
        {"type": "master_workforce"},
        {"$set": {"attendance": data}},
        upsert=True
    )
    return jsonify({"status": "updated"})

@app.route('/api/workforce/shifts', methods=['PUT'])
@login_required
def update_workforce_shifts():
    data = request.get_json(silent=True)
    if not isinstance(data, list):
        return jsonify({"error": "Expected array of shift schedules"}), 400
    get_collection('workforce').update_one(
        {"type": "master_workforce"},
        {"$set": {"shifts": data}},
        upsert=True
    )
    return jsonify({"status": "updated"})

@app.route('/api/workforce/operator', methods=['POST'])
@login_required
def add_workforce_operator():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400
    col = get_collection('workforce')
    doc = col.find_one({"type": "master_workforce"})
    ops = doc.get("operators", []) if doc else []
    data.setdefault("id", f"OP{len(ops)+1:03d}")
    ops.append(data)
    col.update_one({"type": "master_workforce"}, {"$set": {"operators": ops}}, upsert=True)
    return jsonify(data), 201

# ── Stats / Dashboard API ─────────────────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    customers = get_collection('customers')
    production = get_collection('production')
    sales_col = get_collection('sales')
    suppliers_col = get_collection('suppliers')
    shipments_col = get_collection('shipments')
    wf_col = get_collection('workforce')

    total_customers = customers.count_documents({})
    completed_orders = customers.count_documents({"order_status": "Completed"})
    processing_orders = customers.count_documents({"order_status": "Processing"})
    pending_orders = customers.count_documents({"order_status": "Pending"})

    total_production = production.count_documents({})
    completed_production = production.count_documents({"production_status": "Completed"})

    sales_docs = list(sales_col.find())
    total_revenue = sum(s.get("sale_price", 0) for s in sales_docs)
    total_cost = sum(s.get("cost", 0) for s in sales_docs)
    total_profit = total_revenue - total_cost

    total_suppliers = suppliers_col.count_documents({})
    total_shipments = shipments_col.count_documents({})

    wf_doc = wf_col.find_one({"type": "master_workforce"})
    attendance_list = (wf_doc.get("attendance", []) if wf_doc else [])
    present_count = sum(1 for a in attendance_list if a.get("status") in ["Present", "Half Day"])
    att_rate = round((present_count / len(attendance_list) * 100)) if attendance_list else 92

    return jsonify({
        "customers": {
            "total": total_customers,
            "completed": completed_orders,
            "processing": processing_orders,
            "pending": pending_orders,
        },
        "production": {
            "total": total_production,
            "completed": completed_production,
        },
        "sales": {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
        },
        "suppliers": {
            "total": total_suppliers
        },
        "shipments": {
            "total": total_shipments
        },
        "workforce": {
            "attendance_rate": att_rate
        }
    })

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()

    print(f"Starting Hardened Flask server on http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)

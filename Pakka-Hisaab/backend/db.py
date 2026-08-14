"""SQLite schema, deterministic seed data, and read models."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "pakkahisaab.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY, sku TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
  category TEXT NOT NULL, price INTEGER NOT NULL CHECK(price >= 0), stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0)
);
CREATE TABLE IF NOT EXISTS carts (
  id INTEGER PRIMARY KEY, status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cart_items (
  id INTEGER PRIMARY KEY, cart_id INTEGER NOT NULL REFERENCES carts(id), product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL CHECK(quantity > 0), unit_price INTEGER NOT NULL CHECK(unit_price >= 0), UNIQUE(cart_id, product_id)
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, cart_id INTEGER NOT NULL REFERENCES carts(id), total_amount INTEGER NOT NULL,
  status TEXT NOT NULL, payment_method TEXT NOT NULL, created_at TEXT NOT NULL, paid_at TEXT
);
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL REFERENCES orders(id), provider TEXT NOT NULL,
  amount INTEGER NOT NULL, status TEXT NOT NULL, demo_reference TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL, confirmed_at TEXT
);
CREATE TABLE IF NOT EXISTS transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL REFERENCES orders(id), type TEXT NOT NULL,
  status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id INTEGER,
  message TEXT NOT NULL, timestamp TEXT NOT NULL
);
"""


PRODUCTS = [
    (1, "BRIT-001", "Britannia Biscuits", "Grocery", 127, 100),
    (2, "SOAP-001", "Soap", "Personal Care", 45, 50),
    (3, "MILK-001", "Milk", "Dairy", 60, 80),
    (4, "RICE-001", "Rice", "Grocery", 72, 120),
    (5, "TEA-001", "Tea", "Grocery", 140, 65),
    (6, "SUGAR-001", "Sugar", "Grocery", 48, 90),
    (7, "BREAD-001", "Bread", "Bakery", 40, 45),
    (8, "SHAMP-001", "Shampoo", "Personal Care", 210, 30),
    (9, "TOOTH-001", "Toothpaste", "Personal Care", 96, 40),
    (10, "OIL-001", "Cooking Oil", "Grocery", 165, 55),
]


def seed(connection: sqlite3.Connection) -> None:
    now = utc_now()
    connection.executescript(SCHEMA)
    connection.execute("DELETE FROM audit_log")
    connection.execute("DELETE FROM transactions")
    connection.execute("DELETE FROM payments")
    connection.execute("DELETE FROM orders")
    connection.execute("DELETE FROM cart_items")
    connection.execute("DELETE FROM carts")
    connection.execute("DELETE FROM products")
    connection.executemany("INSERT INTO products(id, sku, name, category, price, stock_quantity) VALUES (?, ?, ?, ?, ?, ?)", PRODUCTS)
    carts = [(i, "OPEN", now, now) for i in range(1, 6)]
    connection.executemany("INSERT INTO carts(id, status, created_at, updated_at) VALUES (?, ?, ?, ?)", carts)
    # Every cart uses the current product price from SQLite. Cart 1 stays ₹299.
    items = [
        (1, 1, 2, 127), (1, 2, 1, 45),
        (2, 1, 1, 127), (2, 2, 2, 45),
        (3, 3, 2, 60), (3, 7, 1, 40), (3, 2, 1, 45),
        (4, 5, 1, 140), (4, 6, 1, 48),
        (5, 8, 1, 210), (5, 9, 1, 96), (5, 2, 1, 45), (5, 7, 1, 40),
    ]
    connection.executemany("INSERT INTO cart_items(cart_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)", items)
    connection.execute("INSERT INTO audit_log(event_type, entity_type, entity_id, message, timestamp) VALUES (?, ?, ?, ?, ?)", ("DEMO_RESET", "SYSTEM", None, "Deterministic demo data seeded", now))
    connection.commit()


def ensure_database(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    connection = connect(db_path)
    connection.executescript(SCHEMA)
    if connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        seed(connection)
    return connection


def money(value: int) -> str:
    return f"₹{value:,}"


def cart_view(connection: sqlite3.Connection, cart_id: int) -> dict | None:
    cart = connection.execute("SELECT * FROM carts WHERE id = ?", (cart_id,)).fetchone()
    if not cart:
        return None
    rows = connection.execute(
        """SELECT ci.product_id, p.name, ci.quantity, ci.unit_price, ci.quantity * ci.unit_price AS line_total
           FROM cart_items ci JOIN products p ON p.id = ci.product_id WHERE ci.cart_id = ? ORDER BY ci.id""", (cart_id,)
    ).fetchall()
    total = sum(row["line_total"] for row in rows)
    return {"id": cart["id"], "status": cart["status"], "total": total, "total_display": money(total), "items": [dict(row) for row in rows]}


def dashboard_state(connection: sqlite3.Connection) -> dict:
    carts = []
    for cart_id in range(1, 6):
        view = cart_view(connection, cart_id)
        if view:
            carts.append(view)
    inventory = [dict(row) | {"stock_display": str(row["stock_quantity"])} for row in connection.execute("SELECT id, name, category, price, stock_quantity FROM products ORDER BY id")]
    transactions = [dict(row) for row in connection.execute(
        """SELECT t.id, t.order_id, t.type, t.status, t.created_at, o.cart_id, o.total_amount,
                  p.demo_reference, p.status AS payment_status
           FROM transactions t JOIN orders o ON o.id=t.order_id
           LEFT JOIN payments p ON p.order_id=o.id ORDER BY t.id DESC LIMIT 8""").fetchall()]
    audit = [dict(row) for row in connection.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 12").fetchall()]
    sales = connection.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status='PAID'").fetchone()[0]
    pending = connection.execute("SELECT COUNT(*) FROM payments WHERE status='PENDING'").fetchone()[0]
    units = connection.execute("SELECT COALESCE(SUM(stock_quantity),0) FROM products").fetchone()[0]
    return {"metrics": {"sales": sales, "sales_display": money(sales), "pending": pending, "inventory_units": units}, "carts": carts, "inventory": inventory, "transactions": transactions, "audit": audit}

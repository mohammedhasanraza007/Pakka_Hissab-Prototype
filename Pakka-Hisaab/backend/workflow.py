"""Deterministic POS workflow services."""

from __future__ import annotations

import base64
import io
import logging
import sqlite3
from datetime import datetime, timezone

from .db import cart_view, dashboard_state, money, utc_now

logger = logging.getLogger("pakkahisaab.workflow")

try:
    import qrcode
except ImportError:  # pragma: no cover - optional visual dependency
    qrcode = None


def payment_case(cart_id: int, payment_method: str) -> dict:
    """Deterministic, visible demo behavior. The browser only requests the outcome."""
    cases = {
        (1, "upi"): {"case_label": "CASE 1 · UPI SUCCESS", "auto_outcome": "success", "auto_delay_seconds": 30, "drawer_confirmation": False},
        (2, "upi"): {"case_label": "CASE 2 · UPI FAILURE", "auto_outcome": "failure", "auto_delay_seconds": 30, "drawer_confirmation": False},
        (3, "cash"): {"case_label": "CASE 3 · CASH RECEIVED", "auto_outcome": None, "auto_delay_seconds": None, "drawer_confirmation": True},
        (4, "cash"): {"case_label": "CASE 4 · CASH DRAWER TIMEOUT", "auto_outcome": "failure", "auto_delay_seconds": 60, "drawer_confirmation": False},
    }
    default = {"case_label": "MANUAL DEMO PAYMENT", "auto_outcome": None, "auto_delay_seconds": None, "drawer_confirmation": payment_method == "cash"}
    return cases.get((cart_id, payment_method), default)


def _audit(connection: sqlite3.Connection, event_type: str, entity_type: str, entity_id: int | None, message: str) -> None:
    connection.execute("INSERT INTO audit_log(event_type, entity_type, entity_id, message, timestamp) VALUES (?, ?, ?, ?, ?)", (event_type, entity_type, entity_id, message, utc_now()))


def _qr_data(reference: str) -> str | None:
    if qrcode is None:
        return None
    image = qrcode.make(f"pakkahisaab://demo-payment/{reference}")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def checkout(connection: sqlite3.Connection, cart_id: int | None, payment_method: str = "upi") -> dict:
    if cart_id is None:
        return {"ok": False, "error": "I couldn't identify a cart number."}
    cart = cart_view(connection, cart_id)
    if cart is None:
        return {"ok": False, "error": f"Cart {cart_id} doesn't exist."}
    if cart["status"] == "PAID":
        return {"ok": False, "error": f"Cart {cart_id} is already paid."}
    if not cart["items"]:
        return {"ok": False, "error": f"Cart {cart_id} is empty."}

    existing = connection.execute("""SELECT p.*, o.status AS order_status, o.total_amount, o.cart_id
                                      FROM payments p JOIN orders o ON o.id=p.order_id
                                      WHERE o.cart_id=? AND p.status='PENDING' ORDER BY p.id DESC LIMIT 1""", (cart_id,)).fetchone()
    if existing:
        return _pending_payload(connection, existing["id"], existing["order_id"], cart)

    now = utc_now()
    cursor = connection.execute("INSERT INTO orders(cart_id, total_amount, status, payment_method, created_at) VALUES (?, ?, ?, ?, ?)", (cart_id, cart["total"], "PAYMENT_PENDING", payment_method, now))
    order_id = cursor.lastrowid
    reference = f"PH-DEMO-{order_id:04d}"
    provider = "DEMO_CASH_DRAWER" if payment_method == "cash" else "DEMO_UPI"
    payment_id = connection.execute("INSERT INTO payments(order_id, provider, amount, status, demo_reference, created_at) VALUES (?, ?, ?, ?, ?, ?)", (order_id, provider, cart["total"], "PENDING", reference, now)).lastrowid
    connection.execute("UPDATE carts SET status='PAYMENT_PENDING', updated_at=? WHERE id=?", (now, cart_id))
    _audit(connection, "ORDER_CREATED", "ORDER", order_id, f"Order created from Cart {cart_id} for {money(cart['total'])}")
    _audit(connection, "PAYMENT_PENDING", "PAYMENT", payment_id, f"Demo payment {reference} awaiting confirmation")
    connection.commit()
    return _pending_payload(connection, payment_id, order_id, cart)


def _pending_payload(connection: sqlite3.Connection, payment_id: int, order_id: int, cart: dict) -> dict:
    payment = connection.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
    order = connection.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    demo_case = payment_case(order["cart_id"], order["payment_method"])
    qr = _qr_data(payment["demo_reference"]) if order["payment_method"] == "upi" else None
    return {"ok": True, "kind": "payment_pending", "payment": dict(payment), "order": dict(order), "cart": cart, "qr_data_url": qr, "demo_case": demo_case, "state": dashboard_state(connection)}


def settle_payment(connection: sqlite3.Connection, payment_id: int, outcome: str) -> dict:
    payment = connection.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
    if not payment:
        return {"ok": False, "error": "That demo payment no longer exists."}
    if payment["status"] != "PENDING":
        return {"ok": False, "error": f"Payment is already {payment['status'].lower()}."}
    order = connection.execute("SELECT * FROM orders WHERE id=?", (payment["order_id"],)).fetchone()
    cart = cart_view(connection, order["cart_id"])
    now = utc_now()
    if outcome == "failure":
        connection.execute("UPDATE payments SET status='FAILED' WHERE id=?", (payment_id,))
        connection.execute("UPDATE orders SET status='PAYMENT_FAILED' WHERE id=?", (order["id"],))
        connection.execute("UPDATE carts SET status='PAYMENT_FAILED', updated_at=? WHERE id=?", (now, order["cart_id"]))
        message = f"Payment {payment['demo_reference']} failed; inventory unchanged"
        if order["payment_method"] == "cash":
            message = f"Cash drawer was not confirmed for {payment['demo_reference']}; inventory unchanged"
        _audit(connection, "PAYMENT_FAILED", "PAYMENT", payment_id, message)
        connection.commit()
        return {"ok": True, "kind": "payment_failed", "payment": dict(connection.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()), "order": dict(connection.execute("SELECT * FROM orders WHERE id=?", (order["id"],)).fetchone()), "cart": cart, "state": dashboard_state(connection)}

    # Every validation and mutation below is in one SQLite transaction.
    try:
        connection.execute("BEGIN")
        items = connection.execute("SELECT product_id, quantity FROM cart_items WHERE cart_id=?", (order["cart_id"],)).fetchall()
        for item in items:
            product = connection.execute("SELECT name, stock_quantity FROM products WHERE id=?", (item["product_id"],)).fetchone()
            if product is None or product["stock_quantity"] < item["quantity"]:
                raise ValueError(f"Insufficient inventory for {product['name'] if product else 'an item'}.")
        for item in items:
            connection.execute("UPDATE products SET stock_quantity=stock_quantity-? WHERE id=?", (item["quantity"], item["product_id"]))
        connection.execute("UPDATE payments SET status='PAID', confirmed_at=? WHERE id=?", (now, payment_id))
        connection.execute("UPDATE orders SET status='PAID', paid_at=? WHERE id=?", (now, order["id"]))
        connection.execute("UPDATE carts SET status='PAID', updated_at=? WHERE id=?", (now, order["cart_id"]))
        tx_id = connection.execute("INSERT INTO transactions(order_id, type, status, created_at) VALUES (?, ?, ?, ?)", (order["id"], "RECONCILIATION", "RECONCILED", now)).lastrowid
        _audit(connection, "PAYMENT_CONFIRMED", "PAYMENT", payment_id, f"Payment {payment['demo_reference']} confirmed")
        _audit(connection, "INVENTORY_UPDATED", "ORDER", order["id"], f"Inventory decremented for Cart {order['cart_id']}")
        _audit(connection, "ORDER_RECONCILED", "TRANSACTION", tx_id, f"Order {order['id']} reconciled")
        connection.commit()
    except Exception:
        connection.rollback()
        logger.exception("Payment settlement failed for payment_id=%s", payment_id)
        return {"ok": False, "error": "Payment could not be completed safely."}
    return {"ok": True, "kind": "payment_paid", "payment": dict(connection.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()), "order": dict(connection.execute("SELECT * FROM orders WHERE id=?", (order["id"],)).fetchone()), "cart": cart_view(connection, order["cart_id"]), "state": dashboard_state(connection)}


def view_cart(connection: sqlite3.Connection, cart_id: int | None) -> dict:
    if cart_id is None:
        return {"ok": False, "error": "I couldn't identify a cart number."}
    cart = cart_view(connection, cart_id)
    return {"ok": bool(cart), "kind": "cart_view", "cart": cart, "error": None if cart else f"Cart {cart_id} doesn't exist.", "state": dashboard_state(connection)}


def inventory_query(connection: sqlite3.Connection, product_query: str | None) -> dict:
    if product_query:
        rows = connection.execute("SELECT id, name, category, price, stock_quantity FROM products WHERE lower(name) LIKE ? ORDER BY id", (f"%{product_query}%",)).fetchall()
    else:
        rows = connection.execute("SELECT id, name, category, price, stock_quantity FROM products ORDER BY id").fetchall()
    return {"ok": True, "kind": "inventory_query", "products": [dict(row) for row in rows], "state": dashboard_state(connection)}

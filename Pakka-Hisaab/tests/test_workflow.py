from pathlib import Path

from backend.db import connect, seed
from backend.intent import parse_command
from backend.workflow import checkout, inventory_query, payment_case, settle_payment


def fresh_db(tmp_path: Path):
    db = connect(tmp_path / "test.db")
    seed(db)
    return db


def test_paraphrases_resolve_to_same_checkout():
    commands = [
        "Clear Cart 1 with UPI.",
        "Checkout cart one using UPI.",
        "Let the first customer pay through UPI.",
        "Please settle the first customer's bill using UPI.",
    ]
    parsed = [parse_command(command) for command in commands]
    assert {(item.intent, item.cart_id, item.payment_method) for item in parsed} == {("checkout_cart", 1, "upi")}


def test_hindi_checkout_variations_resolve_to_cart_one_upi():
    commands = ["कार्ट एक को यूपीआई से क्लियर करो", "कार्ट वन का यू पी आई पेमेंट करो", "पहले कार्ट का भुगतान करो"]
    parsed = [parse_command(command) for command in commands]
    assert {(item.intent, item.cart_id, item.payment_method) for item in parsed} == {("checkout_cart", 1, "upi")}


def test_tamil_checkout_example_resolves_to_cart_one_upi():
    parsed = parse_command("கார்ட் 1-ன் கட்டணத்தை UPI மூலம் செலுத்துங்கள்.")
    assert (parsed.intent, parsed.cart_id, parsed.payment_method) == ("checkout_cart", 1, "upi")


def test_demo_cases_are_deterministic():
    assert payment_case(1, "upi")["auto_outcome"] == "success"
    assert payment_case(2, "upi")["auto_outcome"] == "failure"
    assert payment_case(3, "cash")["drawer_confirmation"] is True
    assert payment_case(4, "cash")["auto_delay_seconds"] == 60


def test_cash_commands_resolve_to_cart_three_and_four():
    commands = ["Clear Cart 3 with cash", "Clear Cart 4 with cash", "कार्ट 3 को कैश से क्लियर करो", "கார்ட் 4-ன் கட்டணத்தை ரொக்கம் மூலம் செலுத்துங்கள்"]
    parsed = [parse_command(command) for command in commands]
    assert [(item.cart_id, item.payment_method) for item in parsed] == [(3, "cash"), (4, "cash"), (3, "cash"), (4, "cash")]


def test_cart_prices_match_product_prices(tmp_path):
    db = fresh_db(tmp_path)
    mismatches = db.execute("SELECT COUNT(*) FROM cart_items ci JOIN products p ON p.id=ci.product_id WHERE ci.unit_price != p.price").fetchone()[0]
    assert mismatches == 0


def test_success_updates_inventory_and_reconciles(tmp_path):
    db = fresh_db(tmp_path)
    before = db.execute("SELECT stock_quantity FROM products WHERE id IN (1,2) ORDER BY id").fetchall()
    result = checkout(db, 1, "upi")
    paid = settle_payment(db, result["payment"]["id"], "success")
    after = db.execute("SELECT stock_quantity FROM products WHERE id IN (1,2) ORDER BY id").fetchall()
    assert paid["ok"] and paid["payment"]["status"] == "PAID"
    assert paid["order"]["status"] == "PAID"
    assert [row[0] for row in before] == [100, 50]
    assert [row[0] for row in after] == [98, 49]
    assert db.execute("SELECT status FROM transactions").fetchone()[0] == "RECONCILED"


def test_failure_does_not_update_inventory(tmp_path):
    db = fresh_db(tmp_path)
    before = db.execute("SELECT stock_quantity FROM products ORDER BY id").fetchall()
    result = checkout(db, 2, "upi")
    failed = settle_payment(db, result["payment"]["id"], "failure")
    after = db.execute("SELECT stock_quantity FROM products ORDER BY id").fetchall()
    assert failed["payment"]["status"] == "FAILED"
    assert failed["order"]["status"] == "PAYMENT_FAILED"
    assert [row[0] for row in before] == [row[0] for row in after]
    assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 0


def test_inventory_query_reads_sqlite(tmp_path):
    db = fresh_db(tmp_path)
    result = inventory_query(db, "soap")
    assert result["products"][0]["stock_quantity"] == 50


def test_invalid_and_duplicate_payment_are_safe(tmp_path):
    db = fresh_db(tmp_path)
    assert checkout(db, 99, "upi")["ok"] is False
    result = checkout(db, 1, "upi")
    assert settle_payment(db, result["payment"]["id"], "success")["ok"]
    duplicate = checkout(db, 1, "upi")
    assert duplicate["ok"] is False and "already paid" in duplicate["error"]


def test_reset_restores_seed(tmp_path):
    db = fresh_db(tmp_path)
    result = checkout(db, 1, "upi")
    settle_payment(db, result["payment"]["id"], "success")
    seed(db)
    assert db.execute("SELECT stock_quantity FROM products WHERE id=1").fetchone()[0] == 100
    assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


def test_paid_state_persists_after_database_reopen(tmp_path):
    path = tmp_path / "persistent.db"
    db = connect(path)
    seed(db)
    pending = checkout(db, 1, "upi")
    settle_payment(db, pending["payment"]["id"], "success")
    db.close()
    reopened = connect(path)
    assert reopened.execute("SELECT status FROM carts WHERE id=1").fetchone()[0] == "PAID"
    assert reopened.execute("SELECT stock_quantity FROM products WHERE id=1").fetchone()[0] == 98
    reopened.close()

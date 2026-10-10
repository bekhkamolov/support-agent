"""Mock order database (SQLite) and the business rules for order lookups and returns.

The rules come from the policy documents and are enforced here in code, not by the LLM:
return window (30 days from delivery, 60 for Nordwind Plus), non-returnable item categories,
return label fee outside Germany/Austria. Lookups require the order number *and* the e-mail
address used for the order, and a wrong e-mail gives the same answer as an unknown order, so
order numbers cannot be probed.
"""
from __future__ import annotations

import functools
import sqlite3
import threading
from datetime import date, timedelta
from typing import Annotated, Literal

from pydantic import BaseModel, Field

OrderId = Annotated[str, Field(pattern=r"^NW-\d{6}$", description='Order number, e.g. "NW-100001".')]
Email = Annotated[str, Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="E-mail address used for the order.")]
ReturnReason = Literal["changed_mind", "wrong_size", "not_as_described", "other"]

# Reference date for the demo data, so results are reproducible.
DEMO_TODAY = date(2026, 10, 10)
RETURN_WINDOW_DAYS = 30
RETURN_WINDOW_DAYS_PLUS = 60
FREE_RETURN_COUNTRIES = {"DE", "AT"}
RETURN_LABEL_FEE_EUR = 6.95
# From "Items that cannot be returned" (returns-exceptions).
NON_RETURNABLE_CATEGORIES = {"earrings", "underwear", "swimwear", "cosmetics", "gift_card", "software", "personalised"}

SCHEMA = """
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY, email TEXT NOT NULL, country TEXT NOT NULL, plus_member INTEGER NOT NULL,
    status TEXT NOT NULL, ordered_on TEXT NOT NULL, delivered_on TEXT, carrier TEXT, tracking_no TEXT
);
CREATE TABLE order_items (
    order_id TEXT NOT NULL REFERENCES orders, sku TEXT NOT NULL, name TEXT NOT NULL,
    category TEXT NOT NULL, price_eur REAL NOT NULL, PRIMARY KEY (order_id, sku)
);
CREATE TABLE returns (
    return_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, sku TEXT NOT NULL, reason TEXT NOT NULL,
    label_fee_eur REAL NOT NULL, created_on TEXT NOT NULL, UNIQUE (order_id, sku)
);
CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY, reason TEXT NOT NULL, summary TEXT NOT NULL, order_id TEXT, created_on TEXT NOT NULL
);
"""

# (order_id, email, country, plus_member, status, days ago ordered, days ago delivered, items)
SEED_ORDERS = [
    ("NW-100001", "anna@example.com", "DE", False, "delivered", 15, 12,
     [("JNS-001", "Slim jeans", "clothing", 59.90), ("TSH-014", "Basic T-shirt", "clothing", 14.90)]),
    ("NW-100002", "ben@example.com", "FR", False, "delivered", 25, 20,
     [("JKT-203", "Rain jacket", "clothing", 89.00)]),
    ("NW-100003", "carla@example.com", "DE", False, "delivered", 60, 56,
     [("SNK-310", "Running sneakers", "shoes", 99.00)]),
    ("NW-100004", "david@example.com", "AT", False, "shipped", 3, None,
     [("BAG-007", "Leather backpack", "bags", 129.00)]),
    ("NW-100005", "eva@example.com", "DE", False, "processing", 0, None,
     [("DRS-120", "Summer dress", "clothing", 49.90)]),
    ("NW-100006", "farid@example.com", "DE", False, "delivered", 12, 9,
     [("EAR-055", "Silver earrings", "earrings", 39.00), ("SCF-019", "Wool scarf", "accessories", 24.90)]),
    ("NW-100007", "greta@example.com", "DE", False, "cancelled", 8, None,
     [("HAT-002", "Bucket hat", "accessories", 19.90)]),
    ("NW-100008", "hannah@example.com", "NL", True, "delivered", 50, 45,
     [("BOT-411", "Ankle boots", "shoes", 119.00)]),
]
CARRIERS = {"DE": "DHL", "AT": "Post AT", "FR": "DPD", "NL": "PostNL"}


class OrderItem(BaseModel):
    sku: str
    name: str
    category: str
    price_eur: float
    returnable_category: bool
    already_returned: bool


class OrderInfo(BaseModel):
    order_id: str
    status: Literal["processing", "shipped", "delivered", "cancelled"]
    ordered_on: date
    delivered_on: date | None
    carrier: str | None
    tracking_no: str | None
    country: str
    plus_member: bool
    return_window_ends: date | None
    items: list[OrderItem]


class ReturnLine(BaseModel):
    sku: str
    return_id: str | None = None
    rejected_reason: str | None = None


class ReturnResult(BaseModel):
    status: Literal["started", "partially_started", "rejected", "not_found"]
    lines: list[ReturnLine] = []
    label_fee_eur: float = 0.0
    message: str


class Ticket(BaseModel):
    ticket_id: str
    reason: str


def _locked(method):
    """Serialise database access: the agent framework may run tools in parallel threads."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)

    return wrapper


class OrderStore:
    """SQLite-backed store. Defaults to a fresh in-memory database with the demo orders."""

    def __init__(self, path: str = ":memory:", today: date = DEMO_TODAY):
        self.today = today
        self._lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        if not self.db.execute("SELECT name FROM sqlite_master WHERE name = 'orders'").fetchone():
            self.db.executescript(SCHEMA)
            self._seed()

    def _seed(self) -> None:
        for oid, email, country, plus, status, ordered_ago, delivered_ago, items in SEED_ORDERS:
            shipped = status in ("shipped", "delivered")
            self.db.execute(
                "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    oid, email, country, int(plus), status,
                    (self.today - timedelta(days=ordered_ago)).isoformat(),
                    (self.today - timedelta(days=delivered_ago)).isoformat() if delivered_ago is not None else None,
                    CARRIERS[country] if shipped else None,
                    f"{CARRIERS[country][:3].upper()}{oid[3:]}{len(items)}" if shipped else None,
                ),
            )
            self.db.executemany(
                "INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", [(oid, *item) for item in items]
            )
        self.db.commit()

    def _verified_order(self, order_id: str, email: str) -> sqlite3.Row | None:
        row = self.db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        if row is None or row["email"].lower() != email.strip().lower():
            return None
        return row

    def _window_end(self, row: sqlite3.Row) -> date | None:
        if row["delivered_on"] is None:
            return None
        days = RETURN_WINDOW_DAYS_PLUS if row["plus_member"] else RETURN_WINDOW_DAYS
        return date.fromisoformat(row["delivered_on"]) + timedelta(days=days)

    @_locked
    def get_order(self, order_id: str, email: str) -> OrderInfo | None:
        row = self._verified_order(order_id, email)
        if row is None:
            return None
        returned = {r["sku"] for r in self.db.execute("SELECT sku FROM returns WHERE order_id = ?", (order_id,))}
        items = [
            OrderItem(
                sku=i["sku"], name=i["name"], category=i["category"], price_eur=i["price_eur"],
                returnable_category=i["category"] not in NON_RETURNABLE_CATEGORIES,
                already_returned=i["sku"] in returned,
            )
            for i in self.db.execute("SELECT * FROM order_items WHERE order_id = ? ORDER BY sku", (order_id,))
        ]
        return OrderInfo(
            order_id=row["order_id"], status=row["status"],
            ordered_on=date.fromisoformat(row["ordered_on"]),
            delivered_on=date.fromisoformat(row["delivered_on"]) if row["delivered_on"] else None,
            carrier=row["carrier"], tracking_no=row["tracking_no"], country=row["country"],
            plus_member=bool(row["plus_member"]), return_window_ends=self._window_end(row), items=items,
        )

    @_locked
    def start_return(self, order_id: str, email: str, skus: list[str], reason: ReturnReason) -> ReturnResult:
        order = self.get_order(order_id, email)
        if order is None:
            return ReturnResult(status="not_found", message="No order found for this order number and e-mail.")
        if order.status != "delivered":
            return ReturnResult(
                status="rejected", lines=[ReturnLine(sku=s, rejected_reason="not_delivered") for s in skus],
                message=f"The order has status '{order.status}'; only delivered orders can be returned.",
            )
        if self.today > order.return_window_ends:
            return ReturnResult(
                status="rejected", lines=[ReturnLine(sku=s, rejected_reason="return_window_expired") for s in skus],
                message=f"The return window ended on {order.return_window_ends.isoformat()}.",
            )

        by_sku = {i.sku: i for i in order.items}
        lines, accepted = [], []
        for sku in dict.fromkeys(skus):  # dedupe, keep order
            item = by_sku.get(sku)
            if item is None:
                lines.append(ReturnLine(sku=sku, rejected_reason="not_in_order"))
            elif not item.returnable_category:
                lines.append(ReturnLine(sku=sku, rejected_reason=f"non_returnable_category:{item.category}"))
            elif item.already_returned:
                lines.append(ReturnLine(sku=sku, rejected_reason="already_returned"))
            else:
                return_id = f"RT-{order_id[3:]}-{sku}"
                lines.append(ReturnLine(sku=sku, return_id=return_id))
                accepted.append((return_id, sku))

        fee = 0.0 if order.country in FREE_RETURN_COUNTRIES else RETURN_LABEL_FEE_EUR
        self.db.executemany(
            "INSERT INTO returns VALUES (?, ?, ?, ?, ?, ?)",
            [(rid, order_id, sku, reason, fee, self.today.isoformat()) for rid, sku in accepted],
        )
        self.db.commit()
        if not accepted:
            return ReturnResult(status="rejected", lines=lines, message="None of the items can be returned.")
        status = "started" if len(accepted) == len(lines) else "partially_started"
        fee_text = "free of charge" if fee == 0 else f"a return label fee of EUR {fee:.2f} is deducted from the refund"
        return ReturnResult(
            status=status, lines=lines, label_fee_eur=fee,
            message=f"Return started for {len(accepted)} item(s); {fee_text}.",
        )

    @_locked
    def create_ticket(self, reason: str, summary: str, order_id: str | None = None) -> Ticket:
        n = self.db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] + 1
        ticket = Ticket(ticket_id=f"TK-{n:05d}", reason=reason)
        self.db.execute(
            "INSERT INTO tickets VALUES (?, ?, ?, ?, ?)",
            (ticket.ticket_id, reason, summary, order_id, self.today.isoformat()),
        )
        self.db.commit()
        return ticket

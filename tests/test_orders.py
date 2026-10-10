import pytest
from pydantic import TypeAdapter, ValidationError

from support_agent.orders import OrderId, OrderStore


@pytest.fixture
def store():
    return OrderStore()


def test_lookup_requires_matching_email(store):
    assert store.get_order("NW-100001", "ANNA@example.com ").status == "delivered"
    assert store.get_order("NW-100001", "someone@example.com") is None
    assert store.get_order("NW-999999", "anna@example.com") is None


def test_wrong_email_and_unknown_order_look_the_same(store):
    wrong_email = store.start_return("NW-100001", "x@example.com", ["JNS-001"], "changed_mind")
    unknown = store.start_return("NW-999999", "anna@example.com", ["JNS-001"], "changed_mind")
    assert wrong_email == unknown


def test_return_within_window_is_free_in_germany(store):
    r = store.start_return("NW-100001", "anna@example.com", ["JNS-001"], "wrong_size")
    assert r.status == "started" and r.label_fee_eur == 0.0
    assert r.lines[0].return_id == "RT-100001-JNS-001"
    assert store.get_order("NW-100001", "anna@example.com").items[0].already_returned


def test_return_label_fee_outside_germany_and_austria(store):
    assert store.start_return("NW-100002", "ben@example.com", ["JKT-203"], "changed_mind").label_fee_eur == 6.95


def test_return_window_expired(store):
    r = store.start_return("NW-100003", "carla@example.com", ["SNK-310"], "changed_mind")
    assert r.status == "rejected" and r.lines[0].rejected_reason == "return_window_expired"


def test_plus_members_have_60_day_window(store):
    # delivered 45 days ago: expired for normal customers, allowed for Nordwind Plus
    assert store.start_return("NW-100008", "hannah@example.com", ["BOT-411"], "changed_mind").status == "started"


def test_non_returnable_item_is_rejected_but_rest_goes_through(store):
    r = store.start_return("NW-100006", "farid@example.com", ["EAR-055", "SCF-019"], "changed_mind")
    assert r.status == "partially_started"
    assert r.lines[0].rejected_reason == "non_returnable_category:earrings"
    assert r.lines[1].return_id


@pytest.mark.parametrize("order_id, email", [("NW-100004", "david@example.com"), ("NW-100005", "eva@example.com")])
def test_undelivered_orders_cannot_be_returned(store, order_id, email):
    sku = store.get_order(order_id, email).items[0].sku
    assert store.start_return(order_id, email, [sku], "changed_mind").lines[0].rejected_reason == "not_delivered"


def test_return_is_idempotent(store):
    store.start_return("NW-100001", "anna@example.com", ["JNS-001"], "changed_mind")
    again = store.start_return("NW-100001", "anna@example.com", ["JNS-001"], "changed_mind")
    assert again.status == "rejected" and again.lines[0].rejected_reason == "already_returned"


def test_unknown_sku_is_rejected(store):
    r = store.start_return("NW-100001", "anna@example.com", ["NOPE-1"], "changed_mind")
    assert r.lines[0].rejected_reason == "not_in_order"


def test_tickets_get_sequential_ids(store):
    assert store.create_ticket("complaint", "a").ticket_id == "TK-00001"
    assert store.create_ticket("other", "b", "NW-100001").ticket_id == "TK-00002"


@pytest.mark.parametrize("bad", ["NW-12345", "nw-123456", "123456", "NW-1234567"])
def test_order_id_format_is_validated(bad):
    with pytest.raises(ValidationError):
        TypeAdapter(OrderId).validate_python(bad)

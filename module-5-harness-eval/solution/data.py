"""Trusted fictional identities and fresh in-memory store data."""

from copy import deepcopy


CUSTOMERS = {
    "CUST-101": {"customer_id": "CUST-101", "name": "Alex Rivera"},
    "CUST-102": {"customer_id": "CUST-102", "name": "Priya Shah"},
}


USERS = {
    "support_jordan": {
        "user_id": "USR-201",
        "name": "Jordan Lee",
        "role": "support_agent",
    },
    "supervisor_morgan": {
        "user_id": "USR-301",
        "name": "Morgan Chen",
        "role": "supervisor",
    },
    "admin_taylor": {
        "user_id": "USR-401",
        "name": "Taylor Smith",
        "role": "administrator",
    },
}


ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_id": "CUST-101",
        "items": [
            {
                "sku": "HEADPHONES-01",
                "name": "Wireless Headphones",
                "category": "electronics",
                "quantity": 1,
                "unit_price_cents": 14900,
                "serial_required": True,
                "serial_number": None,
            }
        ],
        "amount_paid_cents": 14900,
        "days_since_delivery": 12,
        "refund_issued": False,
        "refund_history": [],
        "return_ids": [],
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_id": "CUST-101",
        "items": [
            {
                "sku": "SHIRT-01",
                "name": "Cotton Shirt",
                "category": "apparel",
                "quantity": 1,
                "unit_price_cents": 4000,
            }
        ],
        "amount_paid_cents": 4000,
        "days_since_delivery": 8,
        "refund_issued": False,
        "refund_history": [],
        "return_ids": [],
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_id": "CUST-102",
        "items": [
            {
                "sku": "KEYBOARD-01",
                "name": "Mechanical Keyboard",
                "category": "electronics",
                "quantity": 1,
                "unit_price_cents": 14900,
            }
        ],
        "amount_paid_cents": 14900,
        "days_since_delivery": 14,
        "refund_issued": False,
        "refund_history": [],
        "return_ids": ["RET-1003"],
    },
    "ORD-1004": {
        "order_id": "ORD-1004",
        "customer_id": "CUST-101",
        "items": [
            {
                "sku": "ADAPTER-01",
                "name": "USB-C Adapter",
                "category": "electronics",
                "quantity": 1,
                "unit_price_cents": 3000,
            }
        ],
        "amount_paid_cents": 3000,
        "days_since_delivery": 10,
        "refund_issued": False,
        "refund_history": [],
        "return_ids": ["RET-1004"],
    },
    "ORD-1005": {
        "order_id": "ORD-1005",
        "customer_id": "CUST-102",
        "items": [
            {
                "sku": "BACKPACK-01",
                "name": "Travel Backpack",
                "category": "accessories",
                "quantity": 1,
                "unit_price_cents": 8900,
            }
        ],
        "amount_paid_cents": 8900,
        "days_since_delivery": 18,
        "refund_issued": False,
        "refund_history": [],
        "return_ids": ["RET-1005"],
    },
    "ORD-1006": {
        "order_id": "ORD-1006",
        "customer_id": "CUST-101",
        "items": [
            {
                "sku": "LAMP-01",
                "name": "Desk Lamp",
                "category": "home",
                "quantity": 1,
                "unit_price_cents": 7500,
            }
        ],
        "amount_paid_cents": 7500,
        "days_since_delivery": 9,
        "refund_issued": True,
        "refund_history": [{"amount_cents": 7500, "method": "original_payment"}],
        "return_ids": ["RET-1006"],
    },
}


RETURNS = {
    "RET-1003": {
        "return_id": "RET-1003",
        "order_id": "ORD-1003",
        "sku": "KEYBOARD-01",
        "quantity": 1,
        "reason": "Item was returned by the customer.",
        "status": "RECEIVED",
        "approved_refund_amount_cents": 14900,
        "carrier_scan": True,
        "prior_support_contacts": 0,
    },
    "RET-1004": {
        "return_id": "RET-1004",
        "order_id": "ORD-1004",
        "sku": "ADAPTER-01",
        "quantity": 1,
        "reason": "Return received; entered approval amount may be incorrect.",
        "status": "RECEIVED",
        "approved_refund_amount_cents": 30000,
        "carrier_scan": True,
        "prior_support_contacts": 0,
    },
    "RET-1005": {
        "return_id": "RET-1005",
        "order_id": "ORD-1005",
        "sku": "BACKPACK-01",
        "quantity": 1,
        "reason": "Customer requested a return.",
        "status": "LABEL_CREATED",
        "approved_refund_amount_cents": None,
        "carrier_scan": False,
        "prior_support_contacts": 2,
    },
    "RET-1006": {
        "return_id": "RET-1006",
        "order_id": "ORD-1006",
        "sku": "LAMP-01",
        "quantity": 1,
        "reason": "Return completed and refunded.",
        "status": "REFUNDED",
        "approved_refund_amount_cents": 7500,
        "carrier_scan": True,
        "prior_support_contacts": 0,
    },
}


def fresh_store() -> dict:
    """Return isolated mutable state for one task/configuration/trial."""

    return {
        "customers": deepcopy(CUSTOMERS),
        "orders": deepcopy(ORDERS),
        "returns": deepcopy(RETURNS),
        "store_credits": [],
        "next_return_number": 1007,
    }

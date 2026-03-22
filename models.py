from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import uuid

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    points = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    total_co2_saved = db.Column(db.Float, default=0.0)
    streak_count = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    activities = db.relationship("Activity", backref="user", lazy=True)
    chat_messages = db.relationship("ChatMessage", backref="user", lazy=True)


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=False)
    item_name = db.Column(db.String(128))
    kg_co2e = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Float, default=1.0)
    category = db.Column(db.String(64))
    receipt_id = db.Column(db.String(128))
    brand = db.Column(db.String(128), nullable=True)
    unit = db.Column(db.String(32), nullable=True)
    price = db.Column(db.Float, nullable=True)

    swaps = db.relationship("Swap", backref="activity", lazy=True)


class Swap(db.Model):
    __tablename__ = "swaps"
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)
    original_product = db.Column(db.String(256), nullable=False)
    recommended_product = db.Column(db.String(256), nullable=False)
    recommended_brand = db.Column(db.String(128), nullable=True)
    co2_savings = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(512), nullable=False)
    aisle_location = db.Column(db.String(128), nullable=True)
    accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


USERS_DATA = [
    {"name": "Ava Greenleaf", "email": "ava.greenleaf@email.com", "auth0_id": "auth0|mock_001", "points": 2450, "total_co2_saved": 142.0, "streak_count": 14},
    {"name": "Marcus Chen", "email": "marcus.chen@email.com", "auth0_id": "auth0|mock_002", "points": 2180, "total_co2_saved": 128.0, "streak_count": 11},
    {"name": "Priya Sharma", "email": "priya.sharma@email.com", "auth0_id": "auth0|mock_003", "points": 1920, "total_co2_saved": 115.0, "streak_count": 9},
    {"name": "Jordan Rivers", "email": "jordan.rivers@email.com", "auth0_id": "auth0|mock_004", "points": 1640, "total_co2_saved": 98.0, "streak_count": 7},
    {"name": "Sofia Martinez", "email": "sofia.martinez@email.com", "auth0_id": "auth0|mock_005", "points": 1380, "total_co2_saved": 82.0, "streak_count": 12},
    {"name": "Liam O'Connor", "email": "liam.oconnor@email.com", "auth0_id": "auth0|mock_006", "points": 1150, "total_co2_saved": 71.0, "streak_count": 5},
    {"name": "Zara Ahmed", "email": "zara.ahmed@email.com", "auth0_id": "auth0|mock_007", "points": 980, "total_co2_saved": 64.0, "streak_count": 8},
    {"name": "Tyler Brooks", "email": "tyler.brooks@email.com", "auth0_id": "auth0|mock_008", "points": 820, "total_co2_saved": 55.0, "streak_count": 3},
    {"name": "Emma Nakamura", "email": "emma.nakamura@email.com", "auth0_id": "auth0|mock_009", "points": 680, "total_co2_saved": 42.0, "streak_count": 6},
    {"name": "Noah Williams", "email": "noah.williams@email.com", "auth0_id": "auth0|mock_010", "points": 540, "total_co2_saved": 35.0, "streak_count": 4},
    {"name": "Chloe Dupont", "email": "chloe.dupont@email.com", "auth0_id": "auth0|mock_011", "points": 470, "total_co2_saved": 28.0, "streak_count": 2},
    {"name": "Kai Johnson", "email": "kai.johnson@email.com", "auth0_id": "auth0|mock_012", "points": 380, "total_co2_saved": 22.0, "streak_count": 5},
    {"name": "Mia Patel", "email": "mia.patel@email.com", "auth0_id": "auth0|mock_013", "points": 290, "total_co2_saved": 18.0, "streak_count": 3},
    {"name": "Ethan Clark", "email": "ethan.clark@email.com", "auth0_id": "auth0|mock_014", "points": 220, "total_co2_saved": 14.0, "streak_count": 1},
    {"name": "Olivia Santos", "email": "olivia.santos@email.com", "auth0_id": "auth0|mock_015", "points": 160, "total_co2_saved": 9.0, "streak_count": 2},
    {"name": "James Kim", "email": "james.kim@email.com", "auth0_id": "auth0|mock_016", "points": 110, "total_co2_saved": 6.0, "streak_count": 1},
    {"name": "Aaliyah Brown", "email": "aaliyah.brown@email.com", "auth0_id": "auth0|mock_017", "points": 85, "total_co2_saved": 4.0, "streak_count": 1},
    {"name": "Lucas Fernandez", "email": "lucas.fernandez@email.com", "auth0_id": "auth0|mock_018", "points": 60, "total_co2_saved": 2.5, "streak_count": 0},
    {"name": "Harper Lee", "email": "harper.lee@email.com", "auth0_id": "auth0|mock_019", "points": 30, "total_co2_saved": 1.2, "streak_count": 0},
    {"name": "Ben Okafor", "email": "ben.okafor@email.com", "auth0_id": "auth0|mock_020", "points": 15, "total_co2_saved": 0.5, "streak_count": 0},
]


def seed_mock_data(for_auth0_id="auth0|mock_012"):
    """
    Populate 20 mock leaderboard users and (for for_auth0_id) sample receipts, activities, and swaps.
    Call from app startup when the DB has no mock users yet or very few rows (see app.py).
    """
    if User.query.filter(User.auth0_id.like("auth0|mock_%")).first() is not None:
        return

    today = datetime.utcnow().date()

    users = []
    for row in USERS_DATA:
        streak = int(row["streak_count"])
        if streak > 0:
            last_active_date = today - timedelta(days=random.randint(0, 13))
        else:
            last_active_date = None
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 60))
        users.append(
            User(
                auth0_id=row["auth0_id"],
                name=row["name"],
                email=row["email"],
                points=row["points"],
                streak_count=streak,
                total_co2_saved=round(float(row["total_co2_saved"]), 2),
                last_active_date=last_active_date,
                created_at=created_at,
            )
        )

    db.session.add_all(users)
    db.session.flush()

    target = User.query.filter_by(auth0_id=for_auth0_id).first()
    if not target:
        db.session.commit()
        return

    def rec_id(prefix="REC"):
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

    receipt_specs = [
        [
            ("Tyson Chicken Breast", "Tyson", "Meat", 9.2, "lb", 12.99),
            ("Organic Valley Whole Milk", "Organic Valley", "Dairy", 3.4, "gallon", 5.49),
            ("Chobani Greek Yogurt", "Chobani", "Dairy", 2.1, "each", 1.29),
            ("Driscoll's Strawberries", "Driscoll's", "Produce", 0.6, "lb", 4.99),
            ("Nature Valley Granola Bars", "Nature Valley", "Snacks", 1.8, "box", 3.79),
        ],
        [
            ("Applegate Beef Hot Dogs", "Applegate", "Meat", 6.8, "pack", 6.49),
            ("Oatly Barista Oat Milk", "Oatly", "Beverages", 1.2, "carton", 4.29),
            ("LaCroix Sparkling Water 12pk", "LaCroix", "Beverages", 0.9, "pack", 5.99),
            ("Bob's Red Mill Rolled Oats", "Bob's Red Mill", "Grains", 0.7, "bag", 5.49),
            ("Dole Spinach", "Dole", "Produce", 0.4, "bag", 2.99),
            ("Kerrygold Irish Butter", "Kerrygold", "Dairy", 4.2, "block", 4.99),
        ],
        [
            ("Impossible Burger Patties", "Impossible", "Meat", 5.5, "pack", 8.99),
            ("Horizon Organic Cheese Slices", "Horizon", "Dairy", 2.8, "pack", 4.49),
            ("Blue Diamond Almond Milk", "Blue Diamond", "Beverages", 0.85, "half-gallon", 3.29),
            ("Quaker Old Fashioned Oats", "Quaker", "Grains", 1.1, "canister", 4.79),
            ("Wonderful Pistachios", "Wonderful", "Snacks", 2.4, "bag", 6.99),
            ("Taylor Farms Salad Kit", "Taylor Farms", "Produce", 0.55, "each", 3.49),
        ],
    ]

    created_activities = []
    base_ts = datetime.utcnow()
    for group_idx, items in enumerate(receipt_specs):
        rid = rec_id()
        for j, (item_name, brand, category, kg, unit, price) in enumerate(items):
            act = Activity(
                type="grocery",
                item_name=item_name,
                brand=brand,
                unit=unit,
                price=price,
                kg_co2e=kg,
                user_id=target.id,
                timestamp=base_ts - timedelta(days=2 - group_idx, hours=j),
                quantity=1.0,
                category=category,
                receipt_id=rid,
            )
            db.session.add(act)
            created_activities.append(act)

    db.session.flush()

    meat_by_co2 = sorted(
        [a for a in created_activities if a.category == "Meat"],
        key=lambda a: a.kg_co2e,
        reverse=True,
    )
    dairy_by_co2 = sorted(
        [a for a in created_activities if a.category == "Dairy"],
        key=lambda a: a.kg_co2e,
        reverse=True,
    )
    swap_specs = [
        {
            "activity": meat_by_co2[0],
            "recommended_product": "Air-chilled organic chicken thighs",
            "recommended_brand": "Bell & Evans",
            "co2_savings": 3.2,
            "reason": "Lower-emission poultry cut and regional supply chain vs. breast fillet processing.",
            "aisle_location": "Aisle 4 — Meat & poultry",
        },
        {
            "activity": meat_by_co2[1],
            "recommended_product": "Plant-based protein grounds",
            "recommended_brand": "Beyond Meat",
            "co2_savings": 4.1,
            "reason": "Beef-style hot dogs have a high land-use footprint; plant protein cuts emissions sharply.",
            "aisle_location": "Aisle 6 — Plant-based",
        },
        {
            "activity": dairy_by_co2[0],
            "recommended_product": "Plant-based butter spread",
            "recommended_brand": "Miyoko's Creamery",
            "co2_savings": 2.5,
            "reason": "Dairy butter has high methane intensity; plant-based spreads reduce land and enteric emissions.",
            "aisle_location": "Aisle 7 — Dairy alternatives",
        },
    ]
    for spec in swap_specs[:3]:
        a = spec["activity"]
        db.session.add(
            Swap(
                activity_id=a.id,
                original_product=a.item_name,
                recommended_product=spec["recommended_product"],
                recommended_brand=spec["recommended_brand"],
                co2_savings=spec["co2_savings"],
                reason=spec["reason"],
                aisle_location=spec["aisle_location"],
                accepted=False,
            )
        )

    db.session.commit()

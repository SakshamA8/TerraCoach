"""
EcoCart 3D supermarket floorplan (80 x 60) and routing helpers.
Coordinates: x left-right, z top-bottom (entrance south at high z).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

STORE_WIDTH = 80
STORE_DEPTH = 60
SPINE_X = 17.0
CROSS_BACK_Z = 10.0
CROSS_FRONT_Z = 42.0
ENTRANCE = {"x": 35.0, "z": 60.0}
CHECKOUT_CENTER = {"x": 38.0, "z": 48.0}


def _p(
    pid: str,
    name: str,
    brand: str,
    kg: float,
    sx: float,
    sz: float,
    rec: bool,
) -> Dict[str, Any]:
    return {
        "id": pid,
        "name": name,
        "brand": brand,
        "kg_co2e": round(kg, 2),
        "shelf_x": round(sx, 2),
        "shelf_z": round(sz, 2),
        "is_recommended": rec,
    }


def _zone(
    zid: str,
    name: str,
    category: str,
    x: float,
    z: float,
    width: float,
    depth: float,
    color: str,
    perimeter: bool,
    products: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "id": zid,
        "name": name,
        "category": category,
        "x": x,
        "z": z,
        "width": width,
        "depth": depth,
        "color": color,
        "is_perimeter": perimeter,
        "products": products,
    }


def _build_zones() -> List[Dict[str, Any]]:
    zones: List[Dict[str, Any]] = []

    # BACK WALL
    zones.append(
        _zone(
            "cake_meal",
            "Cake & Meal (Deli Cases)",
            "Bakery",
            0,
            0,
            10,
            8,
            "#f59e0b",
            True,
            [
                _p("cake-1", "Chocolate Layer Cake", "Bakery Fresh", 0.9, 3, 4, True),
                _p("cake-2", "Red Velvet Sheet Cake", "Store Brand", 1.1, 6, 5, False),
                _p("cake-3", "Cheesecake Slices", "Philadelphia", 0.85, 4, 6, True),
                _p("cake-4", "Tiramisu Tray", "Imported", 1.3, 7, 3, False),
                _p("cake-5", "Birthday Cake 8in", "Custom", 1.0, 2, 5, True),
                _p("cake-6", "Cupcakes 12pk", "Sweet Tooth", 0.7, 8, 6, True),
            ],
        )
    )
    zones.append(
        _zone(
            "bakery",
            "Fresh Foods Market — Bakery",
            "Grains",
            10,
            0,
            15,
            10,
            "#fbbf24",
            True,
            [
                _p("bakery-1", "Sourdough Loaf", "La Brea", 0.55, 14, 4, True),
                _p("bakery-2", "Whole Wheat Bread", "Oroweat", 0.62, 18, 5, True),
                _p("bakery-3", "Croissants 4pk", "Artisan", 0.78, 12, 7, False),
                _p("bakery-4", "Bagels 6pk", "Thomas", 0.5, 20, 3, True),
                _p("bakery-5", "Danish Pastries", "Store", 0.95, 16, 8, False),
                _p("bakery-6", "Pita Bread", "Toufayan", 0.48, 22, 4, True),
                _p("bakery-7", "Challah", "Zomick's", 0.7, 11, 6, False),
            ],
        )
    )
    zones.append(
        _zone(
            "dairy_left",
            "Dairy (Left)",
            "Dairy",
            25,
            0,
            15,
            6,
            "#3b82f6",
            True,
            [
                _p("dairyL-1", "2% Milk Gallon", "Organic Valley", 2.4, 28, 3, True),
                _p("dairyL-2", "Whole Milk Gallon", "Store Brand", 2.8, 32, 4, False),
                _p("dairyL-3", "Greek Yogurt 32oz", "Chobani", 1.9, 30, 2, True),
                _p("dairyL-4", "Cheddar Block", "Tillamook", 11.0, 34, 3, False),
                _p("dairyL-5", "Mozzarella Shredded", "Polly-O", 8.5, 27, 4, True),
                _p("dairyL-6", "Butter Salted", "Kerrygold", 12.0, 36, 2, False),
                _p("dairyL-7", "Oat Milk Half Gallon", "Oatly", 1.6, 29, 5, True),
            ],
        )
    )
    zones.append(
        _zone(
            "dairy_right",
            "Dairy (Right)",
            "Dairy",
            40,
            0,
            15,
            6,
            "#3b82f6",
            True,
            [
                _p("dairyR-1", "Skim Milk Gallon", "Horizon", 2.2, 43, 3, True),
                _p("dairyR-2", "Heavy Cream", "Organic Valley", 2.9, 48, 4, False),
                _p("dairyR-3", "Cottage Cheese", "Good Culture", 2.1, 45, 2, True),
                _p("dairyR-4", "Swiss Slices", "Boar's Head", 9.2, 50, 3, True),
                _p("dairyR-5", "Ice Cream Tub", "Häagen-Dazs", 3.4, 46, 5, False),
                _p("dairyR-6", "Almond Milk", "Silk", 1.5, 52, 2, True),
            ],
        )
    )
    zones.append(
        _zone(
            "deli_prepared",
            "Deli & Prepared",
            "Meat",
            58,
            0,
            22,
            12,
            "#f97316",
            True,
            [
                _p("deliP-1", "Rotisserie Chicken", "Store Kitchen", 4.2, 64, 5, True),
                _p("deliP-2", "Honey Ham Sliced", "Boar's Head", 6.5, 70, 4, False),
                _p("deliP-3", "Turkey Breast", "Applegate", 5.1, 66, 8, True),
                _p("deliP-4", "Mac & Cheese Tray", "Deli", 2.8, 72, 6, True),
                _p("deliP-5", "Beef Brisket", "USDA Choice", 18.0, 75, 3, False),
                _p("deliP-6", "Veggie Sushi Roll", "Fresh", 1.4, 68, 9, True),
                _p("deliP-7", "Chicken Salad lb", "Deli", 3.9, 60, 7, False),
            ],
        )
    )

    # LEFT WALL
    zones.append(
        _zone(
            "case_meat",
            "Case Meat",
            "Meat",
            0,
            8,
            8,
            6,
            "#ef4444",
            True,
            [
                _p("cmeat-1", "Ground Beef 80/20", "Certified Angus", 22.0, 3, 10, False),
                _p("cmeat-2", "Chicken Thighs", "Bell & Evans", 5.2, 5, 11, True),
                _p("cmeat-3", "Pork Chops", "Smithfield", 9.5, 4, 12, True),
                _p("cmeat-4", "Steak Ribeye", "Prime", 26.0, 6, 9, False),
                _p("cmeat-5", "Ground Turkey", "Jennie-O", 6.8, 2, 12, True),
            ],
        )
    )
    zones.append(
        _zone(
            "butchers",
            "Butchers Market",
            "Meat",
            0,
            14,
            10,
            8,
            "#dc2626",
            True,
            [
                _p("butch-1", "Beef Tenderloin", "Local Farm", 24.0, 4, 17, False),
                _p("butch-2", "Chicken Breast", "Air-chilled Organic", 5.5, 6, 18, True),
                _p("butch-3", "Lamb Chops", "Imported", 19.0, 3, 19, False),
                _p("butch-4", "Pork Tenderloin", "Niman Ranch", 10.0, 7, 16, True),
                _p("butch-5", "Bison Burgers", "Great Range", 14.0, 5, 20, True),
                _p("butch-6", "Beef Short Ribs", "Choice", 21.0, 8, 18, False),
            ],
        )
    )
    zones.append(
        _zone(
            "fishermans",
            "Fishermans Market",
            "Meat",
            0,
            22,
            10,
            8,
            "#0ea5e9",
            True,
            [
                _p("fish-1", "Atlantic Salmon Fillet", "Wild-ish", 4.5, 4, 25, True),
                _p("fish-2", "Shrimp 16oz", "Imported Farmed", 12.0, 6, 26, False),
                _p("fish-3", "Cod Fillets", "MSC", 3.8, 3, 27, True),
                _p("fish-4", "Tuna Steaks", "Yellowfin", 5.2, 7, 24, False),
                _p("fish-5", "Mussels 2lb", "PEI", 2.9, 5, 28, True),
                _p("fish-6", "Tilapia", "Farm Raised", 4.1, 8, 25, True),
            ],
        )
    )
    zones.append(
        _zone(
            "produce",
            "Farmers Market — Produce",
            "Produce",
            0,
            32,
            16,
            16,
            "#22c55e",
            True,
            [
                _p("produce-1", "Organic Bananas", "Dole", 0.5, 4, 36, True),
                _p("produce-2", "Imported Avocados", "Mission", 1.8, 8, 40, False),
                _p("produce-3", "Spinach Clamshell", "Taylor Farms", 0.45, 6, 38, True),
                _p("produce-4", "Strawberries 1lb", "Driscoll's", 0.7, 10, 35, True),
                _p("produce-5", "Tomatoes Vine", "Local", 0.55, 12, 42, True),
                _p("produce-6", "Bell Peppers", "Greenhouse", 1.2, 5, 44, False),
                _p("produce-7", "Potatoes 5lb", "Idaho", 0.9, 14, 39, True),
                _p("produce-8", "Out-of-season Berries", "Air-freight", 1.45, 11, 45, False),
            ],
        )
    )

    # Grocery aisle shelf products (center block) — 6 aisles, products along shelf centers
    aisle_labels = [
        ("grocery-1", "Canned Goods & Soups", 12.0),
        ("grocery-2", "Cereals & Breakfast", 17.0),
        ("grocery-3", "Baking & Condiments", 22.0),
        ("grocery-4", "Pasta & Grains", 27.0),
        ("grocery-5", "Snacks & Chips", 32.0),
        ("grocery-6", "Beverages", 37.0),
    ]
    for aid, aname, az in aisle_labels:
        base_z = az
        zones.append(
            _zone(
                aid,
                aname,
                "Other",
                18,
                base_z - 1,
                40,
                4,
                "#5eead4",
                False,
                [
                    _p(f"{aid}-a", "Black Beans Canned", "Goya", 0.85, 24, base_z, True),
                    _p(f"{aid}-b", "Chicken Noodle Soup", "Campbell's", 1.1, 32, base_z, False),
                    _p(f"{aid}-c", "Diced Tomatoes", "Muir Glen", 0.65, 40, base_z, True),
                    _p(f"{aid}-d", "Coconut Milk", "Thai Kitchen", 1.4, 28, base_z + 0.6, True),
                    _p(f"{aid}-e", "Chili No Beans", "Hormel", 2.2, 36, base_z + 0.6, False),
                    _p(f"{aid}-f", "Vegetable Broth", "Pacific", 0.72, 44, base_z, True),
                ],
            )
        )

    # RIGHT WALL — Frozen
    zones.append(
        _zone(
            "frozen",
            "Frozen",
            "Frozen",
            65,
            12,
            8,
            28,
            "#a78bfa",
            True,
            [
                _p("frz-1", "Frozen Broccoli", "Birds Eye", 3.2, 68, 18, True),
                _p("frz-2", "Ice Cream Sandwiches", "Klondike", 4.5, 69, 24, False),
                _p("frz-3", "Veggie Burgers", "Dr. Praeger", 3.8, 67, 30, True),
                _p("frz-4", "Frozen Pizza Meat", "DiGiorno", 6.2, 70, 22, False),
                _p("frz-5", "Frozen Berries", "Wyman's", 2.1, 68, 35, True),
                _p("frz-6", "Fish Sticks", "Gorton's", 4.0, 71, 28, False),
                _p("frz-7", "Frozen Lasagna", "Stouffer's", 5.5, 69, 32, False),
            ],
        )
    )

    # BOTTOM AREA
    zones.append(
        _zone(
            "deli_front",
            "Fresh Foods Market — Deli",
            "Meat",
            12,
            14,
            12,
            10,
            "#fb923c",
            True,
            [
                _p("deliF-1", "Sliced Turkey", "Boar's Head", 5.0, 15, 17, True),
                _p("deliF-2", "Salami Milano", "Columbus", 7.2, 18, 19, False),
                _p("deliF-3", "Hummus Tub", "Sabra", 1.3, 14, 20, True),
                _p("deliF-4", "Olive Bar Mix", "Deli", 1.8, 20, 16, True),
                _p("deliF-5", "Prosciutto", "Imported", 8.8, 17, 21, False),
                _p("deliF-6", "Swiss Cheese Sliced", "Prima Della", 9.0, 19, 18, True),
            ],
        )
    )
    zones.append(
        _zone(
            "checkout_zone",
            "Checkout Impulse",
            "Snacks",
            28,
            44,
            20,
            8,
            "#9ca3af",
            True,
            [
                _p("chk-1", "Chewing Gum", "Extra", 0.35, 32, 46, True),
                _p("chk-2", "Chocolate Bar", "Hershey", 0.9, 38, 47, False),
                _p("chk-3", "Granola Bar", "Kind", 0.55, 35, 45, True),
                _p("chk-4", "Breath Mints", "Altoids", 0.4, 40, 46, True),
                _p("chk-5", "Potato Chips", "Lay's", 1.8, 36, 48, False),
            ],
        )
    )
    zones.append(
        _zone(
            "floral",
            "Floral",
            "Other",
            28,
            52,
            14,
            6,
            "#f472b6",
            True,
            [
                _p("flo-1", "Local Tulips", "Floral", 0.4, 32, 54, True),
                _p("flo-2", "Roses Bouquet", "Imported", 1.2, 35, 55, False),
                _p("flo-3", "Potted Basil", "Herb", 0.35, 30, 53, True),
                _p("flo-4", "Sunflowers", "Local", 0.5, 38, 54, True),
                _p("flo-5", "Orchids", "Air-shipped", 1.5, 34, 56, False),
            ],
        )
    )
    zones.append(
        _zone(
            "health_beauty",
            "Health & Beauty",
            "Household",
            55,
            42,
            16,
            10,
            "#c084fc",
            True,
            [
                _p("hb-1", "Bar Soap 6pk", "Dr. Bronner", 0.9, 58, 45, True),
                _p("hb-2", "Shampoo Refill", "Love Beauty", 1.2, 62, 46, True),
                _p("hb-3", "Toothpaste", "Tom's", 0.65, 60, 44, True),
                _p("hb-4", "Disposable Razors", "Gillette", 2.5, 66, 47, False),
                _p("hb-5", "Vitamin D", "Nature Made", 0.55, 64, 48, True),
                _p("hb-6", "Makeup Wipes", "Neutrogena", 1.1, 61, 49, False),
            ],
        )
    )
    zones.append(
        _zone(
            "customer_service",
            "Customer Service",
            "Other",
            55,
            52,
            12,
            6,
            "#6b7280",
            True,
            [
                _p("cs-1", "Gift Cards Rack", "Store", 0.2, 58, 54, True),
                _p("cs-2", "Shopping Bags Reusable", "Eco", 0.45, 60, 55, True),
                _p("cs-3", "Phone Charger", "Generic", 2.8, 62, 53, False),
                _p("cs-4", "Umbrella", "Totes", 1.4, 59, 56, True),
            ],
        )
    )
    zones.append(
        _zone(
            "restrooms",
            "Restrooms",
            "Other",
            72,
            48,
            8,
            10,
            "#d1d5db",
            True,
            [
                _p("rest-1", "Paper Towels Travel", "Bounty", 0.7, 74, 51, True),
                _p("rest-2", "Hand Sanitizer", "Purell", 0.5, 76, 52, True),
                _p("rest-3", "Wet Wipes", "Baby", 0.6, 75, 54, False),
            ],
        )
    )

    return zones


def _build_aisles() -> List[Dict[str, Any]]:
    labels = [
        ("grocery-1", "Canned Goods & Soups", 12),
        ("grocery-2", "Cereals & Breakfast", 17),
        ("grocery-3", "Baking & Condiments", 22),
        ("grocery-4", "Pasta & Grains", 27),
        ("grocery-5", "Snacks & Chips", 32),
        ("grocery-6", "Beverages", 37),
    ]
    return [
        {
            "id": lid,
            "label": f"Aisle {i + 1}: {lbl}",
            "x": 18,
            "z": float(z),
            "width": 38,
            "depth": 2,
        }
        for i, (lid, lbl, z) in enumerate(labels)
    ]


def get_layout_dict() -> Dict[str, Any]:
    return {
        "store_width": STORE_WIDTH,
        "store_depth": STORE_DEPTH,
        "zones": _build_zones(),
        "aisles": _build_aisles(),
        "checkout": {"x": 28, "z": 44, "width": 20, "depth": 8},
        "entrance": {"x": ENTRANCE["x"], "z": ENTRANCE["z"]},
    }


def _product_index(layout: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for z in layout["zones"]:
        for p in z["products"]:
            idx[p["id"]] = {
                **p,
                "zone_id": z["id"],
                "zone_name": z["name"],
            }
    return idx


def _dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _dedupe_waypoints(pts: List[Dict[str, float]]) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    for p in pts:
        if not out or abs(out[-1]["x"] - p["x"]) > 0.05 or abs(out[-1]["z"] - p["z"]) > 0.05:
            out.append(p)
    return out


def _navigate(fx: float, fz: float, tx: float, tz: float) -> List[Dict[str, float]]:
    """
    Walkable path via north-south spine (x=17) and east-west crosses at z=10 and z=42.
    Does not cut through shelf blocks: approach spine on z=42 when south of grocery.
    """
    w: List[Dict[str, float]] = []
    eps = 0.05

    def push(x: float, z: float) -> None:
        x, z = round(x, 2), round(z, 2)
        if not w or abs(w[-1]["x"] - x) > eps or abs(w[-1]["z"] - z) > eps:
            w.append({"x": x, "z": z})

    push(fx, fz)
    # Join spine: if south of front cross, move north to z=42 first
    if fz > CROSS_FRONT_Z + eps:
        push(fx, CROSS_FRONT_Z)
    if abs(w[-1]["x"] - SPINE_X) > eps:
        push(SPINE_X, w[-1]["z"])
    # Move along spine to target latitude
    if abs(w[-1]["z"] - tz) > eps:
        # Optional detour via back cross when both ends are deep north
        if w[-1]["z"] > CROSS_BACK_Z + 1 and tz < CROSS_BACK_Z + 1:
            push(SPINE_X, CROSS_BACK_Z)
        push(SPINE_X, tz)
    # Leave spine to target
    if abs(w[-1]["x"] - tx) > eps:
        push(tx, w[-1]["z"])
    if abs(w[-1]["z"] - tz) > eps:
        push(tx, tz)
    return _dedupe_waypoints(w)


def _append_leg(
    waypoints: List[Dict[str, float]], fx: float, fz: float, tx: float, tz: float
) -> None:
    leg = _navigate(fx, fz, tx, tz)
    if not leg:
        return
    if waypoints and leg[0]["x"] == waypoints[-1]["x"] and leg[0]["z"] == waypoints[-1]["z"]:
        waypoints.extend(leg[1:])
    else:
        waypoints.extend(leg)


def _path_length(waypoints: List[Dict[str, float]]) -> float:
    t = 0.0
    for i in range(1, len(waypoints)):
        t += _dist(
            (waypoints[i - 1]["x"], waypoints[i - 1]["z"]),
            (waypoints[i]["x"], waypoints[i]["z"]),
        )
    return round(t, 2)


def compute_route(product_ids: List[str]) -> Dict[str, Any]:
    layout = get_layout_dict()
    idx = _product_index(layout)
    missing = [pid for pid in product_ids if pid not in idx]
    if missing:
        return {"error": f"Unknown product ids: {missing}"}

    start = (ENTRANCE["x"], ENTRANCE["z"])
    checkout = (CHECKOUT_CENTER["x"], CHECKOUT_CENTER["z"])

    remaining = list(product_ids)
    ordered: List[str] = []
    cur = start
    while remaining:
        best = None
        best_d = 1e18
        for pid in remaining:
            p = idx[pid]
            d = _dist(cur, (p["shelf_x"], p["shelf_z"]))
            if d < best_d:
                best_d = d
                best = pid
        ordered.append(best)
        remaining.remove(best)
        cur = (idx[best]["shelf_x"], idx[best]["shelf_z"])

    waypoints: List[Dict[str, float]] = []
    curx, curz = start

    stops: List[Dict[str, Any]] = []
    stop_n = 0
    for pid in ordered:
        p = idx[pid]
        tx, tz = p["shelf_x"], p["shelf_z"]
        _append_leg(waypoints, curx, curz, tx, tz)
        curx, curz = tx, tz
        stop_n += 1
        stops.append(
            {
                "product_id": pid,
                "product_name": p["name"],
                "zone_name": p["zone_name"],
                "x": tx,
                "z": tz,
                "stop_number": stop_n,
            }
        )

    _append_leg(waypoints, curx, curz, checkout[0], checkout[1])
    waypoints = _dedupe_waypoints(waypoints)
    return {
        "waypoints": waypoints,
        "stops": stops,
        "total_distance": _path_length(waypoints),
    }


def match_activity_to_layout_product(
    item_name: str, category: Optional[str]
) -> Optional[str]:
    """Pick a layout product id for a receipt line (heuristic)."""
    layout = get_layout_dict()
    idx = _product_index(layout)
    name_l = (item_name or "").lower()
    cat = (category or "Other").strip()

    def zone_matches(zc: str) -> bool:
        if cat == "Other":
            return True
        if cat == "Meat":
            return zc == "Meat"
        return zc == cat

    pool: List[str] = []
    for z in layout["zones"]:
        if not zone_matches(z["category"]):
            continue
        for p in z["products"]:
            pool.append(p["id"])
    if not pool:
        for z in layout["zones"]:
            for p in z["products"]:
                pool.append(p["id"])

    best_id: Optional[str] = None
    best_score = -1
    for pid in pool:
        pn = idx[pid]["name"].lower()
        score = sum(2 for w in name_l.split() if len(w) > 2 and w in pn)
        if len(name_l) >= 4 and name_l[:4] in pn:
            score += 1
        if score > best_score:
            best_score = score
            best_id = pid

    if best_id is None or best_score <= 0:
        return min(pool, key=lambda i: idx[i]["kg_co2e"])
    return best_id

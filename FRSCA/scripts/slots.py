"""
Slot mapping utility.

Maps dataset item categories to outfit slots.
This is a deterministic rule-based mapping used
by the outfit generator.
"""

# -----------------------------
# Slot category definitions
# -----------------------------

TOP_CATEGORIES = {
    "top",
    "tshirt",
    "t-shirt",
    "shirt",
    "blouse",
    "tank",
    "sweater",
    "hoodie",
    "tee"
}

BOTTOM_CATEGORIES = {
    "bottom",
    "jeans",
    "trousers",
    "pants",
    "skirt",
    "shorts"
}

OUTERWEAR_CATEGORIES = {
    "outerwear",
    "jacket",
    "coat",
    "blazer",
    "cardigan",
    "overcoat"
}

DRESS_CATEGORIES = {
    "dress",
    "gown"
}

# -----------------------------
# Slot mapping function
# -----------------------------

def get_slot(item):
    # Primary signal (your dataset uses this correctly)
    category = item.get("category", "").lower()

    if category == "dress":
        return "DRESS"

    if category == "top":
        return "TOP"

    if category == "bottom":
        return "BOTTOM"

    if category == "outerwear":
        return "OUTERWEAR"

    # Fallbacks (defensive, for noisy labels)
    subcategory = item.get("subcategory", "").lower()

    if "jacket" in subcategory or "coat" in subcategory or "blazer" in subcategory:
        return "OUTERWEAR"

    return None



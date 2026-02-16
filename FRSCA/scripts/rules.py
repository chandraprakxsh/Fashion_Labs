"""
Rules engine for outfit generation.

Encodes Season, Occasion, and Style constraints.
These rules decide:
- which slots are active
- which items are allowed
"""

# -----------------------------
# SEASON RULES (hard constraints)
# -----------------------------

SEASON_RULES = {
    "summer": {
        "OUTERWEAR": False,
        "allowed_coverage": {"short", "long"}  # Allow both for flexibility (e.g., formal summer wear)
    },
    "winter": {
        "OUTERWEAR": True,
        "allowed_coverage": {"long"}
    },
    "monsoon": {
        "OUTERWEAR": "optional",
        "allowed_coverage": {"short", "long"}
    }
}

# -----------------------------
# OCCASION RULES (hard social constraints)
# -----------------------------

OCCASION_RULES = {
    "casual": {
        "disallowed_categories": {"blazer"}
    },
    "office": {
        "disallowed_categories": {"shorts", "tank", "sandals"},
        "required_footwear": {"shoes", "loafers"}
    },
    "party": {
        "disallowed_categories": {"athletic"}
    }
}

# -----------------------------
# STYLE RULES (soft constraints)
# -----------------------------

STYLE_PREFERENCES = {
    "minimal": {
        "preferred_fit": {"regular", "slim"}
    },
    "street": {
        "preferred_fit": {"relaxed", "oversized"}
    },
    "formal": {
        "preferred_fit": {"structured", "tailored"}
    }
}

# -----------------------------
# Slot activation logic
# -----------------------------

def slot_enabled(slot, season):
    """
    Determine if a slot is enabled based on season.
    """
    rule = SEASON_RULES.get(season, {})
    slot_rule = rule.get(slot, True)

    if slot_rule is False:
        return False

    return True

# -----------------------------
# Item validation logic
# -----------------------------

def item_allowed(item, slot, season, occasion):
    """
    Validate if an item is allowed based on season and occasion constraints.
    """
    # Check occasion-based usage filtering
    if occasion == "formal":
        usage = item.get("usage", [])
        if "formal" not in usage:
            return False
    
    # Check season-based coverage rules
    season_rule = SEASON_RULES.get(season, {})
    allowed_coverage = season_rule.get("allowed_coverage")
    
    if allowed_coverage:
        item_coverage = item.get("coverage", "")
        if item_coverage and item_coverage not in allowed_coverage:
            return False
    
    # Check occasion-based category restrictions
    occasion_rule = OCCASION_RULES.get(occasion, {})
    disallowed = occasion_rule.get("disallowed_categories", set())
    
    item_category = item.get("subcategory", "")
    if item_category in disallowed:
        return False
    
    return True

# -----------------------------
# Style preference scoring (optional)
# -----------------------------

def style_bonus(item, style):
    """
    Soft bonus score based on style preference.
    Does NOT invalidate items.
    """

    if not style:
        return 0.0

    fit = item.get("fit", "").lower()
    preferred = STYLE_PREFERENCES.get(style, {}).get("preferred_fit", set())

    if fit and fit in preferred:
        return 0.05

    return 0.0

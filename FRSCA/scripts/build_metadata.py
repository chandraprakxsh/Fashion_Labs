import os
import json
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "processed")

embeddings = np.load(os.path.join(PROC_DIR, "embeddings.npy"))
image_names = np.load(os.path.join(PROC_DIR, "image_names.npy"), allow_pickle=True)

def map_filename_to_metadata(filename):
    name = filename.lower()

    # -------- gender --------
    if filename.startswith("WOMEN"):
        gender = "women"
    elif filename.startswith("MEN"):
        gender = "men"
    else:
        gender = "unknown"

    # -------- tokenize --------
    try:
        main = filename.split("-")[1]   # Jackets_Coats
    except IndexError:
        main = ""
    tokens = main.lower().split("_")

    # -------- vocabularies --------
    OUTERWEAR = {"jacket", "jackets", "coat", "coats", "blazer", "blazers"}
    TOPS      = {"tshirt", "tshirts", "tee", "shirt", "shirts", "top", "tops"}
    BOTTOMS   = {"jeans", "pants", "trousers", "shorts", "skirt", "skirts"}
    DRESSES   = {"dress", "dresses"}
    FOOTWEAR  = {"shoes", "shoe", "sneakers", "heels", "boots"}

    # -------- category + subcategory --------
    category = "top"
    subcategory = tokens[0] if tokens else "unknown"

    for t in tokens:
        if t in OUTERWEAR:
            category = "outerwear"
            subcategory = t
            break
        if t in DRESSES:
            category = "dress"
            subcategory = t
            break
        if t in BOTTOMS:
            category = "bottom"
            subcategory = t
            break
        if t in FOOTWEAR:
            category = "footwear"
            subcategory = t
            break
        if t in TOPS:
            category = "top"
            subcategory = t
            break

    # -------- derived attributes --------
    layer = "outer" if category == "outerwear" else "inner"

    if category == "outerwear":
        coverage = "long"
    elif category == "dress":
        coverage = "full"
    elif "shorts" in tokens:
        coverage = "short"
    else:
        coverage = "long"

    structure = "structured" if category in {"outerwear", "dress"} else "unstructured"

    fit = "regular"

    # Derive usage (formal vs casual)
    usage = []
    if category == "outerwear":
        usage.append("cold")
    
    # Determine formal/casual based on subcategory and structure
    # Formal items include: dress shirts, blazers, suiting, structured items, dress pants
    is_formal = False
    is_casual = False
    
    if structure == "structured":
        is_formal = True
    
    # Formal subcategories
    formal_subcategories = {"blazers", "suiting", "shirts"}
    if subcategory in formal_subcategories:
        is_formal = True
        # Shirts can be both formal and casual
        if subcategory == "shirts":
            is_casual = True
    
    # Pants (non-denim) are formal
    if category == "bottom" and subcategory == "pants":
        is_formal = True
        is_casual = True  # Pants can be both
    
    # Casual items
    casual_subcategories = {"denim", "tees", "tanks", "sweatshirts", "hoodies", "shorts", "polos"}
    if subcategory in casual_subcategories:
        is_casual = True
    
    # Default: if not explicitly formal, mark as casual
    if not is_formal and not is_casual:
        is_casual = True
    
    # Add to usage array
    if is_formal:
        usage.append("formal")
    if is_casual:
        usage.append("casual")

    return {
        "gender": gender,
        "category": category,
        "subcategory": subcategory,
        "layer": layer,
        "coverage": coverage,
        "structure": structure,
        "fit": fit,
        "usage": usage
    }


metadata = []

for idx, img_name in enumerate(image_names):
    attrs = map_filename_to_metadata(img_name)

    metadata.append({
        "id": idx,
        "image": img_name,
        **attrs
    })


out_path = os.path.join(PROC_DIR, "metadata.json")

with open(out_path, "w") as f:
    json.dump(metadata, f, indent=2)

print("✅ Metadata file created:", out_path)

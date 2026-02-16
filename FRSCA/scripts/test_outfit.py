import sys
import os
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_outfit import generate_outfit


# -----------------------------
# Load processed data
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "processed")

embeddings = np.load(os.path.join(PROC_DIR, "embeddings.npy"))
image_names = np.load(
    os.path.join(PROC_DIR, "image_names.npy"),
    allow_pickle=True
)

with open(os.path.join(PROC_DIR, "metadata.json")) as f:
    metadata = json.load(f)

print("\n🔍 SAMPLE METADATA KEYS:")
print(metadata[0].keys())

print("\n🔍 SAMPLE CATEGORY-LIKE VALUES:")
for k in metadata[0].keys():
    print(k, "→", metadata[0][k])


# -----------------------------
# Run a test
# -----------------------------
outfit = generate_outfit(
    metadata=metadata,
    embeddings=embeddings,
    image_names=image_names,
    gender="men",
    season="winter",
    occasion="party",
    style="minimal"
)

print("\nGenerated outfit:\n")
if outfit is None:
    print("❌ No outfit could be generated (rules too strict)")
else:
    for slot, item in outfit.items():
        print(f"{slot} → {item}")

from scripts.slot_alternatives import replace_slot

print("\n--- Replacing TOP ---\n")

new_outfit = replace_slot(
    current_outfit=outfit,
    slot_to_replace="TOP",
    metadata=metadata,
    embeddings=embeddings,
    image_names=image_names,
    gender="men",
    season="winter",
    occasion="casual",
    style="minimal"
)

for slot, item in new_outfit.items():
    print(slot, "→", item)

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from scripts.slots import get_slot
from scripts.rules import item_allowed


def generate_outfit(
    metadata,
    embeddings,
    image_names,
    gender,
    season,
    occasion,
    style=None
):
    # -----------------------------
    # 1. Decide active slots (NO FOOTWEAR)
    # -----------------------------
    slots = ["TOP", "BOTTOM"]

    if season == "winter":
        slots.append("OUTERWEAR")

    # -----------------------------
    # 2. Build candidate pools per slot
    # -----------------------------
    slot_candidates = {slot: [] for slot in slots}

    for i, item in enumerate(metadata):
        if item.get("gender") != gender:
            continue

        slot = get_slot(item)
        if slot not in slots:
            continue

        if not item_allowed(item, slot, season, occasion):
            continue

        slot_candidates[slot].append(i)

    # -----------------------------
    # 3. Pick TOP as anchor
    # -----------------------------
    anchor_indices = slot_candidates["TOP"]

    anchor_vectors = [embeddings[i] for i in anchor_indices]
    anchor_centroid = np.mean(anchor_vectors, axis=0)

    anchor_scores = []
    for i in anchor_indices:
        sim = cosine_similarity(
            [anchor_centroid], [embeddings[i]]
        )[0][0]
        anchor_scores.append((i, sim))

    anchor_scores.sort(key=lambda x: x[1], reverse=True)

    if not anchor_scores:
        return None
    
    anchor_index = anchor_scores[0][0]

    outfit = {
        "TOP": build_item(anchor_index, metadata, image_names)
    }

    reference_vectors = [embeddings[anchor_index]]

    # -----------------------------
    # 4. Fill remaining slots
    # -----------------------------
    for slot in slots:
        if slot == "TOP":
            continue

        candidates = slot_candidates[slot]
        if not candidates:
            continue

        ref_vector = np.mean(reference_vectors, axis=0)

        scored = []
        for i in candidates:
            sim = cosine_similarity(
                [ref_vector], [embeddings[i]]
            )[0][0]
            scored.append((i, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        best_index = scored[0][0]

        outfit[slot] = build_item(best_index, metadata, image_names)
        reference_vectors.append(embeddings[best_index])

    return outfit


def build_item(index, metadata, image_names):
    item = metadata[index]
    return {
        "image": image_names[index],
        "category": item.get("category"),
        "gender": item.get("gender")
    }
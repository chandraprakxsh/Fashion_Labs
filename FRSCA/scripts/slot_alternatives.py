import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from scripts.slots import get_slot
from scripts.rules import item_allowed


def recommend_slot_alternatives(
    current_outfit,
    slot,
    metadata,
    embeddings,
    image_names,
    gender,
    season,
    occasion,
    top_k=5
):
    """
    Return top-K compatible items for ONE slot,
    without mutating the outfit.
    """

    # -----------------------------
    # 1. Build reference vector from other slots
    # -----------------------------
    ref_vectors = []
    for s, item in current_outfit.items():
        if s == slot:
            continue
        idx = list(image_names).index(item["image"])
        ref_vectors.append(embeddings[idx])

    if not ref_vectors:
        return []

    ref_vector = np.mean(ref_vectors, axis=0)

    # -----------------------------
    # 2. Collect candidates for the slot
    # -----------------------------
    candidates = []
    for i, item in enumerate(metadata):
        if item.get("gender") != gender:
            continue

        if get_slot(item) != slot:
            continue

        if not item_allowed(item, slot, season, occasion):
            continue

        # avoid suggesting the same item
        if item["image"] == current_outfit[slot]["image"]:
            continue

        candidates.append(i)

    if not candidates:
        return []

    # -----------------------------
    # 3. Score by compatibility
    # -----------------------------
    scored = []
    for i in candidates:
        sim = cosine_similarity(
            [ref_vector], [embeddings[i]]
        )[0][0]
        scored.append((i, sim))

    scored.sort(key=lambda x: x[1], reverse=True)

    # -----------------------------
    # 4. Return top-K alternatives
    # -----------------------------
    results = []
    for i, score in scored[:top_k]:
        results.append({
            "image": image_names[i],
            "category": metadata[i].get("category"),
            "gender": metadata[i].get("gender"),
            "score": float(score)
        })

    return results
import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "processed")

embeddings = np.load(os.path.join(PROC_DIR, "embeddings.npy"))
image_names = np.load(os.path.join(PROC_DIR, "image_names.npy"), allow_pickle=True)

with open(os.path.join(PROC_DIR, "metadata.json")) as f:
    metadata = json.load(f)

def context_score(item, ctx):
    score = 0

    if item["season"] == ctx["season"] or item["season"] == "all":
        score += 1
    if item["style"] == ctx["style"]:
        score += 1
    if item["occasion"] == ctx["occasion"]:
        score += 1

    return score / 3  # normalized (0.0 → 1.0)

def build_context_vector(indices):
    return np.mean([embeddings[i] for i in indices], axis=0)

def recommend(ctx, top_k=10):
    """
    ctx example:
    {
      "gender": "women",
      "category": "outerwear",
      "layer": "outer",
      "coverage": "long",
      "structure": "structured"
    }
    """

    # ---------- STEP 1: HARD FILTER ----------
    candidates = []
    for i, item in enumerate(metadata):
        if (
            item["gender"] == ctx["gender"]
            and item["category"] == ctx["category"]
            and item["layer"] == ctx["layer"]
        ):
            candidates.append(i)

    # Fallback: relax layer
    if not candidates:
        for i, item in enumerate(metadata):
            if (
                item["gender"] == ctx["gender"]
                and item["category"] == ctx["category"]
            ):
                candidates.append(i)

    # Absolute fallback: same category only
    if not candidates:
        for i, item in enumerate(metadata):
            if item["category"] == ctx["category"]:
                candidates.append(i)

    if not candidates:
        return []

    # ---------- STEP 2: REFERENCE VECTOR ----------
    ref_vector = np.mean(
        [embeddings[i] for i in candidates],
        axis=0
    )

    # ---------- STEP 3: SCORE & RANK ----------
    results = []
    for i in candidates:
        item = metadata[i]

        visual_sim = cosine_similarity(
            [ref_vector], [embeddings[i]]
        )[0][0]

        soft_bonus = 0
        if "coverage" in ctx and item["coverage"] == ctx["coverage"]:
            soft_bonus += 0.05

        final_score = visual_sim + soft_bonus

        results.append({
            "image": image_names[i],
            "score": float(final_score),
            "visual_similarity": float(visual_sim),
            "gender": item["gender"],
            "category": item["category"],
            "layer": item["layer"],
            "coverage": item["coverage"],
            "structure": item["structure"]
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    ctx = {
        "season": "summer",
        "style": "formal",
        "occasion": "party"
    }

    recs = recommend(ctx, top_k=5)

    for r in recs:
        print(r)
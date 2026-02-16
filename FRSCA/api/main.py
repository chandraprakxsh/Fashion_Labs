import os
import sys
import json
import numpy as np
from typing import Dict

from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------
# Fix import path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# -----------------------------
# Import your logic
# -----------------------------
from scripts.generate_outfit import generate_outfit
from scripts.slot_alternatives import recommend_slot_alternatives

# -----------------------------
# Load data ONCE at startup
# -----------------------------
PROC_DIR = os.path.join(BASE_DIR, "processed")

embeddings = np.load(os.path.join(PROC_DIR, "embeddings.npy"))
image_names = np.load(
    os.path.join(PROC_DIR, "image_names.npy"),
    allow_pickle=True
)

with open(os.path.join(PROC_DIR, "metadata.json")) as f:
    metadata = json.load(f)

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI()

# -----------------------------
# Serve images as static files
# -----------------------------
IMAGE_DIR = os.path.join(BASE_DIR, "train_images")

app.mount(
    "/images",
    StaticFiles(directory=IMAGE_DIR),
    name="images"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for dev
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Request schemas
# -----------------------------

class GenerateOutfitRequest(BaseModel):
    gender: str
    season: str
    occasion: str
    style: str | None = None


class SlotAlternativesRequest(BaseModel):
    current_outfit: dict
    slot: str
    gender: str
    season: str
    occasion: str
    top_k: int = 5


# -----------------------------
# Endpoints
# -----------------------------

@app.post("/generate-outfit")
def generate_outfit_api(req: GenerateOutfitRequest):
    try:
        outfit = generate_outfit(
            metadata=metadata,
            embeddings=embeddings,
            image_names=image_names,
            gender=req.gender,
            season=req.season,
            occasion=req.occasion,
            style=req.style
        )
        return {"outfit": outfit}
    except Exception as e:
        return {"error": str(e)}

@app.post("/slot-alternatives")
def slot_alternatives_api(req: SlotAlternativesRequest):
    alternatives = recommend_slot_alternatives(
        current_outfit=req.current_outfit,
        slot=req.slot,
        metadata=metadata,
        embeddings=embeddings,
        image_names=image_names,
        gender=req.gender,
        season=req.season,
        occasion=req.occasion,
        top_k=req.top_k
    )

    return {
        "slot": req.slot,
        "alternatives": alternatives
    }
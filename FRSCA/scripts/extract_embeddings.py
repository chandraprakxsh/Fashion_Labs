import os
import numpy as np
import torch
from PIL import Image
from tqdm import tqdm

from torchvision.models import resnet50, ResNet50_Weights
import torch.nn as nn
from torchvision import transforms


# -----------------------------
# Paths (Windows-safe)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "train_images")
OUT_DIR = os.path.join(BASE_DIR, "processed")

os.makedirs(OUT_DIR, exist_ok=True)


# -----------------------------
# Model (Feature Extractor)
# -----------------------------
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.fc = nn.Identity()
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)


# -----------------------------
# Image Transform
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# -----------------------------
# Extraction Loop
# -----------------------------
embeddings = []
image_names = []

image_files = os.listdir(IMG_DIR)

print(f"Found {len(image_files)} images")

with torch.no_grad():
    for img_name in tqdm(image_files):
        img_path = os.path.join(IMG_DIR, img_name)

        try:
            img = Image.open(img_path).convert("RGB")
            img_tensor = transform(img).unsqueeze(0).to(device)

            emb = model(img_tensor)
            embeddings.append(emb.squeeze().cpu().numpy())
            image_names.append(img_name)

        except Exception as e:
            print(f"Skipping {img_name}: {e}")


# -----------------------------
# Save to Disk
# -----------------------------
embeddings = np.array(embeddings)

np.save(os.path.join(OUT_DIR, "embeddings.npy"), embeddings)
np.save(os.path.join(OUT_DIR, "image_names.npy"), image_names)

print("✅ Embedding extraction completed")
print("Embeddings shape:", embeddings.shape)

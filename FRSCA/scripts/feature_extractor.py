import torch
from torchvision.models import resnet50, ResNet50_Weights
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms

weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.fc = nn.Identity()
model.eval()

# Load ResNet-50
def get_resnet():
    model = models.resnet50(pretrained=True)
    model.fc = nn.Identity()
    model.eval()
    return model

# Image preprocessing
def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
if __name__ == "__main__":
    from PIL import Image
    import os

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(BASE_DIR, "train_images")

    img_name = os.listdir(img_dir)[0]
    img = Image.open(os.path.join(img_dir, img_name)).convert("RGB")

    transform = get_transform()
    model = get_resnet()

    img_tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        emb = model(img_tensor)

    print("Embedding shape:", emb.shape)

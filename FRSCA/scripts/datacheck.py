from PIL import Image
import matplotlib.pyplot as plt
import os

img_dir = "train_images"
img_name = os.listdir(img_dir)[0]

img = Image.open(os.path.join(img_dir, img_name)).convert("RGB")
plt.imshow(img)
plt.axis("off")

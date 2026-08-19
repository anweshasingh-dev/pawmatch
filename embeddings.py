import os
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np

# 1. Setup Device (Use GPU if available, fallback to CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2. Reconstruct your fine-tuned ResNet-50 Architecture
resnet = models.resnet50()
num_features = resnet.fc.in_features
resnet.fc = torch.nn.Linear(num_features, 128)  # Matches your Colab 128-dim FC layer

# 3. Load your fine-tuned weights file
MODEL_PATH = os.path.join(os.path.dirname(__file__), "pet_embedder_resnet50.pth")

if os.path.exists(MODEL_PATH):
    resnet.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    print("Successfully loaded custom pet_embedder_resnet50.pth!")
else:
    print(f"Warning: Custom model file not found at {MODEL_PATH}. Using untrained weights.")

resnet.to(device)
resnet.eval()

# 4. Standard Preprocessing Pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def extract_image_vector(image_path: str) -> list[float]:
    """Extracts a 128-dimensional feature vector using your fine-tuned pet model."""
    try:
        image = Image.open(image_path).convert("RGB")
        tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            features = resnet(tensor)
            vector = features.squeeze().cpu().numpy().tolist()
        return vector
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        return []

def calculate_visual_similarity(vector1: list[float], vector2: list[float]) -> float:
    """Calculates cosine similarity percentage (0 - 100%) between two vectors."""
    if not vector1 or not vector2:
        return 0.0
    
    # Dimension Guard: Prevents matrix alignment crashes on vector length mismatches
    if len(vector1) != len(vector2):
        print(f"Warning: Vector size mismatch ({len(vector1)} vs {len(vector2)}). Skipping similarity calculation.")
        return 0.0
    
    values1 = np.asarray(vector1, dtype=float)
    values2 = np.asarray(vector2, dtype=float)
    norm1 = np.linalg.norm(values1)
    norm2 = np.linalg.norm(values2)
    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = (np.dot(values1, values2) / (norm1 * norm2)) * 100
    return max(0.0, round(float(similarity), 2))
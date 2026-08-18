import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
from scipy.spatial.distance import cosine

# Load a pre-trained ResNet-18 model and remove its final classification layer
resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
resnet.eval()
feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])

# Image preprocessing pipeline for ResNet
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def extract_image_vector(image_path: str) -> list[float]:
    """Extracts a 512-dimensional feature vector from an image file."""
    try:
        image = Image.open(image_path).convert("RGB")
        tensor = transform(image).unsqueeze(0)
        with torch.no_grad():
            features = feature_extractor(tensor)
            # Flatten to a 1D vector (512 dimensions)
            vector = features.squeeze().numpy().tolist()
        return vector
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        return []

def calculate_visual_similarity(vector1: list[float], vector2: list[float]) -> float:
    """Calculates cosine similarity percentage (0 - 100%) between two vectors."""
    if not vector1 or not vector2:
        return 0.0
    # Cosine distance is 1 - similarity
    distance = cosine(vector1, vector2)
    similarity = (1 - distance) * 100
    return max(0.0, round(similarity, 2))
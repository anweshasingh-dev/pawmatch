class AnimalDetector:
    """Mock detector used during custom ML pipeline development."""

    def __init__(self, confidence=0.25):
        self.confidence = confidence

    def detect(self, image):
        # Stub response until custom trained model is integrated
        return {
            "species": "unknown",
            "confidence": 1.0,
            "bounding_box": None
        }
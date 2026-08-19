import os
from embeddings import extract_image_vector, calculate_visual_similarity
from geocoding import get_coordinates, calculate_haversine_distance

print("--- TESTING PAWMATCH BACKEND PIPELINE ---\n")

# 1. Test Geocoding & Distance Calculation
print("1. Testing Geocoding & Location Math...")
address1 = "Connaught Place, New Delhi"
address2 = "Saket, New Delhi"

lat1, lon1 = get_coordinates(address1)
lat2, lon2 = get_coordinates(address2)

if lat1 and lat2:
    dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
    print(f" SUCCESS: Distance between '{address1}' and '{address2}' is {dist} km.\n")
else:
    print(" FAILED: Could not resolve coordinates.\n")

# 2. Test Model Vector Extraction
print("2. Testing Feature Vector Extraction & Visual Similarity...")

# Look for an existing image in your 'uploads' folder
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
sample_images = [f for f in os.listdir(uploads_dir) if f.endswith(('.jpg', '.jpeg', '.png'))] if os.path.exists(uploads_dir) else []

if len(sample_images) >= 1:
    img_path1 = os.path.join(uploads_dir, sample_images[0])
    vector1 = extract_image_vector(img_path1)
    
    print(f" SUCCESS: Extracted vector from '{sample_images[0]}'. Vector length: {len(vector1)}")
    
    if len(sample_images) >= 2:
        img_path2 = os.path.join(uploads_dir, sample_images[1])
        vector2 = extract_image_vector(img_path2)
        sim = calculate_visual_similarity(vector1, vector2)
        print(f" SUCCESS: Similarity score between '{sample_images[0]}' and '{sample_images[1]}': {sim}%")
    else:
        # Compare image against itself as a sanity check (should be 100%)
        sim = calculate_visual_similarity(vector1, vector1)
        print(f" SUCCESS: Self-similarity score for '{sample_images[0]}': {sim}% (Expected: 100%)")
else:
    print(" NOTICE: Place a sample pet photo inside your 'uploads/' folder to test image vector extraction.")

print("\n--- PIPELINE TEST COMPLETE ---")
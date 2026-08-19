# 🐾 PawMatch

## AI-Powered Lost & Found Pet Platform

**Project Type:** Full-Stack Web Application + Computer Vision + Similarity Search
**Primary Goal:** Help reunite lost pets with their owners by intelligently matching lost and found pet reports.

**Project Status:** Active Development

---

# 1. Project Overview

PawMatch is a web-based lost-and-found pet platform where users can report pets that they have lost or found.

Each report can contain:

- Pet photographs
- Species
- General physical characteristics
- Location where the pet was lost/found
- Date and time
- Additional description
- Contact information
- Report status

The system is designed to go beyond a simple searchable database.

When a user submits a lost or found pet report, PawMatch will analyse the available information and rank existing reports according to how closely they match the submitted pet.

The long-term matching system will combine:

1. **Visual similarity**
2. **Species compatibility**
3. **Geographical proximity**
4. **Time/date relevance**
5. **User-provided physical characteristics**
6. **Potentially other learned features**

The result will be a ranked list of potentially matching reports rather than requiring users to manually search through every report.

---

# 2. Problem Statement

Traditional lost-and-found pet systems largely depend on users manually browsing listings.

This creates several problems:

- A user may not know what keywords to search for.
- Different people may describe the same animal differently.
- Photographs contain information that text-based search cannot fully capture.
- A lost pet may be reported using different terminology from the corresponding found-pet report.
- Large numbers of reports make manual comparison difficult.
- Location and time are important but are often treated separately from image information.

PawMatch aims to reduce this search burden by automatically identifying potentially related reports.

---

# 3. Product Vision

The ideal user experience is:

> **Upload a photo → provide basic information → PawMatch analyses existing reports → receive a ranked list of likely matches.**

For example:

A user reports:

> **Lost dog**
> Location: Meerut
> Date: 15 August
> Brown-and-white dog
> Medium-sized
> Photograph uploaded

The system searches existing found-pet reports and might return:

| Rank | Report         | Visual Match | Location | Overall Score |
| ---- | -------------- | -----------: | -------: | ------------: |
| 1    | Found Dog #184 |          91% |   2.3 km |           88% |
| 2    | Found Dog #162 |          84% |   5.7 km |           77% |
| 3    | Found Dog #201 |          79% |   8.1 km |           71% |

The system should therefore act as a **matching assistant**, not as an authority declaring that two reports definitely refer to the same animal.

---

# 4. Core User Workflow

## 4.1 Creating a Report

The user submits:

- Lost / Found status
- Pet image
- Species
- Approximate location
- Date
- General physical description
- Optional identifying characteristics
- Contact information

The backend stores the report in PostgreSQL.

---

## 4.2 Image Processing

The uploaded image passes through the computer-vision pipeline.

The intended pipeline is:

```text
Uploaded Image
      ↓
Animal Detection
      ↓
Species Identification
      ↓
Pet Crop
      ↓
Feature / Embedding Extraction
      ↓
Similarity Search
      ↓
Multi-Factor Ranking
      ↓
Ranked Reports
```

---

# 5. System Architecture

```text
                    ┌─────────────────────┐
                    │      User           │
                    │ Lost/Found Report   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Flask App       │
                    │   Backend / API     │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
      ┌────────────┐    ┌──────────────┐   ┌──────────────┐
      │ PostgreSQL │    │ Image Storage│   │ ML Pipeline  │
      │  Database  │    │              │   │              │
      └────────────┘    └──────────────┘   └──────┬───────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    │                           │
                                    ▼                           ▼
                              ┌───────────┐              ┌────────────┐
                              │ Detection │              │ Embedding  │
                              │   Model   │              │   Model    │
                              └───────────┘              └─────┬──────┘
                                                               │
                                                               ▼
                                                     ┌─────────────────┐
                                                     │ Similarity +    │
                                                     │ Ranking Engine  │
                                                     └────────┬────────┘
                                                              │
                                                              ▼
                                                     ┌─────────────────┐
                                                     │ Ranked Matches  │
                                                     └─────────────────┘
```

---

# 6. Current Technology Stack

## Backend

- Python
- Flask
- Jinja2
- Werkzeug

## Database

- PostgreSQL
- psycopg2
- JSONB where appropriate

## Computer Vision / Machine Learning

Current/planned:

- YOLO / Ultralytics for object detection
- PyTorch
- torchvision
- ResNet-18 or another embedding model
- Cosine similarity
- Potential future metric-learning model

## Geospatial

- Haversine distance
- geopy
- OpenStreetMap / Nominatim for geocoding

## Frontend

- HTML
- Jinja2
- Tailwind CSS

## Deployment / Infrastructure

- Docker
- Docker Compose

## Notifications

- SMTP email notifications

---

# 7. Current Project Structure

```text
pawmatch/
│
├── app.py
├── database.py
├── detector.py
├── embeddings.py
├── geocoding.py
├── matcher.py
├── notifications.py
│
├── schema.sql
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── templates/
│   ├── ...
│
├── static/
│   ├── ...
│
└── uploads/
```

### Responsibilities

**app.py**

Main Flask application and routes.

**database.py**

Database connections and database operations.

**detector.py**

Computer-vision detection interface.

**embeddings.py**

Image feature extraction.

**geocoding.py**

Location conversion and geographical distance calculations.

**matcher.py**

Combines individual matching signals into an overall ranking.

**notifications.py**

Email notification functionality.

**schema.sql**

PostgreSQL database schema.

---

# 8. Current Implementation Status

## Completed

- [x] Flask backend
- [x] PostgreSQL integration
- [x] Pet report creation
- [x] Lost/found report workflow
- [x] Report storage
- [x] Basic matching infrastructure
- [x] Haversine geographical distance calculation
- [x] Mock detector interface
- [x] Modular ML architecture
- [x] Docker configuration
- [x] Email notification infrastructure

## Currently Mocked / Temporary

The current `detector.py` contains a temporary detector interface.

It intentionally allows the application to operate without a trained computer-vision model.

```python
class AnimalDetector:
    """Mock detector used during custom ML pipeline development."""

    def __init__(self, confidence=0.25):
        self.confidence = confidence

    def detect(self, image):
        return {
            "species": "unknown",
            "confidence": 1.0,
            "bounding_box": None
        }
```

This interface will eventually be replaced by the real model without requiring major changes to the rest of the application.

---

# 9. Planned Computer Vision Pipeline

The ML system should be treated as multiple problems rather than trying to make one model do everything.

## Stage 1 — Animal Detection

Goal:

> Determine whether the uploaded image contains a relevant animal and locate it.

Possible model:

**YOLO**

Output:

```text
Species: dog
Confidence: 0.94
Bounding box: [x1, y1, x2, y2]
```

For cats:

```text
Species: cat
Confidence: 0.97
```

---

# 10. Stage 2 — Pet Image Cropping

If the uploaded image contains background clutter, the detected bounding box can be used to crop the pet.

```text
Original Image
      ↓
YOLO Detection
      ↓
Bounding Box
      ↓
Pet Crop
```

This prevents irrelevant background information from dominating the similarity calculation.

---

# 11. Stage 3 — Visual Feature Extraction

Object detection alone is **not enough** for identifying whether two photographs contain the same individual animal.

YOLO can tell us:

> "This is a dog."

But PawMatch eventually needs to answer:

> "How visually similar is this dog to the dog in another report?"

Therefore, an image embedding model can be used.

For example:

```text
Pet Image
    ↓
Embedding Model
    ↓
512-dimensional feature vector
```

Example:

```text
[0.12, -0.04, 0.87, ...]
```

The exact embedding size depends on the selected model.

---

# 12. Stage 4 — Similarity Calculation

Two pet images can be converted into vectors:

```text
Image A → Vector A
Image B → Vector B
```

Then calculate cosine similarity.

Conceptually:

```text
similarity = cosine(Vector A, Vector B)
```

A higher value means the images are more similar in the embedding space.

However:

> **Similarity score should NOT automatically be interpreted as the probability that two photographs show the same individual animal.**

A proper validation dataset is required before assigning meaningful confidence percentages.

---

# 13. Stage 5 — Multi-Factor Matching

Visual similarity should be only one component of the final ranking.

A possible initial scoring system:

```text
Overall Score =
    0.55 × Visual Similarity
  + 0.20 × Location Score
  + 0.10 × Time Score
  + 0.10 × Physical Feature Score
  + 0.05 × Species Compatibility
```

These weights are **initial engineering assumptions**, not scientifically validated values.

They should eventually be tuned using real validation data.

---

# 14. Example Matching Pipeline

Suppose a lost-pet report is submitted.

```text
Lost Report
    │
    ├── Image
    ├── Species = Dog
    ├── Location
    ├── Date
    └── Description
          │
          ▼
     Image Detector
          │
          ▼
       Dog Crop
          │
          ▼
    Image Embedding
          │
          ▼
     Search Database
          │
          ├── Found Dog A
          ├── Found Dog B
          ├── Found Dog C
          └── Found Dog D
          │
          ▼
     Calculate Scores
          │
          ▼
     Rank Candidates
          │
          ▼
     Display Results
```

---

# 15. Confidence vs Similarity

This distinction is important for the project.

## Detection Confidence

Example:

```text
Dog detected
Confidence = 96%
```

This means the detection model is confident that the object belongs to the "dog" class.

It does **not** mean:

> "There is a 96% chance that this is the user's missing dog."

---

## Image Similarity

Example:

```text
Candidate A
Similarity = 0.91
```

This means the two image representations are highly similar according to the selected embedding model.

It does **not automatically mean** there is a 91% probability that they are the same animal.

---

## Final Match Score

The application can display something like:

```text
Potential Match
Overall Match Score: 88/100
```

The UI should describe this as a **ranking score**, unless the model has been properly calibrated and validated to represent a probability.

---

# 16. Model Training Strategy

The first version should NOT attempt to train an enormous custom model from scratch.

The development strategy should be:

### Phase A — Pretrained Models

Use pretrained models to establish the complete pipeline.

Goal:

```text
Image
→ Detection
→ Crop
→ Embedding
→ Similarity
→ Ranking
```

This allows the application architecture to be tested before investing heavily in training.

---

### Phase B — Collect / Prepare Dataset

The project eventually needs images of individual pets.

The dataset should ideally contain:

```text
Pet ID
├── Image 1
├── Image 2
├── Image 3
└── ...
```

The important distinction is:

```text
Same animal
vs
Different animal
```

This is more important for the matching problem than simply having thousands of generic dog/cat photographs.

---

### Phase C — Evaluate Baseline

Test the pretrained embedding model.

Measure:

- Top-1 accuracy
- Top-5 accuracy
- Precision
- Recall
- False positive rate
- False negative rate

For a lost-and-found application, **false matches are particularly important** because a visually similar but unrelated animal could mislead users.

---

### Phase D — Fine-Tuning

If the pretrained model is insufficient, fine-tune an embedding model using the collected pet dataset.

Possible approaches include:

- Contrastive learning
- Triplet loss
- Siamese networks
- Metric learning
- Fine-tuning pretrained vision encoders

The objective becomes:

```text
Same pet → embeddings closer together

Different pets → embeddings farther apart
```

---

# 17. How Long Will Training Take?

Training time depends much more on the dataset and hardware than on the name of the model.

A useful development estimate:

| Stage                     |                Approximate Effort |
| ------------------------- | --------------------------------: |
| Build pretrained baseline |                          1–3 days |
| Dataset preparation       |                Several days–weeks |
| Baseline evaluation       |                          1–3 days |
| Fine-tuning experiments   | Hours–several days per experiment |
| Model comparison          |                      Several days |
| Production integration    |                          2–5 days |

The actual GPU training time for a small fine-tuning experiment could be relatively short.

The difficult part is **not pressing the training button**.

The difficult part is obtaining a dataset that actually represents the problem.

A model trained on random internet images of dogs and cats may become excellent at:

> dog vs cat

while remaining poor at:

> Is Dog A the same individual as Dog B?

Therefore, dataset quality and evaluation are central to PawMatch.

---

# 18. Recommended Initial ML Approach

The first serious implementation should therefore be:

```text
YOLO
  ↓
Detect dog/cat
  ↓
Crop animal
  ↓
Pretrained image encoder
  ↓
Generate embedding
  ↓
Store embedding
  ↓
Cosine similarity against existing reports
  ↓
Combine with location/time/features
  ↓
Rank reports
```

This gives PawMatch a functioning **AI-assisted matching pipeline** without requiring a massive custom training operation immediately.

---

# 19. Database Concept

Each pet report should contain information similar to:

```text
Report
├── report_id
├── user_id
├── report_type
│      ├── LOST
│      └── FOUND
├── species
├── image_path
├── image_embedding
├── latitude
├── longitude
├── location_description
├── date
├── physical_description
├── contact_information
├── status
└── created_at
```

The embedding can be stored alongside the report or eventually moved to a dedicated vector-search solution depending on scale.

---

# 20. Matching Algorithm

For every new report:

```python
for candidate in candidate_reports:

    visual_score = compare_embeddings(
        new_report.embedding,
        candidate.embedding
    )

    location_score = calculate_location_score(
        new_report.location,
        candidate.location
    )

    time_score = calculate_time_score(
        new_report.date,
        candidate.date
    )

    feature_score = compare_features(
        new_report,
        candidate
    )

    final_score = weighted_score(
        visual_score,
        location_score,
        time_score,
        feature_score
    )
```

Candidates are then sorted:

```python
matches.sort(
    key=lambda x: x["final_score"],
    reverse=True
)
```

---

# 21. Candidate Filtering

The system does not necessarily need to compare a report against every report.

First filter obvious mismatches.

For example:

```text
Lost Dog
    ↓
Ignore Cat Reports
    ↓
Ignore Resolved Reports
    ↓
Prioritize nearby reports
    ↓
Prioritize relevant dates
    ↓
Run expensive image similarity
```

This improves efficiency as the database grows.

---

# 22. Alerts

If a candidate reaches a sufficiently high validated threshold, the system can notify the user.

Example:

```text
Potential Match Found!

A found-pet report near your lost-pet location
has a high matching score.

View Report →
```

The initial threshold should be conservative.

For example, a temporary engineering threshold might be:

```text
Score ≥ 75 → notify
```

But this number should **not be presented as scientifically meaningful** until the model is evaluated on a representative validation dataset.

---

# 23. Important ML Risks

## 23.1 Same Breed ≠ Same Pet

Two Labrador dogs may look extremely similar.

The model needs to learn individual-level visual differences.

---

## 23.2 Different Photographs of the Same Pet

Lighting, camera angle, pose, distance, fur condition and background can change significantly.

The system must therefore be robust to:

- Different angles
- Different lighting
- Different backgrounds
- Different image quality
- Partial occlusion
- Different poses

---

## 23.3 Breed Bias

A system trained on certain breeds or image distributions may perform poorly on uncommon breeds or mixed-breed animals.

---

## 23.4 False Confidence

The UI should never imply:

> "This is definitely your pet."

It should communicate:

> "This report is a potentially strong match."

The human user remains responsible for verifying the pet.

---

# 24. Development Roadmap

## Phase 1 — Core Infrastructure

**Status: Mostly complete**

- [x] Flask application
- [x] PostgreSQL database
- [x] Report submission
- [x] Lost/found workflow
- [x] Basic matching architecture
- [x] Geographical calculations
- [x] Modular detector interface
- [x] Docker setup

---

## Phase 2 — Baseline Computer Vision

**Next major milestone**

- [ ] Integrate pretrained YOLO
- [ ] Detect dog/cat
- [ ] Extract bounding boxes
- [ ] Crop detected pets
- [ ] Integrate pretrained embedding model
- [ ] Generate image embeddings
- [ ] Store embeddings
- [ ] Implement cosine similarity
- [ ] Display similarity results

---

## Phase 3 — Multi-Factor Ranking

- [ ] Visual similarity score
- [ ] Location score
- [ ] Time score
- [ ] Physical-feature score
- [ ] Species filtering
- [ ] Combined ranking algorithm
- [ ] Candidate filtering
- [ ] Match result UI

---

## Phase 4 — Dataset & Model Research

- [ ] Find suitable public datasets
- [ ] Investigate pet re-identification datasets
- [ ] Build dataset preprocessing pipeline
- [ ] Define train/validation/test splits
- [ ] Establish baseline metrics
- [ ] Compare embedding models
- [ ] Experiment with fine-tuning

---

## Phase 5 — Production ML Pipeline

- [ ] Model versioning
- [ ] Embedding generation service
- [ ] Efficient similarity search
- [ ] Model confidence calibration
- [ ] Threshold tuning
- [ ] Error analysis
- [ ] Performance monitoring

---

## Phase 6 — Product Polish

- [ ] Better UI/UX
- [ ] User authentication
- [ ] User profiles
- [ ] Report management
- [ ] Image galleries
- [ ] Map interface
- [ ] Email alerts
- [ ] Better mobile experience
- [ ] Deployment

---

# 25. Current Immediate Tasks

## Repository

- [ ] Verify `.env` is excluded from Git
- [ ] Verify `uploads/` is excluded where appropriate
- [ ] Remove unnecessary model weights from Git
- [ ] Update `requirements.txt`
- [ ] Verify application starts cleanly
- [ ] Push clean baseline to GitHub

## Backend

- [ ] Keep detector interface modular
- [ ] Keep ML logic separated from Flask routes
- [ ] Verify report creation
- [ ] Verify database queries
- [ ] Verify matching pipeline

## Machine Learning

- [ ] Research pretrained YOLO model
- [ ] Test dog/cat detection
- [ ] Research suitable embedding models
- [ ] Implement embedding extraction
- [ ] Compare two pet images
- [ ] Test cosine similarity
- [ ] Integrate similarity into matcher
- [ ] Experiment with ranking weights

---

# 26. Project Design Principle

PawMatch should be built so that the AI model is **replaceable**.

The Flask application should not care whether the detector is:

```text
Mock Model
     ↓
YOLO
     ↓
Custom YOLO
     ↓
Another Detection Model
```

The interface should remain approximately:

```python
detection = detector.detect(image)
```

Likewise, the application should not depend directly on the internal architecture of the embedding model.

Conceptually:

```python
embedding = embedder.encode(image)
```

This allows experimentation without rewriting the entire application.

---

# 27. Definition of Done for the First AI Version

The first meaningful AI milestone does NOT require a custom-trained model.

Version 1 is complete when:

```text
User uploads pet image
        ↓
System detects dog/cat
        ↓
Pet is cropped
        ↓
Embedding is generated
        ↓
Embedding is compared with reports
        ↓
Potential matches are ranked
        ↓
Location/time information modifies ranking
        ↓
User sees ranked candidate reports
```

Once this pipeline works, the project has a real AI matching system.

The next question becomes:

> How accurate is it?

That is where dataset collection, evaluation and fine-tuning begin.

---

# 28. Long-Term Vision

PawMatch can eventually evolve from a simple lost-and-found database into an intelligent pet re-identification platform.

Possible future capabilities:

- Pet-specific visual embeddings
- Breed identification
- Fur-pattern analysis
- Face / muzzle / ear feature analysis
- Collar/accessory recognition
- Location-aware search
- Time-aware matching
- Duplicate report detection
- Similarity-based recommendations
- Community verification
- Automated high-confidence alerts
- Map-based missing-pet discovery
- Image quality assessment
- Multiple-photo matching

The central idea remains:

> **Turn scattered lost-and-found reports into a searchable, intelligent network of potential matches.**

---

# 29. Project Philosophy

PawMatch is intentionally being developed in layers.

```text
Product
  ↓
Backend
  ↓
Database
  ↓
Matching Architecture
  ↓
Pretrained AI Baseline
  ↓
Evaluation
  ↓
Custom ML
  ↓
Production Optimization
```

The goal is not to train a complicated model immediately.

The goal is to build a complete system where every component has a clear purpose, can be tested independently, and can be improved without rebuilding the application from scratch.

---

# 30. Current Project Status Summary

**PawMatch currently has the foundation of the product implemented.**

The web application, database, report workflow and matching architecture provide the infrastructure required for the next major stage.

The current detector is intentionally a temporary interface.

The next major development milestone is therefore:

> **Replace the mock detector with a real computer-vision pipeline and introduce image embeddings for individual-pet similarity matching.**

After the baseline pipeline works, model accuracy can be improved through better datasets, evaluation, fine-tuning and metric-learning approaches.

This keeps the project development practical:

```text
Build → Test → Measure → Improve
```

rather than attempting to solve the entire machine-learning problem before the product itself exists.

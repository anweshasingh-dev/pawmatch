# 📦 VisionBox — Object Detection Workshop

Upload an image and detect **animals** *and what they're doing* (e.g. "dog (sit)") using
a YOLO11 model. We build the detection logic together, step by step, over the session.

## Setup (do this BEFORE the workshop)

The first install downloads some large libraries, so please do this ahead of time on a
good internet connection.

### Option A — with `uv` (fastest, recommended)

[`uv`](https://docs.astral.sh/uv/) is a fast Python package manager. If you don't have it,
install it with the one-liner from the [uv install docs](https://docs.astral.sh/uv/getting-started/installation/)
(e.g. `pip install uv`).

1. Open a terminal in this folder.
2. Create the virtual environment and install the dependencies in one go:
   ```bash
   uv sync
   ```
3. Run the app to make sure it launches:
   ```bash
   uv run streamlit run app.py
   ```

### Option B — with `pip` + venv

1. Open a terminal in this folder.
2. (Recommended) create and activate a virtual environment:

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app to make sure it launches:
   ```bash
   streamlit run app.py
   ```
   Your browser should open with the VisionBox page. Uploading an image works, but
   clicking **Run detection** will show an error for now — that's expected! We write the
   detection code together during the session.

## The idea (read this first)

Our model doesn't just find animals — it was trained to also detect **poses** (what the
animal is doing). It returns these as **separate boxes**: one box for `dog`, another box
for `sit`. Our job in Part 2 is to figure out which pose belongs to which animal and
combine them into a single label like **"dog (sit)"**.

To decide if two boxes belong together, we measure how much they overlap using **IoU**
(Intersection over Union):

```
IoU = area of overlap  /  area covered by both boxes together
```

IoU is `0.0` when boxes don't touch and `1.0` when they're identical. If an animal box
and a pose box overlap by at least `POSE_IOU_THRESHOLD` (0.3), we treat them as a pair.

## What we build (two parts)

All the code lives in **`detector.py`**, which has five functions with step-by-step
`TODO` comments. `app.py` (the UI) is already done — you don't need to edit it.

### Part 1 — Basic detection

| Step | Function | What it does |
|------|----------|--------------|
| 1–2  | `load_model()`     | Load the YOLO model (`animals.pt`) |
| 3    | `detect_objects()` | Run the model on the uploaded image |
| 4    | `draw_boxes()`     | Draw the boxes (start simple with `results.plot()`) |

**Checkpoint:** run the app, upload an animal photo, click **Run detection**. You should
see boxes drawn on the image. The results table shows a "coming in Part 2" note — that's
expected.

### Part 2 — Pose pairing

| Step | Function | What it does |
|------|----------|--------------|
| 5    | `_iou()`               | Measure overlap between two boxes |
| 6    | `pair_detections()`    | Match each animal with its best-overlapping pose |
| 8    | `draw_boxes()` (upgrade) | Redraw with custom labels like "dog (sit)" |
| 7    | `build_results_table()`| Build the table shown under the image |

**The pairing algorithm** (`pair_detections`), in words:

1. Split every detected box into two lists: `animals` and `poses` (use `POSE_CLASSES`).
2. For each animal, look at every pose that hasn't been used yet and compute the IoU.
   Keep the pose with the **highest** IoU, as long as it's at least the threshold (0.3).
   That pose becomes the animal's `position`. (If none overlap enough, `position` stays
   `None`.)
3. Any pose that never matched an animal is still reported on its own.

**Checkpoint:** upload an animal photo and you should see combined labels like
"dog (sit)" on the image, plus a table of all detections below it.

## What the model can detect

- **Animals:** cat · cow · dog · horse · sheep
- **Poses:** eating · laying · run · sit · stand

Bring or download a few photos of these animals to test with.

## Files

```
app.py            # the user interface (already done — no need to edit)
detector.py       # the detection logic — we build this together
animals.pt        # the trained YOLO11 model
requirements.txt  # Python dependencies
```

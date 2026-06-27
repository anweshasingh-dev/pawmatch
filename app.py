import streamlit as st
from PIL import Image

from detector import detect_objects, draw_boxes, build_results_table

st.set_page_config(page_title="VisionBox", page_icon="📦")
st.title("📦 VisionBox — Object Detection")
st.caption("Upload an image and detect animals (and what they're doing) with YOLO11.")

confidence = st.slider("Confidence threshold", 0.10, 1.00, 0.25, 0.05)

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded image", width=480)

    if st.button("Run detection"):
        with st.spinner("Detecting..."):
            results = detect_objects(image, confidence)
            annotated = draw_boxes(image, results)
        st.image(annotated, caption="Detected objects", width=480)

        # PART 2: the results table. Until build_results_table() is written this
        # shows a friendly note instead of crashing.
        try:
            table = build_results_table(results)
            st.subheader("Detections")
            st.dataframe(table, use_container_width=True)
        except NotImplementedError:
            st.info("Results table comes in Part 2 — build build_results_table().")

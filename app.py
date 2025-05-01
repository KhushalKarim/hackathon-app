import os
import streamlit as st
from PIL import Image
from transformers import pipeline

# Load Hugging Face models for text extraction (OCR) and summarization
ocr_model = pipeline("image-to-text", model="facebook/dino-vitb16")  # Replace with an actual OCR model if needed
summarizer = pipeline("summarization", model="Falconsai/text_summarization")

# UI Title
st.title("🩺 Second Opinion App for Patients")

# Divider
st.markdown("---")
st.subheader("📥 Step 1: Upload Your Prescription")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your prescription (Image or PDF)", 
    type=["jpg", "png", "jpeg", "pdf"]
)

# Helper functions
def extract_text_from_image(file):
    img = Image.open(file)
    return ocr_model(img)

def extract_text_from_pdf(file):
    # PDF processing for OCR
    # You may want to implement PDF-to-image conversion if needed using libraries like pdf2image
    pass

# Step 2: Extract and display text
presc_text = ""
if uploaded_file is not None:
    if uploaded_file.type.startswith("image/"):
        presc_text = extract_text_from_image(uploaded_file)
        st.image(uploaded_file, caption="Prescription Image", use_column_width=True)
    else:
        presc_text = extract_text_from_pdf(uploaded_file)
        st.write("📄 PDF uploaded — text extracted below:")

    # Show extracted text
    st.subheader("📄 Extracted Prescription Text")
    st.write(presc_text)

# Divider
st.markdown("---")
st.subheader("🔍 Step 2: Enter the Medicine Names")

# User inputs medicine names
meds = st.text_input("Please type the medicine names from the prescription (comma-separated)", "")

if meds:
    st.write(f"✅ You entered: `{meds}`")

# Divider
st.markdown("---")
st.subheader("💡 Step 3: Generate Questions to Ask Your Doctor")

# Generate suggestions when both prescription and medicine names are available
if presc_text.strip() and meds.strip():
    if st.button("💬 Generate Questions"):
        input_prompt = (
            f"Here is a prescription provided by a doctor:\n{presc_text}\n\n"
            f"Medicines prescribed: {meds}\n\n"
            "Based on this prescription and the medicines the doctor has suggested, generate a list of important questions a patient should ask their doctor before taking them. "
            "Focus on asking about side effects, dosage instructions, drug interactions, and any necessary precautions."
        )

        try:
            summary = summarizer(input_prompt, max_length=120, min_length=40, do_sample=False)[0]["summary_text"]
            st.subheader("📋 Suggested Questions for Your Doctor")
            for line in summary.strip().split(". "):
                if line.strip():
                    st.write("•", line.strip())
        except Exception as e:
            st.error(f⚠️ Error generating questions: {e}")
else:
    st.info("Please upload a prescription and enter medicine names to generate questions.")

# Optional: Final confirmation button
if st.button("✅ Final Check"):
    st.success("Prescription reviewed. You may now ask these questions to your doctor.")

import os
import streamlit as st
from PIL import Image, Image as PILImage
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust if needed
import fitz  # PyMuPDF
from transformers import pipeline

# Load Hugging Face summarization model
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
    return pytesseract.image_to_string(img)

def extract_text_from_pdf(file):
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        text = page.get_text()
        if text.strip():
            full_text += text + "\n"
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            full_text += ocr_text + "\n"
    return full_text

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
            st.error(f"⚠️ Error generating questions: {e}")
else:
    st.info("Please upload a prescription and enter medicine names to generate questions.")

# Optional: Final confirmation button
if st.button("✅ Final Check"):
    st.success("Prescription reviewed. You may now ask these questions to your doctor.")

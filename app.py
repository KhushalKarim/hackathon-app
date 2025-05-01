import os
import streamlit as st
from PIL import Image, Image as PILImage
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust if needed
import fitz
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# Streamlit UI setup
st.title("🩺 Second Opinion App For Patients")

# Helper functions for text extraction
def extract_text_from_image(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img)

def extract_text_from_pdf(file):
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        page_text = page.get_text()
        if page_text.strip():
            full_text += page_text + "\n"
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            full_text += ocr_text + "\n"
    return full_text

# Load Hugging Face summarization model as a workaround to generate helpful questions
summarizer = pipeline("summarization", model="Falconsai/text_summarization")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your prescription (Image or PDF)", 
    type=["jpg", "png", "jpeg", "pdf"]
)

if uploaded_file is not None:
    # Extract text
    if uploaded_file.type.startswith("image/"):
        presc_text = extract_text_from_image(uploaded_file)
        st.image(uploaded_file, caption="Prescription Image", use_column_width=True)
    else:
        presc_text = extract_text_from_pdf(uploaded_file)
        st.write("📄 PDF Uploaded — text extracted below:")

    # Display extracted text
    st.subheader("Extracted Prescription Text")
    st.write(presc_text)

    # Optional manual medicine entry
    meds = st.text_input("Medicine names (comma-separated)", "")
    if meds:
        st.write(f"**You entered:** {meds}")

    # Suggest questions to ask the doctor
    if presc_text.strip():
        input_prompt = (
    f"Here is a prescription provided by a doctor:\n{presc_text}\n\n"
    f"Medicines prescribed: {meds}\n\n"
    "Based on this prescription and the medicines the doctor has suggested, generate a list of important questions a patient should ask their doctor before taking them. "
    "Focus on asking about side effects, dosage instructions, drug interactions, and any necessary precautions."
)


        try:
            summary = summarizer(input_prompt, max_length=120, min_length=40, do_sample=False)[0]["summary_text"]
            st.subheader("💬 Suggested Questions (via Hugging Face)")
            for line in summary.strip().split(". "):
                if line:
                    st.write("•", line.strip())
        except Exception as e:
            st.error(f"⚠️ Error generating questions: {e}")

# Button for further logic
if st.button("Check Prescription"):
    st.info("✅ Prescription checked!")

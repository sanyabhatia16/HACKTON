import streamlit as st
import os
import fitz  # PyMuPDF
import docx2txt
from dotenv import load_dotenv
from openai import AzureOpenAI

# 🔑 Load environment variables
load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# 🌐 Streamlit config
st.set_page_config(page_title="StartupDoc AI", page_icon="📘", layout="wide")

# ===============================
# 🧭 Sidebar Info
# ===============================
with st.sidebar:
    st.title("📘 StartupDoc AI")
    st.info("⚡ MCA Project\n🎯 Legal PDF Assistant\n🚀 Built by **Sanya Bhatia**")

# ===============================
# 🗂 Tabs Setup
# ===============================
tab1, tab2, tab3 = st.tabs(["💬 Legal Q&A", "📁 Upload & Summarize", "❓ Ask from Document"])

file_text = ""  # Global for all tabs

# ===============================
# 💬 Tab 1: Legal Q&A
# ===============================
with tab1:
    st.header("💬 Ask a Legal Question")
    q1 = st.text_area("Ask here:", placeholder="E.g. What are the steps for GST registration?")
    if st.button("Get Answer", use_container_width=True):
        if q1.strip():
            with st.spinner("🧠 Thinking..."):
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful Indian legal assistant for startup founders."},
                        {"role": "user", "content": q1}
                    ],
                    temperature=0.4,
                    max_tokens=800
                )
                st.success("✅ Answer")
                st.markdown(response.choices[0].message.content)
        else:
            st.warning("❗ Please type a question.")

# ===============================
# 📁 Tab 2: Upload & Summarize
# ===============================
with tab2:
    import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import os

# Constants
MAX_FILE_SIZE_MB = 5  # Maximum file size in MB

# Function to check if the file is a valid PDF or DOCX
def is_valid_file(uploaded_file):
    return uploaded_file.type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# Function to extract text from PDF files
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error while extracting text from PDF: {e}")
        return ""

# Function to extract text from DOCX files
def extract_text_from_docx(file):
    try:
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error while extracting text from DOCX: {e}")
        return ""

# File uploader
uploaded_file = st.file_uploader("Upload PDF or DOCX file", type=["pdf", "docx"])

if uploaded_file:
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)  # Convert bytes to MB
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error("File size exceeds 5 MB limit.")
    else:
        # Validate file type
        if is_valid_file(uploaded_file):
            # Extract text based on file type
            text = ""
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text_from_docx(uploaded_file)

            # Log extracted text to console for debugging
            if text:
                st.write("Extracted Text:")
                st.text_area("Text Output", text, height=300)
            else:
                st.warning("No text was extracted from the file.")
        else:
            st.error("Invalid file type. Please upload a PDF or DOCX file.")
else:
    st.info("Please upload a PDF or DOCX file to get started.")

# Button to generate summary (placeholder)
if st.button("Generate Summary"):
    st.success("Summary Ready!")



    


# ===============================
# ❓ Tab 3: Ask From Document
# ===============================
with tab3:
    st.header("❓ Ask Questions About This Document")

    if file_text.strip():
        doc_q = st.text_input("Ask a question based on uploaded document")
        if st.button("🔍 Ask From Document", use_container_width=True):
            if doc_q.strip():
                with st.spinner("💬 Generating response..."):
                    prompt = f"Document Content:\n{file_text[:3000]}\n\nQuestion: {doc_q}"
                    response = client.chat.completions.create(
                        model=deployment_name,
                        messages=[
                            {"role": "system", "content": "You're a legal document analyst helping startups."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                        max_tokens=800
                    )
                    st.success("✅ Answer:")
                    st.markdown(response.choices[0].message.content)
            else:
                st.warning("❗ Please ask something.")
    else:
        st.info("📁 Upload and extract a document in Tab 2 first.")

# ===============================
# ✅ Footer
# ===============================
st.markdown("---")
st.caption("✨ MCA Project | Made with ❤️ by Sanya Bhatia")

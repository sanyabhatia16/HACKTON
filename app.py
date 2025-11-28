import streamlit as st
import os
import fitz  # PyMuPDF
import docx2txt
from dotenv import load_dotenv
from openai import AzureOpenAI
from PyPDF2 import PdfReader
from docx import Document

# =========================================================
# ✅ Load Environment Variables
# =========================================================
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# =========================================================
# 🌐 Streamlit Config
# =========================================================
st.set_page_config(page_title="StartupDoc AI", page_icon="📘", layout="wide")

# =========================================================
# 🧭 Sidebar
# =========================================================
with st.sidebar:
    st.title("📘 StartupDoc AI")
    st.info("⚡ MCA Project\n🎯 Legal PDF Assistant\n🚀 Built by **Sanya Bhatia**")

# Global variable shared across tabs
file_text = ""

# =========================================================
# 🗂 Tabs
# =========================================================
tab1, tab2, tab3 = st.tabs(["💬 Legal Q&A", "📁 Upload & Summarize", "❓ Ask from Document"])


# =========================================================
# 💬 TAB 1: Ask General Legal Questions
# =========================================================
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


# =========================================================
# 📁 TAB 2: Upload & Summarize
# =========================================================
with tab2:
    st.header("📁 Upload Document")

    MAX_FILE_SIZE_MB = 5

    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])

    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error("❗ File size exceeds 5MB limit.")
        else:
            text = ""

            # ===== Extract PDF =====
            if uploaded_file.type == "application/pdf":
                try:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        text += (page.extract_text() or "") + "\n"
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")

            # ===== Extract DOCX =====
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                try:
                    doc = Document(uploaded_file)
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                except Exception as e:
                    st.error(f"Error reading DOCX: {e}")

            if text.strip():
                st.success("✅ Text Extracted")
                st.text_area("Extracted Text", text, height=300)
                file_text = text  # Save to global variable
            else:
                st.warning("❗ No text extracted.")

    # ===== Summary Button =====
    if st.button("Generate Summary"):
        if file_text.strip():
            with st.spinner("📝 Summarizing..."):
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "system", "content": "Summarize documents for Indian legal and startup use cases."},
                        {"role": "user", "content": f"Summarize this document:\n\n{file_text[:8000]}"}
                    ],
                    temperature=0.3,
                    max_tokens=700
                )
                st.success("📄 Summary")
                st.markdown(response.choices[0].message.content)
        else:
            st.warning("❗ Upload a document first.")


# =========================================================
# ❓ TAB 3: Ask Questions FROM Document
# =========================================================
with tab3:
    st.header("❓ Ask Questions About This Document")

    if file_text.strip():
        doc_q = st.text_input("Ask something about your document")
        if st.button("🔍 Ask From Document", use_container_width=True):
            if doc_q.strip():
                with st.spinner("💬 Analyzing..."):
                    prompt = f"Document:\n{file_text[:3000]}\n\nQuestion: {doc_q}"

                    response = client.chat.completions.create(
                        model=deployment_name,
                        messages=[
                            {"role": "system", "content": "You're a legal document analyst for startup founders."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                        max_tokens=800
                    )
                    st.success("✅ Answer:")
                    st.markdown(response.choices[0].message.content)
            else:
                st.warning("❗ Please type a question.")
    else:
        st.info("📁 Upload a document in Tab 2 first.")


# =========================================================
# Footer
# =========================================================
st.markdown("---")
st.caption("✨ MCA Project | Made with ❤️ by Sanya Bhatia")

import streamlit as st
import os
from dotenv import load_dotenv
from google import genai  # Google Gemini SDK
from PyPDF2 import PdfReader
from docx import Document

# =========================================================
# ✅ Load Environment Variables
# =========================================================
load_dotenv()

# Ensure required key exists
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("❗ Missing Gemini API key in the .env file.")
    st.stop()

# =========================================================
# ⚙️ FIXED Gemini Client Setup (Using GenAI SDK)
# =========================================================
client = genai.Client(api_key=GEMINI_API_KEY)

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

file_text = ""  # shared text

# =========================================================
# 🗂 Tabs
# =========================================================
tab1, tab2, tab3 = st.tabs(
    ["💬 Legal Q&A", "📁 Upload & Summarize", "❓ Ask from Document"]
)

# =========================================================
# 💬 TAB 1: Ask General Legal Questions
# =========================================================
with tab1:
    st.header("💬 Ask a Legal Question")
    q1 = st.text_area(
        "Ask here:", placeholder="E.g. What are the steps for GST registration?"
    )

    if st.button("Get Answer", use_container_width=True):
        if q1.strip():
            with st.spinner("🧠 Thinking..."):
                try:
                    # Using the GenAI client to get a response
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",  # Replace with the specific model name
                        contents=q1,
                    )
                    st.success("✅ Answer")
                    st.markdown(response.text)  # Output the answer from GenAI
                except Exception as e:
                    st.error(f"❗ Gemini API Error: {e}")
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

            if uploaded_file.type == "application/pdf":
                try:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        text += (page.extract_text() or "") + "\n"
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")

            elif (
                uploaded_file.type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                try:
                    doc = Document(uploaded_file)
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                except Exception as e:
                    st.error(f"Error reading DOCX: {e}")

            if text.strip():
                st.success("✅ Text Extracted")
                st.text_area("Extracted Text", text, height=300)
                file_text = text
            else:
                st.warning("❗ No text extracted.")

    if st.button("Generate Summary"):
        if file_text.strip():
            with st.spinner("📝 Summarizing..."):
                try:
                    # Using the GenAI client to generate a summary
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",  # Replace with the specific model name
                        contents=f"Summarize this document:\n\n{file_text[:8000]}",  # Ensure the content fits within API limits
                    )
                    st.success("📄 Summary")
                    st.markdown(response.text)  # Output the summary from GenAI
                except Exception as e:
                    st.error(f"❗ Gemini API Error: {e}")
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
                    try:
                        # Using the GenAI client to get a response from the document
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",  # Replace with the specific model name
                            contents=prompt,
                        )
                        st.success("✅ Answer:")
                        st.markdown(response.text)  # Output the answer from GenAI
                    except Exception as e:
                        st.error(f"❗ Gemini API Error: {e}")
            else:
                st.warning("❗ Please type a question.")
    else:
        st.info("📁 Upload a document in Tab 2 first.")

# =========================================================
# Footer
# =========================================================
st.markdown("---")
st.caption("✨ MCA Project | Made with ❤️ by Sanya Bhatia")

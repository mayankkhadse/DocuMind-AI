import streamlit as st

from pdf_loader import load_pdf
from utils import chunk_text
from vector_store import create_vectorstore
from rag import get_rag_chain

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.title("📄 DocuMind AI")
    st.markdown("---")

    st.write(
        "Upload one or more PDF documents and ask questions about them."
    )

    st.markdown("### ✨ Features")

    st.write("✅ Multiple PDF Upload")
    st.write("✅ AI-powered Answers")
    st.write("✅ Source References")
    st.write("✅ Chat History")
    st.write("✅ Download Chat")

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown("""
<div style='text-align:center; padding:20px'>
    <h1>📄 DocuMind AI</h1>
    <h4>Your AI-powered PDF Assistant</h4>
    <p>Upload PDFs and ask intelligent questions instantly.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# PDF UPLOADER
# ---------------------------------------------------
uploaded_files = st.file_uploader(
    "📂 Upload PDF Files",
    type="pdf",
    accept_multiple_files=True
)

# ---------------------------------------------------
# PROCESS PDFs
# ---------------------------------------------------
if uploaded_files:

    st.success(
        f"✅ {len(uploaded_files)} PDF(s) uploaded successfully"
    )

    with st.expander("📂 Uploaded Files"):
        for file in uploaded_files:
            st.write("📄", file.name)

    all_text = ""

    # Read all PDFs
    with st.spinner("📚 Reading PDFs..."):
        for uploaded_file in uploaded_files:
            text = load_pdf(uploaded_file)
            all_text += text + "\n"

    # Create chunks
    chunks = chunk_text(all_text)

    # Create vector database
    with st.spinner("🧠 Creating knowledge base..."):
        vectorstore = create_vectorstore(chunks)

    # Create RAG chain
    rag_chain = get_rag_chain(vectorstore)

    # ---------------------------------------------------
    # SHOW PREVIOUS CHAT HISTORY
    # ---------------------------------------------------
    for msg in st.session_state.messages:

        with st.chat_message("user"):
            st.write(msg["question"])

        with st.chat_message("assistant"):
            st.write(msg["answer"])

    # ---------------------------------------------------
    # CHAT INPUT
    # ---------------------------------------------------
    query = st.chat_input(
        "Ask anything about your PDFs..."
    )

    if query:

        with st.chat_message("user"):
            st.write(query)

        with st.spinner(
            "🧠 Analyzing document and generating answer..."
        ):

            response = rag_chain.invoke(query)

        with st.chat_message("assistant"):
            st.write(response)

        # Save chat history
        st.session_state.messages.append({
            "question": query,
            "answer": response
        })

        # ---------------------------------------------------
        # SOURCES
        # ---------------------------------------------------
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 3}
        )

        docs = retriever.invoke(query)

        if docs:
            with st.expander("📚 Sources Used"):

                for i, doc in enumerate(docs):

                    st.markdown(f"### Source {i+1}")

                    source_text = doc.page_content

                    if len(source_text) > 600:
                        source_text = source_text[:600] + "..."

                    st.write(source_text)

# ---------------------------------------------------
# DOWNLOAD CHAT
# ---------------------------------------------------
if st.session_state.messages:

    chat_text = ""

    for msg in st.session_state.messages:

        chat_text += (
            f"Question: {msg['question']}\n"
        )

        chat_text += (
            f"Answer: {msg['answer']}\n\n"
        )

    st.download_button(
        "📥 Download Chat History",
        chat_text,
        file_name="chat_history.txt"
    )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

def get_rag_chain(vectorstore):
    
    print("MODEL USED = llama-3.3-70b-versatile")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

    print("RAG.PY IS RUNNING")
    print("MODEL =", llm.model_name)

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 10}
        )

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])
    
    prompt = ChatPromptTemplate.from_template("""
You are an intelligent document assistant.

Answer the question strictly from the provided context.

If the answer is not present in the context, say:

"I could not find the answer in the uploaded documents."

Context:
{context}

Question:
{question}

Answer:
""")

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": lambda x: x
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def get_llm(vectorstore):
    return get_rag_chain(vectorstore)

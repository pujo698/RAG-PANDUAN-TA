from utils.loader import load_pdf
from utils.splitter import split_document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import *
docs = load_pdf(PDF_PATH)
chunks = split_document(docs)
embedding = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory=CHROMA_PATH
)
print("===================================")
print("Jumlah halaman :", len(docs))
print("Jumlah chunk :", len(chunks))
print("Database berhasil dibuat")
print("===================================")
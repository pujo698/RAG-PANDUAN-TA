from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

from config import *
from prompt import SYSTEM_PROMPT


class RAGSystem:

    def __init__(self):

        self.embedding = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        self.db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=self.embedding
        )

        self.retriever = self.db.as_retriever(
            search_kwargs={
                "k": TOP_K
            }
        )

        self.llm = OllamaLLM(
            model=LLM_MODEL,
            temperature=0
        )

    def ask(self, question):

        docs = self.retriever.invoke(question)

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        prompt = f"""
{SYSTEM_PROMPT}

==========================
DOKUMEN
==========================

{context}

==========================
PERTANYAAN
==========================

{question}

==========================
JAWABAN
==========================
"""

        answer = self.llm.invoke(prompt)

        return answer, docs
from rag import RAGSystem
rag = RAGSystem()
question = st.chat_input("Masukkan pertanyaan")
if question:
    answer, docs = rag.ask(question)
    st.write(answer)
import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template


def get_saved_pdf_names():
    if os.path.exists("EmbeddingsDB"):
        return [name for name in os.listdir("EmbeddingsDB") if os.path.isdir(os.path.join("EmbeddingsDB", name))]
    return []


def load_vectorstore(pdf_name):
    vectorstore = FAISS.load_local(
        f"EmbeddingsDB/{pdf_name}",
        OpenAIEmbeddings(),
        allow_dangerous_deserialization=True
    )
    return vectorstore


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks, pdf_name):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    save_path = f"EmbeddingsDB/{pdf_name}"
    os.makedirs(save_path, exist_ok=True)
    vectorstore.save_local(save_path)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
    )
    return conversation_chain




def handle_userinput(user_question):
    
    if st.session_state.conversation is not None:
        response = st.session_state.conversation({'question': user_question})
        
        # Ensure chat history is initialized
        if "chat_history" not in st.session_state or st.session_state.chat_history is None:
            st.session_state.chat_history = []
        
        # Update chat history
        st.session_state.chat_history.extend(response['chat_history'])
    else:
        st.write("Please upload or select a PDF to start a conversation.")




def submit():
    user_question = st.session_state.widget.strip()
    if user_question:  
        st.session_state.user_question = user_question
        handle_userinput(user_question)
    st.session_state.widget = ""  


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with your PDFs", page_icon=":books:")

    st.write(css, unsafe_allow_html=True)

   
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state or st.session_state.chat_history is None:
        st.session_state.chat_history = []
    if "widget" not in st.session_state:
        st.session_state.widget = ""
    if "user_question" not in st.session_state:
        st.session_state.user_question = None

    st.header("Chat with your PDFs")

    
    st.text_input("Ask a question:", key="widget", on_change=submit)

    
    if st.session_state.chat_history:
        for i, message in enumerate(st.session_state.chat_history[::-1]):
            if i % 2 == 0: 
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:  
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

   
    with st.sidebar:
        st.subheader("Your PDFs")
        saved_pdfs = get_saved_pdf_names()
        selected_pdf = st.selectbox("Select an existing PDF", options=["None"] + saved_pdfs)

        if selected_pdf != "None":
            vectorstore = load_vectorstore(selected_pdf)
            st.session_state.conversation = get_conversation_chain(vectorstore)
            st.write(f"Now using {selected_pdf}")
        else:
            pdf_docs = st.file_uploader("Upload your PDFs here", accept_multiple_files=True)
            if st.button("Upload"):
                with st.spinner("Processing"):
                    if pdf_docs:
                        raw_text = get_pdf_text(pdf_docs)
                        text_chunks = get_text_chunks(raw_text)
                        pdf_name = os.path.splitext(pdf_docs[0].name)[0]
                        vectorstore = get_vectorstore(text_chunks, pdf_name)
                        st.session_state.conversation = get_conversation_chain(vectorstore)
                        st.write(f"Embeddings created for {pdf_name}")


if __name__ == '__main__':
    main()
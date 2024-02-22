import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
from fastapi import  UploadFile

from database.db_models import Quiz
from loaders import PDFMinerPagesLoader


def add_quiz_to_vectorstore(source_file: UploadFile, new_quiz: Quiz, file_hash: str ):
    
    documents=get_documents_from_file(source_file=source_file, file_hash=file_hash)
    index_name, namespace, embeddings = get_pinecone_config(quiz=new_quiz)
    
    vectorstore = Pinecone.from_documents(
        documents=documents, 
        embedding=embeddings, 
        index_name=index_name, 
        namespace=namespace)
    return vectorstore
    

def _get_raw_pdf_text(source_file: UploadFile, file_hash: str):
    loader = PDFMinerPagesLoader(file=source_file, file_name=source_file.filename, file_hash=file_hash)
    return loader.load()


def get_pinecone_config(quiz: Quiz):
    index_name = os.getenv("PINECONE_INDEX_NAME")
    namespace = os.getenv("PINECONE_NAMESPACE") + f'{quiz.quiz_id}'
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
    
    return index_name, namespace , embeddings


def get_documents_from_file(source_file: UploadFile, file_hash: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len, is_separator_regex=False)
    split_documents = text_splitter.split_documents(_get_raw_pdf_text(source_file=source_file, file_hash=file_hash))

    return split_documents
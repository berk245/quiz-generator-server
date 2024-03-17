import os
from fastapi import UploadFile
from models.db_models import Quiz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
from config.cloudwatch_logger import cloudwatch_logger
import time
from loaders import pdf_loader
from constants import MAX_RETRY_ATTEMPTS, RETRY_DELAY_SECONDS


def add_quiz_to_vectorstore(source_file: UploadFile, new_quiz: Quiz, file_hash: str):
    cloudwatch_logger.info('Trying to create the vector store.')
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            documents = get_documents_from_file(source_file=source_file, file_hash=file_hash)
            cloudwatch_logger.info(f'Created documents from the file.')
            index_name, namespace, embeddings = get_pinecone_config(quiz=new_quiz)
            cloudwatch_logger.info(f'Pinecone config is setup name: {index_name}, namespace: {namespace}, embeddings: {embeddings}.')

            vectorstore = Pinecone.from_documents(
                documents=documents, 
                embedding=embeddings, 
                index_name=index_name, 
                namespace=namespace)
            cloudwatch_logger.info('Vector store created successfully.')
            return vectorstore

        except Exception as e:
            if attempt == MAX_RETRY_ATTEMPTS - 1:
                cloudwatch_logger.error(f'Failed to create the vector store after {MAX_RETRY_ATTEMPTS} attempts: {e}')
                raise
            else:
                cloudwatch_logger.warning(f'Connection error encountered, attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}: {e}. Retrying in {(attempt+1) * RETRY_DELAY_SECONDS} seconds...')
                time.sleep((attempt+1) * RETRY_DELAY_SECONDS)
    

def get_documents_from_file(source_file: UploadFile, file_hash: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len,
                                                   is_separator_regex=False)
    documents = pdf_loader.get_documents(source_file=source_file, file_hash=file_hash)
    split_documents = text_splitter.split_documents(documents=documents)

    return split_documents


def get_pinecone_config(quiz: Quiz):
    index_name = os.getenv("PINECONE_INDEX_NAME")
    namespace = os.getenv("PINECONE_NAMESPACE") + f'{quiz.quiz_id}'
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
    
    return index_name, namespace, embeddings


def get_retriever(quiz: Quiz):
    try:
        index_name, namespace, embeddings = get_pinecone_config(quiz=quiz)
        cloudwatch_logger.info(f'Getting retriever index name: {index_name}')
        vectorstore = Pinecone.from_existing_index(
            index_name=index_name,
            namespace=namespace,
            embedding=embeddings
        )
        retriever = vectorstore.as_retriever()
        return retriever
    except Exception as e:
        cloudwatch_logger.error(f'Error in _get_retriever method: {str(e)}')
        raise e



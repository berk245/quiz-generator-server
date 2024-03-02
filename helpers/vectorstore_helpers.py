import os
from typing import List
from fastapi import UploadFile
from database.db_models import Quiz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from loaders import PDFMinerPagesLoader


def add_quiz_to_vectorstore(source_file: UploadFile, new_quiz: Quiz, file_hash: str):
    
    documents = get_documents_from_file(source_file=source_file, file_hash=file_hash)
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
    
    return index_name, namespace, embeddings


def get_documents_from_file(source_file: UploadFile, file_hash: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len,
                                                   is_separator_regex=False)
    split_documents = text_splitter.split_documents(_get_raw_pdf_text(source_file=source_file, file_hash=file_hash))

    return split_documents


def _get_retriever(quiz: Quiz):
    index_name, namespace, embeddings = get_pinecone_config(quiz=quiz)
    vectorstore = Pinecone.from_existing_index(
        index_name=index_name,
        namespace=namespace,
        embedding=embeddings
    )
    retriever = vectorstore.as_retriever()
    return retriever


class GeneratedQuestion(BaseModel):
    question_id: str = Field(description='A unique identifier for each generated question. Could be the index.')
    question_text: str = Field(description="The question to be added to the quiz")
    multiple_choices: str = Field(description="A string that includes four, comma separated potential answers to the "
                                              "question")
    correct_answer: str = Field(description='Correct answer to the question. Must be one of the four multiple choices.')
    question_type: str = Field(description='Always set it as "multi"')


class GeneratedQuestions(BaseModel):
    questions: List[GeneratedQuestion] = Field(description="List of generated questions in the specified amount")


def get_conversation_chain(quiz: Quiz):
    retriever = _get_retriever(quiz=quiz)

    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI().bind_tools([GeneratedQuestions])

    chain = (
        {"context": retriever, 'question': RunnablePassthrough()}
        | prompt
        | model
        | JsonOutputToolsParser()
    )

    return chain

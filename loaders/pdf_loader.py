import io
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from langchain.docstore.document import Document
from fastapi import UploadFile


def get_documents(source_file: UploadFile, file_hash: str):
    documents = []
    
    file_content = source_file.file.read()
    
    with io.BytesIO(file_content) as file:
        for i, page_layout in enumerate(extract_pages(file)):
                page_content = ''
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        page_content += '\n'
                        page_content += element.get_text()
                if len(page_content.strip()) < 10:
                    continue
                document = Document(
                    page_content=page_content,
                    metadata={'source': '{} (page {})'.format(source_file.filename, i + 1),
                              'page': i + 1,
                              'source_file_hash': file_hash})
                documents.append(document)
        print(f'Returning documents {documents}')
        return documents
import io
from typing import List

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader


class PDFMinerPagesLoader(BaseLoader):
    def __init__(self, file, file_name, file_hash=''):
        self.file_hash = file_hash
        self.file_name = file_name
        self.pdf_file_obj = file.file.read()

    def load(self) -> List[Document]:
        documents = []
        with io.BytesIO(self.pdf_file_obj) as file:
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
                    metadata={'source': '{} (page {})'.format(self.file_name, i + 1),
                              'page': i + 1,
                              'source_file_hash': self.file_hash})
                documents.append(document)
        return documents

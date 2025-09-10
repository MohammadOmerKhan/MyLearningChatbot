import os
import uuid
from typing import List, Dict
from datetime import datetime
import PyPDF2
from docx import Document as DocxDocument
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    def __init__(self):
        self.embedding_model = None

    def _get_embedding_model(
        self,
    ):  # get the embedding model if it is not already loaded. This is a lazy loading technique to avoid loading the model until it is needed.
        if self.embedding_model is None:
            self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
        return self.embedding_model

    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        with open(
            file_path, "rb"
        ) as file:  # rb is read binary because pdf files are binary
            pdf_reader = PyPDF2.PdfReader(
                file
            )  # PdfReader is a class in PyPDF2 that reads pdf files
            for page in pdf_reader.pages:  # for each page
                text += (
                    page.extract_text() + "\n"
                )  # extract text from page and add it to the text variable. also add a new line

        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        doc = DocxDocument(
            file_path
        )  # document is a class in docx that reads docx files
        text = ""
        for paragraph in doc.paragraphs:  # for each paragraph in the document
            text += (
                paragraph.text + "\n"
            )  # add the text from the paragraph to the text variable and add a new line
        return text  # one big string

    def chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> List[
        str
    ]:  # chunking text makes it easier for both sentecetransformers and LLMs to read

        chunks = []
        start = 0

        while start < len(text):  # slice text from start to end
            end = start + chunk_size
            chunk = text[start:end]  # slciing text from start to end

            if end < len(text):
                last_period = chunk.rfind(
                    "."
                )  # if not at end of text cut chunk at last period
                if (
                    last_period > chunk_size * 0.7
                ):  # but make sure the chunk is at least 70% of the chunk size
                    chunk = chunk[: last_period + 1]  # cut at last period
                    end = start + last_period + 1  # move end to after the last period

            chunks.append(chunk.strip())  # strip the whitespaces and add to chunks list
            start = end - overlap  # move start to after the last period
        return [
            chunk for chunk in chunks if chunk.strip()
        ]  # remove empty chunks and return the list

    async def process_document(self, file_path: str, filename: str) -> str:
        try:
            if filename.lower().endswith(
                ".pdf"
            ):  # make lowercase and check if it ends with pdf
                text = self.extract_text_from_pdf(
                    file_path
                )  # call the extract_text_from_pdf function
            elif filename.lower().endswith(
                (".docx", ".doc")
            ):  # make lowercase and check if it ends with docx or doc
                text = self.extract_text_from_docx(
                    file_path
                )  # call the extract_text_from_docx function
            else:
                return f"Unsupported file type: {filename}"

            chunks = self.chunk_text(
                text
            )  # call the chunk_text function to chunk the text

            embedding_model = self._get_embedding_model()

            from main import database

            collection = database.document_chunks

            saved_chunks = 0
            for i, chunk in enumerate(chunks):

                try:

                    embedding = embedding_model.embed_query(
                        chunk
                    )  # creating vector representation by passing single chunk as list to embedding model

                    # Save to database
                    doc_dict = {
                        "text": chunk,
                        "filename": filename,
                        "chunk_index": i,
                        "timestamp": datetime.utcnow(),
                        "embedding": embedding,
                    }
                    await collection.insert_one(doc_dict)
                    saved_chunks += 1
                except Exception as e:
                    print(f"Error processing chunk {i}: {e}")
                    continue

            return (
                f"Document '{filename}' saved to database. Total {saved_chunks} chunks."
            )

        except Exception as e:
            return f"Error processing document: {str(e)}"


document_processor = DocumentProcessor()

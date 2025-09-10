import os
from typing import List, Dict
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


class RAGTool:
    def __init__(self):
        self.name = "RAGTool"
        self.description = "Retrieve, augment and generate"
        self.embeddingModel = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )  # OpenAI embeddings for better performance  # Secret sauce that creates the vector embeddings for the documents

    async def search_documents(self, query: str, limit: int = 5):
        try:
            queryEmbedding = self.embeddingModel.embed_query(
                query
            )  # uses the sauce to create the vector embedding for the query

            from main import database

            collection = database.document_chunks  # Fixed collection name

            cursor = collection.find({})
            documents = await cursor.to_list(length=None)

            results = []
            for doc in documents:
                if "embedding" in doc:
                    similarity = self._cosine_similarity(
                        queryEmbedding, doc["embedding"]
                    )

                    doc_obj = Document(
                        page_content=doc["text"],
                        metadata={
                            "filename": doc["filename"],
                            "chunk_index": doc["chunk_index"],
                            "similarity": similarity,
                        },
                    )
                    results.append(doc_obj)

            results.sort(key=lambda x: x.metadata["similarity"], reverse=True)
            return results[:limit]

        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def _cosine_similarity(self, a, b):
        a = np.array(a)  # converting the vecotr into a numpy array
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        """calculating the cosine similarity by taking the dot product of 
    the two vector numpy arrays and dividing it by the product of 
    the norms(magnitude) of the two vectors. The formula for cosine 
    similarity is (A.B) / (||A|| * ||B||). This gives us 3 values, 0, 1, and -1. 
    1 means they have the same direction so same semantic meaning, 0 means they are perpendicular
    so no similarity, and -1 means they have opposite directions so opposite semantic meaning."""

    def format_results(self, results: List[Document]) -> str:
        if not results:
            return "No relevant documents found."

        formatted = "Relevant document information:\n"
        for i, doc in enumerate(results, 1):
            filename = doc.metadata.get("filename", "Unknown")
            similarity = doc.metadata.get("similarity", 0)
            formatted += f"{i}. From {filename} (similarity: {similarity:.2f}):\n"
            formatted += f"   {doc.page_content[:300]}...\n\n"

        return formatted


# Create an instance of the RAG tool
rag_tool = RAGTool()

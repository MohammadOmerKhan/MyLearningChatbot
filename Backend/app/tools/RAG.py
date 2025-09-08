import os
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGTool:
    def __init__(self):
        self.name = "RAGTool"
        self.description = "Retrieve, augment and generate"
        self.embeddingModel = SentenceTransformer(
            "all-Mini-L6-v2"
        )  # Secret sauce that creates the vector embeddings for the documents

    async def search_documents(self, query: str, limit: int = 5):
        try:
            queryEmbedding = self.embeddingModel.encode([query])[
                0
            ]  # uses the sauce to create the vector embedding for the query

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

                    results.append(
                        {
                            "text": doc["text"],
                            "filename": doc["filename"],
                            "similarity": similarity,
                            "chunk_index": doc["chunk_index"],
                        }
                    )

            results.sort(key=lambda x: x["similarity"], reverse=True)
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


    def format_results(self, results: List[Dict]) -> str:
        if not results:
            return "No relevant documents found."

        formatted = "Relevant document information:\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. From {result['filename']} (similarity: {result['similarity']:.2f}):\n"
            formatted += f"   {result['text'][:300]}...\n\n"

        return formatted


# Create an instance of the RAG tool
rag_tool = RAGTool()

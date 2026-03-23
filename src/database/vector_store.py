import chromadb
from chromadb.utils import embedding_functions
import os
import json

class VectorStore:
    def __init__(self, persist_directory="data/database"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        # Use a default embedding function (could be OpenAI or local)
        # For demo, using default sentence-transformers or consistent one
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.fund_collection = self.client.get_or_create_collection(
            name="mutual_funds",
            embedding_function=self.embedding_fn
        )
        self.reg_collection = self.client.get_or_create_collection(
            name="regulations",
            embedding_function=self.embedding_fn
        )

    def add_fund_data(self, fund_id, text, metadata):
        self.fund_collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[fund_id]
        )

    def add_regulations(self, chunks):
        ids = [f"reg_{i}" for i in range(len(chunks))]
        self.reg_collection.add(
            documents=chunks,
            ids=ids
        )

    def query(self, query_text, n_results=3):
        fund_results = self.fund_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        reg_results = self.reg_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return fund_results, reg_results

if __name__ == "__main__":
    # Test
    vs = VectorStore()
    print("Vector Store initialized.")

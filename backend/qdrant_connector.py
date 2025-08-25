from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from typing import Any
import uuid


class QdrantConnector:
      
    def __init__(
        self, 
        qdrant_host: str = "localhost", 
        qdrant_port: int = 6333,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        collection_name: str = "pdf_documents"
    ):
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.embedding_model = SentenceTransformer(embedding_model)
        self.collection_name = collection_name

    def _get_sentence_splitter(self, chunk_size: int, overlap: int) -> RecursiveCharacterTextSplitter:
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,     # Number of characters per chunk
            chunk_overlap=overlap,   # Overlap to maintain context
            separators=["\n\n", "\n", ".", " ", ""]  # Prioritize splitting on paragraph, newline, and sentence boundaries
        )
    
    def recreate_collection(self):
        """Check and create collection in Qdrant if it doesn't exist"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            if self.collection_name in collection_names:
                print(f"Collection '{self.collection_name}' already exists, deleting it for fresh start.")
                self.qdrant_client.delete_collection(collection_name=self.collection_name)
            vector_size = self.embedding_model.get_sentence_embedding_dimension()
            
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection '{self.collection_name}'")
        except Exception as e:
            print(f"Error creating collection: {e}")

    def upload_to_qdrant(
        self, 
        text: str,
        metadata: dict[str, Any] = None
    ) -> None:
        """
        Upload chunks and embeddings to Qdrant
        
        Args:
            chunks: List of text chunks
            embeddings: Embeddings for chunks
            metadata: Additional metadata (e.g., filename, page)
        
        Returns:
            List of IDs of added points
        """
        sentence_chunks = self._get_sentence_splitter(metadata["chunk_size"], metadata["overlap"]).split_text(text)
        print(f"text spliited into {len(sentence_chunks)} chunks")
        for i, chunk in enumerate(sentence_chunks):
            point_id = str(uuid.uuid4())
            embedding = self.embedding_model.encode(chunk)

            payload = {
                "text": chunk,
                "chunk_index": i,
                "chunk_length": len(chunk)
            }
            if metadata:
                payload.update(metadata)

            point = PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload=payload
            )
            try:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=[point]
                )
                print(f"Uploaded point {point_id} to Qdrant")
            except Exception as e:
                print(f"Error uploading to Qdrant: {e}")
                return None

    def search_similar(self, query: str, limit: int = 5) -> list[dict]:
            """
            Search for similar chunks to query
            
            Args:
                query: Text query
                limit: Maximum number of results
            
            Returns:
                List of similar chunks with metadata
            """
            # Create embedding for query
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit
            )
            
            results = []
            for result in search_results:
                results.append({
                    "text": result.payload["text"],
                    "score": result.score,
                    "file_name": result.payload.get("file_name", "unknown"),
                    "chunk_index": result.payload.get("chunk_index", 0)
                })
            
            return results

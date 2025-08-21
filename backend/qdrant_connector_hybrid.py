from qdrant_client import QdrantClient
from qdrant_client import models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Any
import uuid


class QdrantConnectorHybrid:
      
    def __init__(
        self, 
        qdrant_host: str = "localhost", 
        qdrant_port: int = 6333,
        embedding_model: str = "jinaai/jina-embeddings-v2-small-en",
        collection_name: str = "pdf_documents"
    ):
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self._ensure_collection_exists()

    @property
    def sentence_splitter(self):
        return RecursiveCharacterTextSplitter(
            chunk_size=500,     # Number of characters per chunk
            chunk_overlap=50,   # Overlap to maintain context
            separators=["\n\n", "\n", ".", " "]  # Prioritize splitting on paragraph, newline, and sentence boundaries
        )
    
    def _ensure_collection_exists(self):
        """Check and create collection in Qdrant if it doesn't exist"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
        
                self.qdrant_client.create_collection(
                    collection_name="pdf_documents_sparse_and_dense",
                    vectors_config={
                        # Named dense vector for jinaai/jina-embeddings-v2-small-en
                        "jina-small": models.VectorParams(
                            size=512,
                            distance=models.Distance.COSINE,
                        ),
                    },
                    sparse_vectors_config={
                        "bm25": models.SparseVectorParams(
                            modifier=models.Modifier.IDF,
                        )
                    }
)
                print(f"Created collection '{self.collection_name}'")
            else:
                print(f"Collection '{self.collection_name}' already exists")
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
        sentence_chunks = self.sentence_splitter.split_text(text)
        print(f"text spliited into {len(sentence_chunks)} chunks")
        for i, chunk in enumerate(sentence_chunks):
            point_id = str(uuid.uuid4())
            payload = {
                "text": chunk,
                "chunk_index": i,
                "chunk_length": len(chunk)
            }
            if metadata:
                payload.update(metadata)
            try:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        models.PointStruct(
                            id=uuid.uuid4().hex,
                            vector={
                                "jina-small": models.Document(
                                    text=chunk,
                                    model=self.embedding_model,
                                ),
                                "bm25": models.Document(
                                    text=chunk, 
                                    model="Qdrant/bm25",
                                ),
                            },
                            payload=payload
                        )
                    ]
                )
                print(f"Uploaded point {point_id} to Qdrant")
            except Exception as e:
                print(f"Error uploading to Qdrant: {e}")
                return None

    def search_similar(self, query: str, limit: int = 5) -> list[str]:
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    models.Prefetch(
                        query=models.Document(
                            text=query,
                            model=self.embedding_model,
                        ),
                        using="jina-small",
                        limit=(10 * limit),
                    ),
                ],
                query=models.Document(
                    text=query,
                    model="Qdrant/bm25", 
                ),
                using="bm25",
                limit=limit,
                with_payload=True,
            ) 
            return [result.payload["text"] for result in  results.points]

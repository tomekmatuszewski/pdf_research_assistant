import os
from qdrant_connector import QdrantConnector
import PyPDF2


class PDFToQdrant:
    def __init__(self, qdrant_connector: QdrantConnector):
        """
        Initialize PDF to Qdrant processing system
        
        Args:
            qdrant_host: Qdrant server host address
            qdrant_port: Qdrant server port
            embedding_model: Model for creating embeddings
            collection_name: Collection name in Qdrant
        """
        self.qdrant_connector = qdrant_connector
    
    def _extract_pdf(self, pdf_path: str) -> str:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    def process_pdf(
        self, 
        pdf_path: str, 
        chunk_size: int = 1000, 
        overlap: int = 100
    ) -> None:
        print(f"Processing file: {pdf_path}")
        text = self._extract_pdf(pdf_path)
        if not text.strip():
            return {"error": "Failed to extract text from PDF"}
        
        print(f"Extracted {len(text)} characters of text")

        metadata = {
            "file_name": os.path.basename(pdf_path),
            "file_path": pdf_path,
            "chunk_size": chunk_size,
            "overlap": overlap
        }
        
        self.qdrant_connector.upload_to_qdrant(text, metadata)
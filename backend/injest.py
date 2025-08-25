import requests
from pathlib import Path
from urllib.parse import unquote
from pdf_to_qdrant import PDFToQdrant
from qdrant_connector import QdrantConnector
import os

DATA_PATH = Path(__file__).parent.parent / "data"

def download_pdf(url: str, dest_folder: str) -> Path:
    filename = unquote(url.split("/")[-1])
    if not filename.endswith(".pdf"):
        raise ValueError("The URL does not point to a PDF file.")
    filepath = Path(dest_folder) / filename
    print(f"Loading data from: {url}")
    print(f"Saving pdf to: {filepath}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with filepath.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("File downloaded successfully.")
    return filepath

def list_urls(path: str) -> list[str]:
    with open(path) as file:
        text = file.read()
        if text:
            return text.split("\n")
        else:
            return []
        

if __name__ == "__main__":
    urls_path = DATA_PATH / "urls.txt"
    urls = list_urls(urls_path)
    if urls:
        for url in urls:
            download_pdf(url, DATA_PATH)

    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    qdrant_connector = QdrantConnector(qdrant_host=os.getenv("QDRANT_HOST"), embedding_model=embedding_model
                                       )
    qdrant_connector.recreate_collection()

    pdf_processor = PDFToQdrant(qdrant_connector=qdrant_connector)
    for file in DATA_PATH.glob("*.pdf"):
        pdf_processor.process_pdf(file, chunk_size=800, overlap=100)
        


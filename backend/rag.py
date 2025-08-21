from .qdrant_connector import QdrantConnector
import os
import ollama
from ollama import GenerateResponse

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")

def build_prompt(query, search_results):
    prompt_template = """
        nothink/
        You're a pdf research assistant. Answer the QUESTION based on the CONTEXT from the Qdrant database.
        Use only the facts from the CONTEXT when answering the QUESTION.

        QUESTION: {question}

        CONTEXT: x
        {context}
    """.strip()

    prompt = prompt_template.format(question=query, context=search_results).strip()
    return prompt

def rag(query: str, model: str) -> GenerateResponse:
    qdrant_connector = QdrantConnector(qdrant_host=os.getenv("QDRANT_HOST"))
    print("Searching in qdrant db")
    search_result = qdrant_connector.search_similar(query=query)
    ollama_host = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
    client = ollama.Client(host=ollama_host)
    prompt = build_prompt(query, search_result)
    print(prompt)
    response = client.generate(
        model=model,
        prompt=prompt
        
    )
    return response


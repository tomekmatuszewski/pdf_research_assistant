from fastapi import FastAPI
from pydantic import BaseModel
import ollama
from .rag import rag
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")

ollama_host = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

client = ollama.Client(host=ollama_host)

class Prompt(BaseModel):
    model: str
    text: str

app = FastAPI()

@app.get("/healthcheck")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/ask")
def llm(prompt: Prompt):
    response = rag(query=prompt.text, model=prompt.model)
    return response

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import ollama
import concurrent.futures
from .rag import rag, evaluate_relevance, clean_qwen_response
from .db import save_conversation
import os
from time import time

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")

ollama_host = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

client = ollama.Client(host=ollama_host)

class Prompt(BaseModel):
    model: str
    text: str

app = FastAPI()

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def chained_background_tasks(query: str, response: str, model: str, response_time: float):
    """Run evaluate_relevance first, then save_conversations with the result"""
    try:
        print("Evaluating relevance of the answer in background task")
        cleaned_response = clean_qwen_response(response.response)
        relevance_result = evaluate_relevance(query, cleaned_response, model)

        answer_data = {
            "answer": cleaned_response.strip(),
            "model_used": model,
            "response_time": response_time,
            "relevance": relevance_result.get("Relevance", "UNKNOWN"),
            "relevance_explanation": relevance_result.get("Explanation", "No explanation provided"),
        }
        
        print("Saving conversation to the database")
        save_conversation(query, answer_data)
        
    except Exception as e:
        print(f"Error in background tasks: {e}")

@app.get("/healthcheck")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/ask")
def llm(prompt: Prompt):
    start = time()
    response = rag(query=prompt.text, model=prompt.model)
    end = time()
    response_time = end - start
    executor.submit(chained_background_tasks, prompt.text, response, prompt.model, response_time)
    return response

@app.on_event("shutdown")
def shutdown_event():
    executor.shutdown(wait=True)
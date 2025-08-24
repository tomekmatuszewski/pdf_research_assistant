from .qdrant_connector import QdrantConnector
import os
import ollama
import json
import re
from ollama import GenerateResponse

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")

def build_prompt(query, search_results):
    prompt_template = """
        /no_think
        You're a pdf research assistant. Answer the QUESTION based on the CONTEXT from the Qdrant database.
        Use only the facts from the CONTEXT when answering the QUESTION.

        QUESTION: {question}

        CONTEXT: x
        {context}
    """.strip()

    prompt = prompt_template.format(question=query, context=search_results).strip()
    return prompt

def build_evaluation_prompt(query, answer_llm):
    evaluation_prompt_template = """
        /no_think
        You are an expert evaluator for a RAG system.
        Your task is to analyze the relevance of the generated answer to the given question.
        Based on the relevance of the generated answer, you will classify it
        as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

        Here is the data for evaluation:

        Question: {question}
        Generated Answer: {answer_llm}

        Please analyze the content and context of the generated answer in relation to the question
        and provide your evaluation in parsable JSON without using code blocks:

        {{
        "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
        "Explanation": "[Provide a brief explanation for your evaluation]"
        }}
        """.strip()
    evaluation_prompt = evaluation_prompt_template.format(question=query, answer_llm=answer_llm).strip()
    return evaluation_prompt

def clean_qwen_response(text):
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned).strip()
    return cleaned

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

def evaluate_relevance(question: str, answer: str, model: str) -> dict:
    prompt = build_evaluation_prompt(question, answer)
    print("Asking ollama for evaluation with prompt:", prompt)
    ollama_host = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
    client = ollama.Client(host=ollama_host)
    response = client.generate(
        model=model,
        prompt=prompt
    )
    print("Evaluation response:", response.response)
    cleaned = clean_qwen_response(response.response)
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result

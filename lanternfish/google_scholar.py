from llm_client import AsyncLLMClient
import asyncio
from prompts import SYSTEM_GENERATE_QUERIES
from scholarly import scholarly
from pydantic import BaseModel
import pydantic
import logging
import json

class SearchQueries(pydantic.BaseModel):
    queries: list[str]

llm_client = AsyncLLMClient()

def generate_search_prompts(user_prompt):
    return asyncio.run(
        llm_client.get_completion(user_prompt,
                                    system_message=SYSTEM_GENERATE_QUERIES))


def search(prompt, max_n_papers=50):
    search_queries = generate_search_prompts(prompt)

    search_results = []

        
    for paper in scholarly.search_pubs(search_queries):
        if len(search_results) >= max_n_papers:
            break
        if paper not in search_results:
            search_results.append(paper)

    return search_results

if __name__ == "__main__":
    # Example usage
    prompt = "What are the latest advancements in quantum computing?"
    search_results = search(prompt,  max_n_papers=10)
    print("Search results:")
    for result in search_results:
        print(f"Title: {result['bib']['title']}")

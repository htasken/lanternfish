from llm import LLM
from scholarly import scholarly
from pydantic import BaseModel
import pydantic
import logging

class SearchQueries(pydantic.BaseModel):
    queries: list[str]

def generate_search_prompts(user_prompt, model):
    llm = LLM(model=model)
    prompt = f"""Generate three search queries for Google Scholar based on the following description from the user:

{user_prompt}

Together the queries should give all potentiall relevant papers. Search operators may be used if beneficial. The answer must be given in a JSON format.
"""

    messages = [
        {"role": "user", "content": prompt},
    ]
    llm.add_chat_task(messages, format=SearchQueries.model_json_schema())
    response = llm.run_tasks()[0]
    search_queries = SearchQueries.model_validate_json(response.message.content)

    return search_queries.queries

def search(prompt, model, max_n_papers=50):
    search_queries = generate_search_prompts(prompt, model)
    logging.debug(f"Generated search queries: {search_queries}")
    if len(search_queries) != 3:
        logging.warning(f"Expected 3 search queries, but got {len(search_queries)}")
    search_results = []
    for search_prompt in search_queries:
        for paper in scholarly.search_pubs(search_prompt):
            if len(search_results) >= max_n_papers:
                break
            if paper not in search_results:
                search_results.append(paper)

    return search_results

if __name__ == "__main__":
    # Example usage
    prompt = "What are the latest advancements in quantum computing?"
    search_results = search(prompt, "llama3.1", max_n_papers=10)
    print("Search results:")
    for result in search_results:
        print(f"Title: {result['bib']['title']}")

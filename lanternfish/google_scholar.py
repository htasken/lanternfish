
from llm_api import generate_search_prompts
from scholarly import scholarly
import logging

def search(prompt, max_n_papers=50):
    search_queries = generate_search_prompts(prompt)

    search_results = []

    logging.info(f"Searching Google Scholar for at most {max_n_papers} papers")
    
    papers = scholarly.search_pubs(search_queries)
    
    for paper in papers:
        search_results.append(paper)
        if len(search_results) >= max_n_papers:
            break

    logging.info(f"Found {len(search_results)} papers")
    
    return search_results

if __name__ == "__main__":
    # Example usage
    prompt = "What are the latest advancements in quantum computing?"
    search_results = search(prompt,  max_n_papers=10)
    print("Search results:")
    for result in search_results:
        print(f"Title: {result['bib']['title']}")

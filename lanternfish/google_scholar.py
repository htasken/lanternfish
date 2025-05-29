
from llm_api import generate_search_prompts
from scholarly import scholarly
import logging

def search(prompt, max_n_papers=50):
    """Find papers using Google Scholar.

    A LLM is used to generate search terms based on the user's prompt.
    The first search term is the LLM's best initial attempt to find relevant papers.
    For subsequent search terms the LLM is prompted to find relevant papers not
    found by previous searches.

    The first 75% of the returned list of papers are google scholars top
    results for the first search term, the next 15% are the top results from the
    second search term that is not already in the first 75%, and the last 10% are
    the top results from the third search term that is not already in the first 90%.

    Args:
        prompt (str): A description of the what the user is after.
        max_n_papers (int): Maximum number of papers to return.

    Returns:
        list: A list of dictionaries with information about each paper found. 
    """

    print("Generate search terms for Google Scholar...")

    search_queries = []
    search_queries.append(generate_search_prompts(prompt))
    
    for i in range(2):
        new_prompt = f"Description of the papers I want to find: {prompt}\n\nPrevious search queries that have missed some papers:\n"
        for query in search_queries:
            new_prompt += f"- {query}\n"
        new_prompt += "Please generate a new search query that will find more relevant papers."
        search_queries.append(generate_search_prompts(new_prompt))

    search_results = []

    logging_info_queries = "Search queries generated:\n"
    for query in search_queries:
        logging_info_queries += f"- {query}\n"
    logging.info(logging_info_queries)

    print("Searching Google Scholar for papers...")
    logging.info(f"Searching Google Scholar for at most {max_n_papers} papers")
    
    current_max_n_papers = [int(max_n_papers* 0.75), int(max_n_papers * 0.90), max_n_papers]
    for i, query in enumerate(search_queries):
        papers = scholarly.search_pubs(query)
        for paper in papers:
            if len(search_results) >= current_max_n_papers[i]:
                break
            if paper not in search_results:
                search_results.append(paper)

    logging.info(f"Found {len(search_results)} papers")
    
    return search_results

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    prompt = "What are the latest advancements in quantum computing?"
    search_results = search(prompt,  max_n_papers=10)
    print("Search results:")
    for result in search_results:
        print(f"Title: {result['bib']['title']}")

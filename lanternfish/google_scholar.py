
from llm_api import generate_search_prompts
from scholarly import scholarly
import logging
from cache_to_disk import cache_to_disk

@cache_to_disk(1)
def get_scholar_search_pubs(query, max_n_papers): # to cache google scholar results
    papers = []
    n_paper = 0
    for paper in scholarly.search_pubs(query):
        papers.append(paper)
        n_paper += 1
        if n_paper >= max_n_papers:
            break
    return papers

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
        new_prompt += "Please generate a new search query that will find more relevant papers. Consider making the search less specific potentially with fewer ANDs and more ORs."
        search_queries.append(generate_search_prompts(new_prompt))

    logging_info_queries = "Search queries generated:\n"
    for query in search_queries:
        logging_info_queries += f"- {query}\n"
    logging.info(logging_info_queries)

    paper = {
        "google scholar info": None,
        "pdf path": None,
        "url": None,
        "markdown path": None,
        "relevancy score": None,
        "quality score": None,
        "total score": None,
        "summary": None,
    }
    papers = []
    unique_ids = []

    print("Searching Google Scholar for papers...")
    logging.info(f"Searching Google Scholar for at most {max_n_papers} papers")
    
    current_max_n_papers = [int(max_n_papers* 0.75), int(max_n_papers * 0.90), max_n_papers]
    for i, query in enumerate(search_queries):
        google_scholar_hits = get_scholar_search_pubs(query, max_n_papers)
        for paper_info in google_scholar_hits:
            if len(papers) >= current_max_n_papers[i]:
                break
            unique_id = (paper_info['bib']['title'], paper_info['bib']['author'])
            if (unique_id not in unique_ids):
                papers.append(paper.copy())
                papers[-1]["google scholar info"] = paper_info
                unique_ids.append(unique_id)

    logging.info(f"Found {len(papers)} papers")
    
    return papers

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    prompt = "What are the latest advancements in quantum computing?"
    papers = search(prompt,  max_n_papers=10)
    print("Search results:")
    for paper in papers:
        print(f"Title: {paper['google scholar info']['bib']['title']}")

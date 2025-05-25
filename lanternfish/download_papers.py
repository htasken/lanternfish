import os
import requests
import arxiv
from thefuzz import fuzz

def download_pdf_from_url(pdf_url, title, folder="lanternfish/papers"):
    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:100]
    filepath = os.path.join(folder, f"{safe_title}.pdf")

    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()  

        content_type = response.headers.get('Content-Type', '')
        if "pdf" not in content_type.lower():
            print(f"URL does not point to a PDF: {pdf_url}")
            return None

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"Downloaded: {title}\n")
        return filepath

    except Exception as e:
        print(f"Failed to download {title} from {pdf_url}: {e}\n")
        return None


def download_from_arxiv(title, folder="lanternfish/papers", similarity_threshold=80):
    if not os.path.exists(folder):
        os.makedirs(folder)

    client = arxiv.Client()

    search = arxiv.Search(
        query=title,
        max_results=1,
        sort_by=arxiv.SortCriterion.Relevance
    )

    try:
        for result in client.results(search):
            arxiv_title = result.title
            similarity = fuzz.token_set_ratio(title.lower(), arxiv_title.lower())
            print(f"Comparing titles:\n  Original: {title}\n  arXiv:    {arxiv_title}\n  Similarity: {similarity}%")

            if similarity >= similarity_threshold:
                pdf_url = result.pdf_url
                print(f"Title similarity {similarity}% >= {similarity_threshold}%. Downloading {arxiv_title}")
                return download_pdf_from_url(pdf_url, title, folder)

        print(f"No arXiv papers matched the title with similarity >= {similarity_threshold}%")
    except Exception as e:
        print(f"Arxiv download failed for {title}: {e}")
    return None


def download_paper(paper, folder="lanternfish/papers"):
    """
    Wrapper function to try Google Scholar eprint_url first, then fallback to arXiv search if needed.
    """
    title = paper['bib']['title']
    url = paper.get('eprint_url', None)

    if url:
        print(f"Trying direct download for paper: {title}")
        filepath = download_pdf_from_url(url, title, folder)
        if filepath is not None:
            return filepath
        else:
            print(f"Direct download failed.")
            return download_from_arxiv(title, folder)
    else:
        print(f"Trying arXiv for {title}")
        return download_from_arxiv(title, folder)


if __name__=="__main__":
    papers_example =[
        {'bib': {'title': 'NISQ Quantum Computing: A Security-Centric Tutorial and Survey [Feature]'},
                      'eprint_url': 'https://iontrap.physics.indiana.edu/papers/Chen2024.pdf'}, 
                    # Directly downloadable

        {'bib': {'title': 'Attention Is All You Need'},  
                        'eprint_url': 'https://papers.nips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html'},
                    # Not directly downloadable, found in arXiv

        {'bib': {'title': 'Analysis of the Principles of Quantum Computing and State-of-the-Art Applications'},
                       'eprint_url': 'https://www.ewadirect.com/proceedings/tns/article/view/16377'} 
                    # Not directly downloadable and not found in arXiv
                    ]
    
    for paper in papers_example:
        download_paper(paper)

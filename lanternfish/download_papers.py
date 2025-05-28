import os
import requests
import arxiv
import shutil
from thefuzz import fuzz

def download_pdf_from_url(pdf_url, title, folder="lanternfish/papers", verbose = False):
    
    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:100]
    filepath = os.path.join(folder, f"{safe_title}.pdf")

    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()  

        content_type = response.headers.get('Content-Type', '')
        if "pdf" not in content_type.lower():
            if verbose:
                print(f"URL does not point to a PDF: {pdf_url}")
            return None

        with open(filepath, "wb") as f:
            f.write(response.content)

        if verbose:
            print(f"Downloaded")
        return filepath

    except Exception as e:
        print(f"Failed to download from {pdf_url}: {e}")
        return None


def download_from_arxiv(title, folder="lanternfish/papers", similarity_threshold=80, verbose = False):

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
            if verbose:
                print(f"Comparing titles:\n  Original: {title}\n  arXiv:    {arxiv_title}\n  Similarity: {similarity}%")

            if similarity >= similarity_threshold:
                pdf_url = result.pdf_url
                if verbose:
                    print(f"Title similarity {similarity}% >= {similarity_threshold}%.")
                return download_pdf_from_url(pdf_url, title, folder)

        if verbose:
            print(f"No arXiv papers matched the title with similarity >= {similarity_threshold}%")
    except Exception as e:
        if verbose:
            print(f"arXiv download failed for {title}: {e}")
        return None


def download_paper(paper, folder="lanternfish/papers", verbose = False):
    """
    Wrapper function to try Google Scholar eprint_url first, then fallback to arXiv search if needed.
    """
    title = paper['bib']['title']
    url = paper.get('eprint_url', None)

    if url:
        if verbose:
            print(f"Trying direct download")
        filepath = download_pdf_from_url(url, title, folder, verbose = verbose)
        if filepath is not None:
            return filepath
        else:
            if verbose:
                print(f"Direct download failed")
                print(f"Trying arXiv download")
            return download_from_arxiv(title, folder, verbose = verbose)
    else:
        if verbose:
            print(f"Trying arXiv download")
        return download_from_arxiv(title, folder, verbose = verbose)
    

def download_papers(papers, folder="lanternfish/papers", verbose=False):
    successful_downloads = 0
    download_attempts = len(papers)
    successful_papers = []
    pdf_paths = []

    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        clear_folder(folder)

    print("Downloading papers")

    for i, paper in enumerate(papers):
        if verbose:
            print(f"\nAttempting to download paper {i+1}/{download_attempts}: {paper['bib']['title']}")
        path = download_paper(paper, verbose=verbose)
        if path is not None:
            if verbose:
                print("✅ Success")
            successful_downloads += 1
            successful_papers.append(paper)
            pdf_paths.append(path)
        else:
            if verbose:
                print("❌ Failed")

    print("\nDownload completed")
    print(f"Out of a total of {download_attempts} papers, {successful_downloads} were successfully downloaded.")
    return successful_papers, pdf_paths


def clear_folder(folder):
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')


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
    
    papers_example = download_papers(papers_example, verbose=True)


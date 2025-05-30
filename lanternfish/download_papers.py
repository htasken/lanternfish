from common import clear_folder
import os
import requests
import arxiv
from thefuzz import fuzz

def download_pdf_from_url(pdf_url, title, folder="lanternfish/papers", verbose = False):
    """
    Download a PDF from a given URL and save it locally using a sanitized version of the title.

    The PDF is saved in the specified folder with a filename derived from the paper title,
    where non-alphanumeric characters are replaced by underscores and truncated to 100 characters.

    Args:
        pdf_url (str): URL pointing to the PDF file.
        title (str): Title used to create a safe filename for saving the PDF.
        folder (str): Directory where the PDF should be saved. Defaults to "lanternfish/papers".
        verbose (bool): If True, prints progress messages. Defaults to False.

    Returns:
        str or None: The path to the saved PDF file if successful, otherwise None.
    """

    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:100]
    filepath = os.path.join(folder, f"{safe_title}.pdf")

    if os.path.exists(filepath):
        if verbose:
            print(f"File already exists, skipping download: {filepath}")
        return filepath

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
    """
    Search for and download a paper from arXiv using a fuzzy match on the title.

    The function queries arXiv for the most relevant paper matching the provided title.
    It then compares the returned title with the given title using token set ratio similarity.
    If the similarity is above the specified threshold, the paper's PDF is downloaded.

    Args:
        title (str): The title of the paper to search for.
        folder (str): Directory where the PDF should be saved. Defaults to "lanternfish/papers".
        similarity_threshold (int): Minimum required similarity (0-100) between titles. Defaults to 80.
        verbose (bool): If True, prints diagnostic messages during execution. Defaults to False.

    Returns:
        str or None: Path to the downloaded PDF if successful, otherwise None.
    """

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
    Attempt to download a paper using its direct eprint URL, with fallback to arXiv search.

    This function first tries to download the paper using the 'eprint_url' field provided
    by Google Scholar. If the direct download fails or the URL is not present, it falls 
    back to searching for the paper on arXiv using a fuzzy match on the paper title.

    Args:
        paper (dict): A dictionary containing metadata about the paper. Expected to have a 
                      'bib' field with a 'title', and optionally an 'eprint_url' field.
        folder (str): Directory where the PDF should be saved. Defaults to "lanternfish/papers".
        verbose (bool): If True, prints progress and debug information. Defaults to False.

    Returns:
        str or None: Path to the downloaded PDF if successful, otherwise None.
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
    """
    Attempt to download a list of papers and return the successfully downloaded ones.

    For each paper, this function first tries to download using the 'eprint_url' field 
    if available. If that fails or is missing, it falls back to a fuzzy arXiv title match.
    Successfully downloaded PDFs are saved to the specified folder.
    Downloads are skipped if the PDF file already exists locally, avoiding redundant downloads.
    

    Args:
        papers (list): A list of dictionaries, each representing a paper with at least a 
                       'bib' subdictionary containing the 'title'. Optionally includes an 
                       'eprint_url' field.
        folder (str): Directory where the downloaded PDFs will be saved. Defaults to "lanternfish/papers".
        verbose (bool): If True, prints detailed information about each download attempt. Defaults to False.

    Returns:
        tuple:
            list: The subset of `papers` that were successfully downloaded.
            list: Paths to the corresponding successfully downloaded PDF files.
    """

    successful_downloads = 0
    download_attempts = len(papers)
    successful_papers = []
    pdf_paths = []

    if not os.path.exists(folder):
        os.makedirs(folder)

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


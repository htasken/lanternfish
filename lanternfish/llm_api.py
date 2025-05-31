from llm_client import AsyncLLMClient
import asyncio
from prompts import SYSTEM_GENERATE_QUERY, SYSTEM_GENERATE_RELEVANCE_SCORE, SYSTEM_GENERATE_QUALITY_SCORE, SYSTEM_GENERATE_SUMMARY, SYSTEM_GENERATE_TITLE


llm_client = AsyncLLMClient()


def generate_search_prompts(user_prompt):
    return asyncio.run(
        llm_client.get_completion(user_prompt,
                                  system_message=SYSTEM_GENERATE_QUERY)
    )

async def generate_score(user_prompt, paper_info, n_samples=1, type="relevance"):
    """
    Generate a relevance or quality score for a paper or review using an LLM.

    The function sends a prompt to a language model `n_samples` times and computes the
    average score returned by the model. For relevance scoring, the prompt consists of
    the user's search intent and the paper information. For quality scoring, the prompt
    uses review content instead. The score must be an integer between 0 and 9 (inclusive).

    Args:
        user_prompt (str): The user's query or task description.
        paper_info (str): LaTeX-formatted paper metadata or review content.
        n_samples (int): Number of times to query the model to average out the score. Default is 1.
        type (str): Type of score to generate, either "relevance" or "quality".

    Returns:
        float: The average score returned by the LLM across `n_samples` calls.

    Raises:
        ValueError: If the `type` is invalid or no valid scores are returned.
    """

    if type == "relevance":
        complete_prompt = f"User prompt:\n{user_prompt}\n\nPaper:\n{paper_info}"
        system_message = SYSTEM_GENERATE_RELEVANCE_SCORE
    elif type == "quality":
        complete_prompt = f"Review: {paper_info}"
        system_message = SYSTEM_GENERATE_QUALITY_SCORE
    else:
        raise ValueError(f"Invalid type: {type}. Must be 'relevance' or 'quality'.")

    tasks = [
        llm_client.get_completion(
            complete_prompt,
            system_message=system_message,
            max_tokens=1
        )
        for _ in range(n_samples)
    ]

    responses = await asyncio.gather(*tasks)

    scores = []
    for response in responses:
        if response is not None:
            try:
                score = int(response.strip())
                if 0 <= score <= 9:
                    scores.append(score)
                else:
                    print(f"Invalid score (out of range): {score}")
            except ValueError:
                print(f"Invalid score (non-integer): {response}")

    if not scores:
        return 5
        #raise ValueError("No valid scores returned by the LLM.")

    return sum(scores) / len(scores)


def generate_summary(user_prompt, paper_latex, verbose=False):
    """
    Generate a summary of a paper's transcription tailored to the user's prompt using the LLM.

    Args:
        transcription (str): The full markdown text transcription of the paper.
        user_prompt (str): The prompt describing the field/context for tailoring the summary.
        verbose (bool): Whether to print debug info.

    Returns:
        str: The generated summary from the LLM.
    """

    # Combine the transcription and user prompt into the message to the model
    full_prompt = f"Paper content:\n{paper_latex}\n\nUser prompt:\n{user_prompt}"

    if verbose:
        print("Generating summary with LLM...")

    summary = asyncio.run(
        llm_client.get_completion(
            full_prompt,
            system_message=SYSTEM_GENERATE_SUMMARY
        )
    )

    if verbose:
        print("Summary generated.")

    return summary

def generate_title(user_prompt):
    """
    Generate a title for a paper based on the user's prompt using the LLM.

    Args:
        user_prompt (str): The prompt describing the field/context for generating the title.

    Returns:
        str: The generated title from the LLM.
    """

    return asyncio.run(
        llm_client.get_completion(
            user_prompt,
            system_message=SYSTEM_GENERATE_TITLE
        )
    )

def generate_summary_overall(user_prompt, papers):
    paper_titles_and_summaries = ""
    for paper in papers:
        paper_titles_and_summaries += f"Title:\n {paper['google scholar info']['bib']['title']}\n\nSummary:\n {paper['summary']}\n\n"

    prompt = f"User prompt:\n{user_prompt}\n\nPapers in report:\n{paper_titles_and_summaries}"

    return asyncio.run(
        llm_client.get_completion(
            prompt,
            system_message=SYSTEM_GENERATE_SUMMARY
        )
    )

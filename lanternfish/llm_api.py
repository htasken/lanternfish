from llm_client import AsyncLLMClient
import asyncio
from prompts import SYSTEM_GENERATE_QUERY, SYSTEM_GENERATE_RELEVANCE_SCORE, SYSTEM_GENERATE_QUALITY_SCORE


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
        complete_prompt = f"User prompt: {user_prompt} \nPaper: {paper_info}"
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
        raise ValueError("No valid scores returned by the LLM.")

    return sum(scores) / len(scores)


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


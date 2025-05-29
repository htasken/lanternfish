from llm_client import AsyncLLMClient
import asyncio
from prompts import SYSTEM_GENERATE_QUERY, SYSTEM_GENERATE_RELEVANCE_SCORE


llm_client = AsyncLLMClient()


def generate_search_prompts(user_prompt):
    return asyncio.run(
        llm_client.get_completion(user_prompt,
                                  system_message=SYSTEM_GENERATE_QUERY)
    )


def generate_relevance_score(user_prompt, paper_latex):

    complete_prompt = f"User prompt: {user_prompt} \nPaper: {paper_latex}"

    response = asyncio.run(
        llm_client.get_completion(complete_prompt,
                                  system_message=SYSTEM_GENERATE_RELEVANCE_SCORE)
    )

    if response and response.strip().isdigit():
        return int(response.strip())
    else:
        return None

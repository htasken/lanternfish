from llm_client import AsyncLLMClient
import asyncio
from prompts import SYSTEM_GENERATE_QUERIES


llm_client = AsyncLLMClient()


def generate_search_prompts(user_prompt):
    return asyncio.run(
        llm_client.get_completion(user_prompt,
                                    system_message=SYSTEM_GENERATE_QUERIES))



import os
import asyncio
from openai import AsyncOpenAI, OpenAIError # Import AsyncOpenAI
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class AsyncLLMClient:
    def __init__(self):
        self.server_ip = os.getenv("LLM_SERVER_IP")
        self.server_port = os.getenv("LLM_SERVER_PORT")
        self.model_name = os.getenv("LLM_MODEL_NAME")
        self.api_key = os.getenv("OPENAI_API_KEY")

        custom_base_url = None
        if self.server_ip and self.server_port:
            custom_base_url = f"http://{self.server_ip}:{self.server_port}/v1"
            logging.info(f"Using custom LLM endpoint: {custom_base_url}")
        elif os.getenv("OPENAI_API_BASE"):
            custom_base_url = os.getenv("OPENAI_API_BASE")
            logging.info(f"Using OpenAI base URL from OPENAI_API_BASE: {custom_base_url}")
        else:
            logging.info("Using default OpenAI API endpoint.")

        try:
            # Use AsyncOpenAI instead of OpenAI
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=custom_base_url
            )
        except OpenAIError as e: # Note: OpenAIError might not be specific to async initialization
            logging.error(f"Error initializing AsyncOpenAI client: {e}")
            self.client = None

    async def get_completion(self, prompt: str, system_message: str = "You are a helpful assistant.", max_tokens: int = 500, json: bool = False) -> str | None:
        if not self.client:
            logging.error("AsyncLLMClient is not initialized. Cannot get completion.")
            return None

        try:
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            if json:
                response_format={ "type": "json_object" }
            else:
                response_format=None

            # Use await for the asynchronous API call
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format=response_format,
                max_tokens=max_tokens
            )
            if response.choices and len(response.choices) > 0:
                text_response = response.choices[0].message.content.strip()
                logging.debug("Response: "+text_response)
                if json:
                    try:
                        return json.loads(text_response)
                    except:
                        logging.error(f"Couldn't parse json {text_response}")
                        
                return  text_response
            else:
                logging.error("No completion choices returned.")
                return None
        except OpenAIError as e: # OpenAIError can be raised by async calls too
            logging.error(f"Error during LLM API call: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None

    async def close(self):
        """
        Closes the underlying HTTPX client session.
        It's good practice to call this when the client is no longer needed,
        especially in long-running applications.
        """
        if self.client:
            await self.client.close()
            logging.info("AsyncLLMClient session closed.")

async def main():
    # Instantiate the client
    llm_client = AsyncLLMClient()

    if llm_client.client: 
        user_prompt = "Explain why bayesians are the worst thing happening to statistics ever."
        print(f"\nUser Prompt: {user_prompt}")

        # Await the asynchronous method
        completion = await llm_client.get_completion(user_prompt)

        if completion:
            print("\nLLM Response:")
            print(completion)
        else:
            print("\nFailed to get completion from the LLM.")

        print("\n--- Concurrent Calls Example ---")
        prompts = [
            "Explain why bayesian priors are wishful thinking that should be criminalized.",
            "Write a short poem about what a potato and bayesians have in common."
        ]
        tasks = [llm_client.get_completion(p) for p in prompts]
        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            print(f"\nResponse for prompt '{prompts[i]}':")
            if result:
                print(result)
            else:
                print("Failed to get completion.")

        await llm_client.close()
    else:
        logging.error("Could not initialize AsyncLLMClient.")

if __name__ == "__main__":
    asyncio.run(main())

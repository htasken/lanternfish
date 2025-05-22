import asyncio
import ollama
import subprocess
import sys
import os
import requests
import logging
import signal
import time

class LLM:
    """LLM wrapper class for Ollama with async support."""

    def __init__(self, model, logging_level=logging.WARNING):
        """Start up a Ollama server and pull the model if not already running.

        Args:
            model (str): The name of the Ollma model to use. See https://ollama.com/models for available models.
            logging_level (int): Logging level for the server. Default is logging.WARNING.
        """
        logging.basicConfig(level=logging_level)
        self.model = model
        try:
            file_dir = os.path.dirname(os.path.abspath(__file__))
        except:
            file_dir = os.getcwd()
        self.server_pid_file = os.path.join(file_dir, ".server.pid")
        self.server_users_pid_file = os.path.join(file_dir, ".server_users.pid")
        self.server_port = 11435
        self.server_url = f"http://localhost:{self.server_port}"
        os.environ["OLLAMA_HOST"] = self.server_url
        self._start_ollama_server()
        self._register_use_of_ollama_server()
        self.tasks = []

    def _check_if_ollama_server_is_running(self):
        try: 
            if requests.get(self.server_url).status_code == 200:
                logging.debug("Server is already running.")
                return True
        except:
            pass 
        logging.debug("Server is not running already.")
        return False

    def _start_ollama_server(self):
        if not self._check_if_ollama_server_is_running():
            logging.info("Starting Ollama server.")
            command = ["ollama", "serve"]
            env_vars = dict(os.environ)
            if sys.platform == "win32":
                process = subprocess.Popen(
                    command,
                    env=env_vars,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
            else:
                process = subprocess.Popen(
                    command,
                    env=env_vars,
                    start_new_session=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
            with open(self.server_pid_file, "w") as f:
                f.write(str(process.pid))
            time.sleep(3)
        client = ollama.Client(host=self.server_url)
        if not any(model.model.startswith(self.model) for model in client.list().models):
            logging.warning(f"Downloading the Ollama model {self.model}. This may take a while...")
            client.pull(model=self.model)

    def _stop_ollama_server(self):
        logging.info("Stopping Ollama server.")
        try:
            with open(self.server_pid_file, "r") as f:
                pid = int(f.read())
            os.kill(pid, signal.SIGTERM)
        except FileNotFoundError:
            logging.warning("Server not running or PID file not found.")

    def _register_use_of_ollama_server(self):
        logging.debug(f"Registering use of Ollama server on {os.getpid()}.")
        with open(self.server_users_pid_file, "a") as f:
            f.write(str(os.getpid()) + "\n")
        
    def _unregister_use_of_ollama_server(self):
        logging.debug(f"Unregistered use of Ollama server on {os.getpid()}.")
        with open(self.server_users_pid_file, "w+") as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if line.strip() != str(os.getpid()):
                    f.write(line)

    def _n_registered_users(self):
        with open(self.server_users_pid_file, "r") as f:
            lines = f.readlines()
        return len(lines)

    def add_generation_task(self, prompt, **kwargs):
        """Generates a continuation of the prompt once 'run_tasks' is called.
        
        Args:
            prompt (str): The prompt to generate from.
            **kwargs: Additional keyword arguments for Ollama's 'generate' function.
        """
        self.tasks.append(ollama.AsyncClient().generate(prompt=prompt, model=self.model, **kwargs))

        return len(self.tasks) - 1

    def add_chat_task(self, messages, **kwargs):
        """Generates a chat answer to messages once 'run_tasks' is called.
        
        Args:
            messages: Chat messagers in the OpenAI format.
            **kwargs: Additional keyword arguments for Ollama's 'chat' function.
        """
        self.tasks.append(ollama.AsyncClient().chat(messages=messages, model=self.model, **kwargs))

        return len(self.tasks) - 1

    async def _run_async_tasks(self):
        return [await task for task in self.tasks]

    def run_tasks(self):
        logging.debug("Running generation and chat tasks asynchronously.")
        return asyncio.run(self._run_async_tasks())

    def close(self):
        """Close the LLM and stop the server if no other users are registered.

        Needs to be called manually if 'with LLM(...) as llm:' is not used,
        as __del__ can't open files."""
        self._unregister_use_of_ollama_server()
        if self._n_registered_users() == 0:
            self._stop_ollama_server()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

if __name__ == "__main__":
    # Example usage
    llm = LLM(model="llama3.1")
    prompts = ["Hello, how are you?", "What color is the sun?"]
    llm.add_generation_task(prompt=prompts[0])
    messages = [
        {"role": "user", "content": prompts[1]},
    ]
    llm.add_chat_task(messages=messages)
    results = llm.run_tasks()
    print(f"{prompts[0]}\n{results[0].response}\n\n")
    print(f"{prompts[1]}\n{results[1].message.content}\n\n")
    llm.close() # Need to be called manually if not using 'with LLM(...) as llm:'

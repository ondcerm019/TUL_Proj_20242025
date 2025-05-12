"""
This module provides a OpenAIClientManager class that manages multiple
OpenAI API clients using a circular buffer. Clients hitting rate limits
are temporarily removed and re-added once their cooldown expires.
"""

import time
import re
from collections import deque
from openai import OpenAI, APIStatusError, APITimeoutError, APIConnectionError #RateLimitError
#from pydantic
from openai.types.chat import ChatCompletionMessageParam

DEFAULT_COOLDOWN = 600


class OpenAIClientManager:
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-locals
    """
    Manages multiple OpenAI API clients with support for different models and base URLs.
    """

    def __init__(self, configs: list[dict]):
        """
        Initializes with a list of config dictionaries:
        [
            {
                "keys": ["api_key1", "api_key2"],
                "model": "model-name",
                "base_url": "https://custom.endpoint/v1"
            },
            ...
        ]
        """
        self._clients = deque()
        self._cooldown_clients = {}  # api_key -> timestamp
        self._key_meta = {}          # api_key -> (model, base_url)
        self._all_keys = []

        for config in configs:
            keys = config.get("keys")
            model = config.get("model")
            base_url = config.get("base_url")

            if not keys:
                raise ValueError("Each config must contain at least one API key.")

            for key in keys:
                self._clients.append(OpenAI(api_key=key, base_url=base_url))
                self._key_meta[key] = (model, base_url)
                self._all_keys.append(key)

    def _restore_cooled_down_clients(self):
        now = time.time()
        ready_keys = [key for key, ts in self._cooldown_clients.items() if now >= ts]
        for key in ready_keys:
            _, base_url = self._key_meta[key]
            print(f"[INFO] Re-adding cooled down client {key}")
            self._clients.append(OpenAI(api_key=key, base_url=base_url))
            del self._cooldown_clients[key]

    def _extract_cooldown_seconds(self, message):
        match = re.search(r"try again in (\d+)m([\d.]+)s", message)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            return minutes * 60 + seconds
        return None

    def chat(self, messages: list[ChatCompletionMessageParam], temperature: float) -> str:
        """
        Sends a chat request using the OpenAI API, rotating through clients.
        Automatically uses the corresponding model and base_url for each API key.
        """
        self._restore_cooled_down_clients()

        total_clients = len(self._all_keys)                # all known API keys (active + cooldown)
        active_clients = len(self._clients)                # not currently on cooldown
        attempts = active_clients

        for _ in range(attempts):
            client = self._clients[0]
            api_key = client.api_key
            model, base_url = self._key_meta[api_key]
            index = self._all_keys.index(api_key) + 1

            #temp

            print(f"Used client {index}/{total_clients} (active: {active_clients}): {base_url}")

            try:
                response = client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=temperature
                )
                returncontent = response.choices[0].message.content
                self._clients.rotate(-1) # circ buffer shift
                return returncontent

            except (APIStatusError, APITimeoutError, APIConnectionError, TypeError) as e:
                print(e)
                message = str(e)
                cooldown_seconds = self._extract_cooldown_seconds(message) or DEFAULT_COOLDOWN
                retry_at = time.time() + cooldown_seconds

                self._cooldown_clients[api_key] = retry_at
                self._clients.popleft()
                print(f"[WARNING] Rate limit hit for {api_key}, retry in {cooldown_seconds:.1f}s.")
                continue

        raise RuntimeError("All API keys are currently rate-limited.")

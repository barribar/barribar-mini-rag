from ..LLMInterface import LLMInterface
import requests
import math
import logging
from typing import List, Union
from ..LLMEnums import OllamaEnums, DocumentTypeEnum


class OllamaProvider(LLMInterface):

    def __init__(
        self,
        generation_model_id: str,
        embedding_model_id: str,
        api_url: str,
        default_input_max_characters: int = 1024,
        default_generation_max_output_tokens: int = 300,
        default_generation_temperature: float = 0.1,
        embedding_size: int = None,
    ):
        self.generation_model_id = generation_model_id
        self.embedding_model_id = embedding_model_id
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.embedding_size = embedding_size
        self.enums = OllamaEnums
        self.logger = logging.getLogger(__name__)

    # --- GENERATION ---

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt,
        }

    def generate(self, prompt: str):
        prompt = self.process_text(prompt)
        response = requests.post(
            f"{self.api_url}/api/generate",
            json={
                "model": self.generation_model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.default_generation_temperature,
                    "num_predict": self.default_generation_max_output_tokens
                }
            }
        )
        response.raise_for_status()
        return response.json()["response"]

    def generate_text(self, prompt: str, chat_history: list = [],
                      max_output_tokens: int = None, temperature: float = None):
        if not self.generation_model_id:
            self.logger.error("Generation model for Ollama was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        # Build messages from chat_history + current prompt
        messages = list(chat_history) + [
            {"role": OllamaEnums.USER.value, "content": self.process_text(prompt)}
        ]

        response = requests.post(
            f"{self.api_url}/api/chat",
            json={
                "model": self.generation_model_id,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_output_tokens,
                }
            }
        )
        response.raise_for_status()
        result = response.json()

        if not result or "message" not in result:
            self.logger.error("Error while generating text with Ollama")
            return None

        return result["message"]["content"]

    # --- EMBEDDINGS ---

    def set_embedding_model(self, model_id: str, embedding_size: int = None):
        self.embedding_model_id = model_id
        if embedding_size:
            self.embedding_size = embedding_size

    def _clean_vector(self, vec):
        """Sanitize a vector for PGVector and JSON (zeros, NaN/Inf)."""
        if not vec and self.embedding_size:
            vec = [0.0] * self.embedding_size
        cleaned = []
        for v in vec:
            try:
                v = float(v)
                if math.isnan(v) or math.isinf(v):
                    cleaned.append(0.0)
                else:
                    cleaned.append(v)
            except (TypeError, ValueError):
                cleaned.append(0.0)
        if self.embedding_size and len(cleaned) < self.embedding_size:
            cleaned += [0.0] * (self.embedding_size - len(cleaned))
        return cleaned

    def embed(self, text: Union[str, List[str]]):
        """
        Supports string or list of strings.
        Always returns a list of vectors.
        """
        if isinstance(text, str):
            text = [text]

        if not text:
            return [[0.0] * self.embedding_size if self.embedding_size else [] for _ in text]

        response = requests.post(
            f"{self.api_url}/api/embeddings",
            json={
                "model": self.embedding_model_id,
                "input": text
            }
        )
        response.raise_for_status()
        result = response.json()

        # --- Case: data array (OpenAI-compatible format)
        if "data" in result:
            vectors = []
            for item in result["data"]:
                vec = self._clean_vector(item.get("embedding", []))
                vectors.append(vec)
            return vectors

        # --- Case: single embedding
        if "embedding" in result:
            e = result["embedding"]

            if not e and self.embedding_size:
                return [[0.0] * self.embedding_size for _ in text]
            elif not e:
                return [[] for _ in text]

            first_elem = e[0]
            if isinstance(first_elem, (int, float)):
                return [self._clean_vector(e)]
            elif isinstance(first_elem, list):
                return [self._clean_vector(v) for v in e]

        raise ValueError(f"Unexpected embedding response format: {result}")

    def embed_text(self, text: Union[str, List[str]], document_type=None):
        """Alias compatible with NlpController."""
        return self.embed(text)
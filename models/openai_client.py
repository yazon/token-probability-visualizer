"""
OpenAI API client for token probability visualization.
"""

import os
from typing import Dict, List, Any, Tuple, Optional

from openai import OpenAI


class OpenAIClient:
    """Client for interacting with OpenAI API to get token probabilities."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set it as an argument or OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models.

        Returns:
            List of model information dictionaries.
        """
        response = self.client.models.list()
        return [
            {"id": model.id, "name": model.id}
            for model in response.data
            if "gpt" in model.id
        ]  # Filter for GPT models

    def generate_with_probabilities(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo-instruct",
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 100,
        logprobs: int = 5,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate text and get token probabilities.

        Args:
            prompt: The input prompt.
            model: The model to use.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            max_tokens: Maximum number of tokens to generate.
            logprobs: Number of log probabilities to return per token.

        Returns:
            Tuple of (generated_text, token_probabilities)
        """
        # For completion models that support logprobs
        if "instruct" in model or model in ["gpt-3.5-turbo-instruct", "davinci"]:
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                logprobs=logprobs,
            )

            text = response.choices[0].text

            # Process token probabilities
            tokens = []
            for i, token in enumerate(response.choices[0].logprobs.tokens):
                token_info = {
                    "token": token,
                    "text": token,
                    "logprob": response.choices[0].logprobs.token_logprobs[i],
                    "probability": 2
                    ** response.choices[0].logprobs.token_logprobs[
                        i
                    ],  # Convert logprob to probability
                    "top_logprobs": {},
                }

                # Add top logprobs if available
                if (
                    hasattr(response.choices[0].logprobs, "top_logprobs")
                    and response.choices[0].logprobs.top_logprobs
                ):
                    for token_text, logprob in (
                        response.choices[0].logprobs.top_logprobs[i].items()
                    ):
                        token_info["top_logprobs"][token_text] = {
                            "logprob": logprob,
                            "probability": 2**logprob,
                        }

                tokens.append(token_info)

            return text, tokens
        else:
            # Chat models don't directly support logprobs
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content

            tokens = []
            for i, char in enumerate(text):
                tokens.append(
                    {
                        "token": char,
                        "text": char,
                        "logprob": None,
                        "probability": None,
                        "top_logprobs": {},
                    }
                )

            return text, tokens

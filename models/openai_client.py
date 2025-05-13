"""
OpenAI API client for token probability visualization.
"""

from typing import Dict, List, Any, Tuple, Optional
import logging

from openai import OpenAI, AzureOpenAI

import config


class OpenAIClient:
    """Client for interacting with OpenAI API to get token probabilities."""

    def __init__(
        self,
        service_type: str = config.STARTUP_SERVICE_TYPE,
        api_key: Optional[str] = None,
        azure_api_key: Optional[str] = config.AZURE_OPENAI_API_KEY,
        azure_endpoint: Optional[str] = config.AZURE_OPENAI_ENDPOINT,
        azure_api_version: Optional[str] = config.AZURE_API_VERSION,
    ):
        """
        Initialize the OpenAI client for either standard OpenAI or Azure OpenAI.

        Args:
            service_type: 'openai' or 'azure'.
            api_key: OpenAI API key. If None, will try to get from environment variable (config.OPENAI_API_KEY).
            azure_api_key: Azure OpenAI API key.
            azure_endpoint: Azure OpenAI endpoint name (e.g., your-resource-name).
            azure_api_version: Azure OpenAI API version.
        """
        self.service_type = service_type
        self.client: Any

        if self.service_type == "azure":
            if not all([azure_api_key, azure_endpoint, azure_api_version]):
                raise ValueError(
                    "For Azure OpenAI, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, "
                    "and AZURE_API_VERSION must be provided or set in config."
                )
            self.client = AzureOpenAI(
                api_key=azure_api_key,
                api_version=azure_api_version,
                azure_endpoint=f"https://{azure_endpoint}.openai.azure.com/",
            )
        else:
            self.api_key = api_key or config.OPENAI_API_KEY
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key is required. Set it as an argument or OPENAI_API_KEY environment variable/config."
                )
            self.client = OpenAI(api_key=self.api_key)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models.
        For Azure, this returns the configured model(s).
        For standard OpenAI, it fetches from the API.

        Returns:
            List of model information dictionaries.
        """
        if self.service_type == "azure":
            return [{"id": "gpt-35-turbo", "name": "gpt-35-turbo"}]
        else:
            response = self.client.models.list()
            return [
                {"id": model.id, "name": model.id}
                for model in response.data
                if "gpt" in model.id
            ]

    def generate_with_probabilities(
        self,
        prompt: str,
        model: str = config.DEFAULT_MODEL,
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 100,
        logprobs: Optional[int] = config.DEFAULT_LOGPROBS,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate text and get token probabilities.

        Args:
            prompt: The input prompt.
            model: The model to use (for Azure, this is the deployment name).
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            max_tokens: Maximum number of tokens to generate.
            logprobs: Number of log probabilities to return per token.
                      Set to None to disable logprobs for models that don't support it well.

        Returns:
            Tuple of (generated_text, token_probabilities)
        """
        tokens: List[Dict[str, Any]] = []
        generated_text: str = ""

        if self.service_type == "azure":
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                logprobs=True if logprobs is not None and logprobs > 0 else None,
                top_logprobs=logprobs
                if logprobs is not None and logprobs > 0
                else None,
            )
            generated_text = response.choices[0].message.content or ""

            if response.choices[0].logprobs and response.choices[0].logprobs.content:
                for token_logprob_info in response.choices[0].logprobs.content:
                    token_info: Dict[str, Any] = {
                        "token": token_logprob_info.token,
                        "text": token_logprob_info.token,
                        "logprob": token_logprob_info.logprob,
                        "probability": 2**token_logprob_info.logprob
                        if token_logprob_info.logprob is not None
                        else None,
                        "top_logprobs": {},
                    }
                    if token_logprob_info.top_logprobs:
                        for top_alt_token in token_logprob_info.top_logprobs:
                            token_info["top_logprobs"][top_alt_token.token] = {
                                "logprob": top_alt_token.logprob,
                                "probability": 2**top_alt_token.logprob
                                if top_alt_token.logprob is not None
                                else None,
                            }
                    tokens.append(token_info)
            else:
                for char_token in generated_text:
                    tokens.append(
                        {
                            "token": char_token,
                            "text": char_token,
                            "logprob": None,
                            "probability": None,
                            "top_logprobs": {},
                        }
                    )
            return generated_text, tokens

        elif "instruct" in model or model in ["davinci-002", "babbage-002"]:
            api_response = self.client.completions.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                logprobs=logprobs if logprobs is not None else 0,
            )
            generated_text = api_response.choices[0].text

            if api_response.choices[0].logprobs:
                raw_logprobs = api_response.choices[0].logprobs
                resp_tokens = (
                    raw_logprobs.tokens if hasattr(raw_logprobs, "tokens") else []
                )
                resp_token_logprobs = (
                    raw_logprobs.token_logprobs
                    if hasattr(raw_logprobs, "token_logprobs")
                    else []
                )
                resp_top_logprobs = (
                    raw_logprobs.top_logprobs
                    if hasattr(raw_logprobs, "top_logprobs")
                    else []
                )

                for i, token_str in enumerate(resp_tokens):
                    token_logp = (
                        resp_token_logprobs[i] if i < len(resp_token_logprobs) else None
                    )
                    token_info = {
                        "token": token_str,
                        "text": token_str,
                        "logprob": token_logp,
                        "probability": 2**token_logp
                        if token_logp is not None
                        else None,
                        "top_logprobs": {},
                    }
                    if (
                        resp_top_logprobs
                        and i < len(resp_top_logprobs)
                        and resp_top_logprobs[i]
                    ):
                        for alt_token_text, alt_logprob in resp_top_logprobs[i].items():
                            token_info["top_logprobs"][alt_token_text] = {
                                "logprob": alt_logprob,
                                "probability": 2**alt_logprob
                                if alt_logprob is not None
                                else None,
                            }
                    tokens.append(token_info)
            return generated_text, tokens
        else:
            try:
                api_response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    logprobs=True if logprobs is not None and logprobs > 0 else None,
                    top_logprobs=logprobs
                    if logprobs is not None and logprobs > 0
                    else None,
                )
                generated_text = api_response.choices[0].message.content or ""

                if (
                    api_response.choices[0].logprobs
                    and api_response.choices[0].logprobs.content
                ):
                    for token_logprob_info in api_response.choices[0].logprobs.content:
                        token_info = {
                            "token": token_logprob_info.token,
                            "text": token_logprob_info.token,
                            "logprob": token_logprob_info.logprob,
                            "probability": 2**token_logprob_info.logprob
                            if token_logprob_info.logprob is not None
                            else None,
                            "top_logprobs": {},
                        }
                        if token_logprob_info.top_logprobs:
                            for top_alt_token in token_logprob_info.top_logprobs:
                                token_info["top_logprobs"][top_alt_token.token] = {
                                    "logprob": top_alt_token.logprob,
                                    "probability": 2**top_alt_token.logprob
                                    if top_alt_token.logprob is not None
                                    else None,
                                }
                        tokens.append(token_info)
                else:
                    for char_token in generated_text:
                        tokens.append(
                            {
                                "token": char_token,
                                "text": char_token,
                                "logprob": None,
                                "probability": None,
                                "top_logprobs": {},
                            }
                        )
                return generated_text, tokens
            except Exception as e:
                logging.warning(
                    f"Logprobs not available for model {model} via chat completions or error: {e}"
                )
                api_response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                )
                generated_text = api_response.choices[0].message.content or ""
                for char_token in generated_text:
                    tokens.append(
                        {
                            "token": char_token,
                            "text": char_token,
                            "logprob": None,
                            "probability": None,
                            "top_logprobs": {},
                        }
                    )
                return generated_text, tokens

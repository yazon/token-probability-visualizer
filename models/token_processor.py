"""
Token probability processing utilities.
"""

import json
from html import escape


class TokenProcessor:
    """Process token probabilities for visualization."""

    @staticmethod
    def calculate_color(probability: float | None) -> str:
        """
        Calculate the CSS class based on token probability.

        Args:
            probability: Token probability (0.0 to 1.0)

        Returns:
            CSS class name for probability visualization
        """
        if probability is None:
            return "unknown-prob"

        # Return class names based on probability thresholds
        if probability > 0.8:
            return "high-prob"
        elif probability > 0.6:
            return "medium-high-prob"
        elif probability > 0.4:
            return "medium-prob"
        elif probability > 0.2:
            return "medium-low-prob"
        else:
            return "low-prob"

    @staticmethod
    def process_tokens(
        tokens: list[dict[str, any]], top_p: float
    ) -> list[dict[str, any]]:
        """
        Process tokens for visualization and calculate selection chance based on top_p.

        Args:
            tokens: list of token information dictionaries from OpenAI API
            top_p: The top_p value used for generation

        Returns:
            Processed tokens with visualization data and selection chance
        """
        processed_tokens_list = []

        for i, raw_token_info in enumerate(tokens):
            chosen_prob = raw_token_info.get("probability")
            chosen_text = raw_token_info.get("text", "")

            # --- Nucleus Sampling Calculation ---
            candidate_tokens = []
            # Add the actually chosen token first (important for reference)
            if chosen_prob is not None:
                candidate_tokens.append(
                    {
                        "text": chosen_text,
                        "probability": chosen_prob,
                    }
                )

            # Add alternatives from top_logprobs
            raw_alternatives = raw_token_info.get("top_logprobs", {})
            if raw_alternatives:
                for alt_text, alt_info in raw_alternatives.items():
                    # Skip adding if it's the same as the chosen token
                    if alt_text == chosen_text:
                        continue
                    alt_prob = alt_info.get("probability")
                    if alt_prob is not None:
                        candidate_tokens.append(
                            {
                                "text": alt_text,
                                "probability": alt_prob,
                            }
                        )

            # Sort candidates by probability (descending)
            candidate_tokens.sort(key=lambda x: x.get("probability", 0), reverse=True)

            nucleus_tokens = []
            cumulative_prob = 0.0
            nucleus_prob_sum = 0.0

            if (
                top_p < 1.0
            ):  # Only apply nucleus logic if top_p is not 1 (where all are included)
                for cand in candidate_tokens:
                    nucleus_tokens.append(cand)  # Add to nucleus first
                    nucleus_prob_sum += cand["probability"]
                    cumulative_prob += cand["probability"]
                    if cumulative_prob >= top_p:
                        break  # Stop adding once threshold is met or exceeded
            else:  # top_p is 1.0, include all candidates
                nucleus_tokens = candidate_tokens
                nucleus_prob_sum = sum(c.get("probability", 0) for c in nucleus_tokens)

            # Calculate selection chance for each candidate
            candidate_chances = {}
            for cand in candidate_tokens:
                cand_text = cand["text"]
                is_in_nucleus = any(n["text"] == cand_text for n in nucleus_tokens)

                if is_in_nucleus and nucleus_prob_sum > 0:
                    chance = cand["probability"] / nucleus_prob_sum
                    candidate_chances[cand_text] = chance
                else:
                    candidate_chances[cand_text] = 0.0
            # --- End Nucleus Sampling Calculation ---

            # --- Process Main Token ---
            processed_token = {
                "token": raw_token_info.get("token", ""),
                "text": chosen_text,
                "probability": chosen_prob,
                "logprob": raw_token_info.get("logprob"),
                "color": TokenProcessor.calculate_color(chosen_prob),
                "selection_chance": candidate_chances.get(
                    chosen_text, 0.0
                ),  # Get calculated chance
                "top_alternatives": [],
            }

            # --- Process Alternatives ---
            # Use the sorted candidates list, map chances back
            if raw_alternatives:
                # Create a dictionary of alternatives from raw_alternatives for easier lookup
                alt_dict = {
                    alt_text: info for alt_text, info in raw_alternatives.items()
                }

                # Iterate through sorted candidates *excluding* the chosen one to build alternatives list
                for cand in candidate_tokens:
                    cand_text = cand["text"]
                    if cand_text == chosen_text:  # Skip the chosen token itself
                        continue

                    # Check if the candidate is in the nucleus (chance > 0) before adding
                    cand_chance = candidate_chances.get(cand_text, 0.0)
                    if cand_chance > 0.0 and cand_text in alt_dict:
                        alt_info = alt_dict[cand_text]
                        alt_prob = alt_info.get("probability")
                        processed_token["top_alternatives"].append(
                            {
                                "text": cand_text,
                                "probability": alt_prob,
                                "logprob": alt_info.get("logprob"),
                                "color": TokenProcessor.calculate_color(alt_prob),
                                "selection_chance": cand_chance,  # Use pre-calculated chance
                            }
                        )

            processed_tokens_list.append(processed_token)

        return processed_tokens_list

    @staticmethod
    def tokens_to_html(processed_tokens: list[dict[str, any]]) -> str:
        """
        Convert processed tokens to HTML for visualization.

        Args:
            processed_tokens: list of processed token dictionaries

        Returns:
            HTML string with token visualization
        """
        html_parts = ['<div class="token-container">']

        for token in processed_tokens:
            prob_text = (
                f"{token['probability']:.4f}"
                if token["probability"] is not None
                else "N/A"
            )
            logprob_text = (
                f"{token['logprob']:.4f}" if token["logprob"] is not None else "N/A"
            )
            prob_class = token.get("color", "unknown-prob")
            chance_text = (
                f"{token.get('selection_chance', 0.0) * 100:.2f}%"  # Format chance
            )

            # --- Create tooltip data dictionary ---
            tooltip_data = {
                "text": token.get("text", ""),
                "probability": prob_text,
                "logprob": logprob_text,
                "selection_chance": chance_text,  # Add formatted chance
                "alternatives": [],
            }

            if token.get("top_alternatives"):
                for alt in token["top_alternatives"]:
                    alt_prob = (
                        f"{alt.get('probability'):.4f}"
                        if alt.get("probability") is not None
                        else "N/A"
                    )
                    alt_logprob = (
                        f"{alt.get('logprob'):.4f}"
                        if alt.get("logprob") is not None
                        else "N/A"
                    )
                    alt_color_class = alt.get("color", "unknown-prob")
                    alt_chance_text = f"{alt.get('selection_chance', 0.0) * 100:.2f}%"  # Format chance

                    tooltip_data["alternatives"].append(
                        {
                            "text": alt.get("text", ""),
                            "probability": alt_prob,
                            "logprob": alt_logprob,
                            "color_class": alt_color_class,
                            "selection_chance": alt_chance_text,  # Add formatted chance
                        }
                    )
            # --- End tooltip data creation ---

            tooltip_json = json.dumps(tooltip_data)
            escaped_tooltip_json = escape(tooltip_json, quote=True)
            escaped_token_text = escape(token.get("text", ""))

            html_parts.append(
                f"<span class='token {prob_class}' data-tooltip='{escaped_tooltip_json}'>"
                f"{escaped_token_text}</span>"
            )

        html_parts.append("</div>")
        return "".join(html_parts)

"""
Main Flask application for Token Probability Visualizer.
"""

from flask import Flask, request, jsonify, render_template

from models.openai_client import OpenAIClient
from models.token_processor import TokenProcessor
import config

# Initialize Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

# Initialize OpenAI client
openai_client = None
try:
    if not config.OPENAI_API_KEY:
        app.logger.warning(
            "OPENAI_API_KEY environment variable not set or empty. OpenAI features will be disabled."
        )
    else:
        openai_client = OpenAIClient(api_key=config.OPENAI_API_KEY)
except ValueError as e:
    app.logger.error(f"Error initializing OpenAI Client: {e}")
except Exception as e:
    app.logger.error(f"Unexpected error initializing OpenAI Client: {e}")


@app.route("/")
def index():
    """Render the main application page."""
    return render_template("index.html")


@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available models from OpenAI API."""
    if not openai_client:
        return jsonify({"error": "OpenAI API key not configured"}), 500

    try:
        models = openai_client.get_available_models()
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate text and get token probabilities."""
    if not openai_client:
        return jsonify({"error": "OpenAI API key not configured"}), 500

    data = request.json
    prompt = data.get("prompt", "")
    model = data.get("model", config.DEFAULT_MODEL)
    temperature = float(data.get("temperature", config.DEFAULT_TEMPERATURE))
    top_p = float(data.get("top_p", config.DEFAULT_TOP_P))
    max_tokens = int(data.get("max_tokens", config.DEFAULT_MAX_TOKENS))

    try:
        # Generate text with token probabilities
        text, tokens = openai_client.generate_with_probabilities(
            prompt=prompt,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            logprobs=config.DEFAULT_LOGPROBS,
        )

        # Process tokens for visualization, passing top_p
        processed_tokens = TokenProcessor.process_tokens(tokens, top_p=top_p)

        # Generate HTML for visualization
        html = TokenProcessor.tokens_to_html(processed_tokens)

        return jsonify({"text": text, "tokens": processed_tokens, "html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get application configuration."""
    return jsonify(
        {
            "default_model": config.DEFAULT_MODEL,
            "default_temperature": config.DEFAULT_TEMPERATURE,
            "default_top_p": config.DEFAULT_TOP_P,
            "default_max_tokens": config.DEFAULT_MAX_TOKENS,
            "available_models": config.AVAILABLE_MODELS,
        }
    )


if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)

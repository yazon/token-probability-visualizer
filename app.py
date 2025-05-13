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


def get_openai_client(
    service_type: str,
    api_key: str = None,
    azure_api_key: str = None,
    azure_endpoint: str = None,
    azure_api_version: str = None,
):
    """Helper function to instantiate OpenAIClient."""
    # The default for service_type argument in this helper should come from the actual request or a sensible default if not provided in request context.
    # For calls from /api/models and /api/generate, service_type is explicitly passed.
    # config.STARTUP_SERVICE_TYPE is not directly used here as service_type is already resolved by the route.
    try:
        client = OpenAIClient(
            service_type=service_type,  # This is the crucial part, passed by the route
            api_key=api_key or config.OPENAI_API_KEY,
            azure_api_key=azure_api_key or config.AZURE_OPENAI_API_KEY,
            azure_endpoint=azure_endpoint or config.AZURE_OPENAI_ENDPOINT,
            azure_api_version=azure_api_version or config.AZURE_API_VERSION,
        )
        app.logger.info(f"OpenAIClient instantiated for service type: {service_type}")
        return client
    except ValueError as e:
        app.logger.error(
            f"Error instantiating OpenAIClient for service type {service_type}: {e}"
        )
        raise
    except Exception as e:
        app.logger.error(
            f"Unexpected error instantiating OpenAIClient for service type {service_type}: {e}"
        )
        raise


@app.route("/")
def index():
    """Render the main application page."""
    return render_template("index.html")


@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available models from OpenAI API based on service_type."""
    service_type = request.args.get(
        "service_type", config.STARTUP_SERVICE_TYPE
    ).lower()  # MODIFIED to use renamed config var

    try:
        client = get_openai_client(service_type)
        if not client:
            return jsonify(
                {
                    "error": f"Could not initialize OpenAI client for service type: {service_type}"
                }
            ), 500

        models = client.get_available_models()
        # Determine default model based on service type for the response
        current_default_model = config.DEFAULT_MODEL
        if service_type == "azure":
            current_default_model = "gpt-35-turbo"  # Azure's specific model/deployment

        return jsonify({"models": models, "default_model": current_default_model})
    except Exception as e:
        app.logger.error(
            f"Error getting models for service type {service_type}: {str(e)}"
        )
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate text and get token probabilities."""
    data = request.json
    service_type = data.get(
        "service_type", config.STARTUP_SERVICE_TYPE
    ).lower()  # MODIFIED to use renamed config var

    try:
        client = get_openai_client(service_type)
        if not client:
            return jsonify(
                {
                    "error": f"Could not initialize OpenAI client for service type: {service_type}"
                }
            ), 500

        prompt = data.get("prompt", "")

        # Determine model to use: if service_type is azure, and model in data is not set or not "gpt-35-turbo", force it.
        # Otherwise, use the model from data or the overall config default.
        current_default_model_for_service = (
            "gpt-35-turbo" if service_type == "azure" else config.DEFAULT_MODEL
        )
        model = data.get("model", current_default_model_for_service)
        if service_type == "azure" and model != "gpt-35-turbo":
            model = (
                "gpt-35-turbo"  # Force to Azure's specific model if service is Azure
            )

        temperature = float(data.get("temperature", config.DEFAULT_TEMPERATURE))
        top_p = float(data.get("top_p", config.DEFAULT_TOP_P))
        max_tokens = int(data.get("max_tokens", config.DEFAULT_MAX_TOKENS))

        # Generate text with token probabilities
        text, tokens = client.generate_with_probabilities(
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
    """Get application configuration for initial frontend setup."""

    startup_service = config.STARTUP_SERVICE_TYPE
    effective_default_model = config.DEFAULT_MODEL
    effective_available_models = config.AVAILABLE_MODELS

    if startup_service == "azure":
        effective_default_model = "gpt-35-turbo"
        effective_available_models = ["gpt-35-turbo"]
        # We also need to ensure Azure is configured if it's the startup type
        # This validation is already in config.py, but an additional check here for robustness
        # or to inform the frontend could be added if desired, though config.py's check is primary.

    return jsonify(
        {
            "default_model": effective_default_model,
            "default_temperature": config.DEFAULT_TEMPERATURE,
            "default_top_p": config.DEFAULT_TOP_P,
            "default_max_tokens": config.DEFAULT_MAX_TOKENS,
            "available_models": effective_available_models,
            "startup_service_type": startup_service,  # RENAMED JSON field
            "azure_openai_endpoint": config.AZURE_OPENAI_ENDPOINT,
        }
    )


if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)

# Token Probability Visualizer

## Overview

The Token Probability Visualizer is a web application that allows you to visualize token probabilities from OpenAI models. You can see the probability of each token in a generated response, with color-coding to indicate different probability levels. The application supports both standard OpenAI and Azure OpenAI services.

## Requirements

- Python 3.10+
- Flask
- OpenAI API key
- Azure OpenAI API key, Endpoint, and API Version (optional, if using Azure OpenAI services)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yazon/token-probability-visualizer.git
cd token-probability-visualizer
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Linux/Mac:
source venv/bin/activate
# On Windows (cmd):
venv\\Scripts\\activate
# On Windows (PowerShell):
.\\venv\\Scripts\\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory and populate it with your API keys and desired settings. You can use `.env.example` as a template. Here's an example:

```
# Flask application settings
SECRET_KEY="your_flask_secret_key_here_for_session_management"

# Determines the default service to use on startup. Can be 'openai' or 'azure'.
# The user can switch between services in the UI if both are configured.
STARTUP_SERVICE_TYPE="openai"

# OpenAI Configuration (Standard)
# Used if STARTUP_SERVICE_TYPE is 'openai' or selected in the UI.
OPENAI_API_KEY="sk-your_openai_api_key_here"

# Azure OpenAI Configuration
# Used if STARTUP_SERVICE_TYPE is 'azure' or selected in the UI.
AZURE_OPENAI_API_KEY="your_azure_openai_api_key_here"
# Your Azure OpenAI resource name (e.g., my-azure-openai-resource). Not the full URL.
AZURE_OPENAI_ENDPOINT="your_azure_openai_resource_name_here"
# The API version for your Azure OpenAI deployment
AZURE_API_VERSION="2024-12-01-preview"
```

Replace placeholder values with your actual credentials and desired configuration.

## Running the Application

1. Start the Flask server:

```bash
python app.py
```

The application will run in debug mode by default.

2. Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

Or `http://<your-local-ip>:5000` if accessing from another device on your network.

## Using the Application

1. **Configure Model Settings**:

   - Select the **Service Type** (OpenAI Standard or Azure OpenAI) from the dropdown.
   - Select an available model from the dropdown menu (models are fetched based on the selected service and your API key/configuration).
   - Adjust temperature (controls randomness, higher = more random).
   - Adjust top_p (controls diversity, lower = more focused).
   - Set maximum tokens to generate.

1. **Enter a Prompt**:

   - Type your prompt in the text area.
   - Click "Generate" or press Ctrl+Enter.

1. **View Token Probabilities**:

   - Generated text will appear with color-coded tokens based on their log probability.
   - Green indicates high probability tokens relative to the chosen `top_p`.
   - Red indicates low probability tokens.
   - Hover over any token to see detailed probability information and alternative likely tokens.

1. **Probability Legend** (Default Colors):

   - High Probability (> 0.8): Bright green
   - Medium-High Probability (> 0.6): Light green
   - Medium Probability (> 0.4): Yellow
   - Medium-Low Probability (> 0.2): Orange
   - Low Probability (\<= 0.2): Red
     *(Note: Colors are defined in `config.py`, thresholds are in `models/token_processor.py`)*

## Troubleshooting

- **API Key Issues**:
  - For **Standard OpenAI**: Ensure your `OPENAI_API_KEY` is correctly set in the `.env` file.
  - For **Azure OpenAI**: Ensure `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_API_VERSION` are correctly set in the `.env` file. The Azure OpenAI option in the UI will be disabled if these are not configured.
  - Make sure the `.env` file is in the project root and is loaded correctly (this happens automatically on startup via `python-dotenv`).
- **Model Availability**: The available models dropdown is populated based on the selected **Service Type** and the models accessible by your corresponding API key and configuration.
  - For **Standard OpenAI**: If a model listed in `config.py` (under `AVAILABLE_MODELS` for OpenAI) doesn't appear, you might not have access to it with your standard OpenAI API key.
  - For **Azure OpenAI**: Only models deployed and configured for your Azure OpenAI service will be available (e.g., a deployment of `gpt-35-turbo`). Ensure your `AZURE_OPENAI_ENDPOINT` and `AZURE_API_VERSION` are correct for the deployments you intend to use.

## License

This project is open source and available under the BSD 3-Clause License.

## Author

- Wojciech Czaplejewicz (czaplejewicz@gmail.com)

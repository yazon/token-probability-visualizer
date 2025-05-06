# Token Probability Visualizer

## Overview
The Token Probability Visualizer is a web application that allows you to visualize token probabilities from OpenAI models. You can see the probability of each token in a generated response, with color-coding to indicate different probability levels.

## Requirements
- Python 3.10+
- Flask
- OpenAI API key

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

4. Create a `.env` file in the project root directory:
```
OPENAI_API_KEY=your-api-key-here
# Optionally add SECRET_KEY=your-flask-secret-key for production
```
Replace `your-api-key-here` with your actual OpenAI API key.

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
   - Select an available model from the dropdown menu (fetched from your OpenAI account).
   - Adjust temperature (controls randomness, higher = more random).
   - Adjust top_p (controls diversity, lower = more focused).
   - Set maximum tokens to generate.

2. **Enter a Prompt**:
   - Type your prompt in the text area.
   - Click "Generate" or press Ctrl+Enter.

3. **View Token Probabilities**:
   - Generated text will appear with color-coded tokens based on their log probability.
   - Green indicates high probability tokens relative to the chosen `top_p`.
   - Red indicates low probability tokens.
   - Hover over any token to see detailed probability information and alternative likely tokens.

4. **Probability Legend** (Default Colors):
   - High Probability (> 0.8): Bright green
   - Medium-High Probability (> 0.6): Light green
   - Medium Probability (> 0.4): Yellow
   - Medium-Low Probability (> 0.2): Orange
   - Low Probability (<= 0.2): Red
   *(Note: Colors are defined in `config.py`, thresholds are in `models/token_processor.py`)*

## Troubleshooting

- **API Key Issues**: Ensure your `OPENAI_API_KEY` is correctly set in the `.env` file in the project root. Make sure the `.env` file is loaded (this happens automatically on startup via `python-dotenv`).
- **Model Availability**: The available models dropdown is populated based on models accessible by your API key. If a model listed in `config.py` doesn't appear, you might not have access to it.
- **Dependency Errors**: Ensure all dependencies are installed correctly using `pip install -r requirements.txt`.

## License
This project is open source and available under the BSD 3-Clause License.

## Author
- Wojciech Czaplejewicz (czaplejewicz@gmail.com)

/**
 * main.js - Main JavaScript functionality for Token Probability Visualizer
 */

// DOM elements
const modelSelect = document.getElementById('model-select');
const temperatureSlider = document.getElementById('temperature-slider');
const temperatureValue = document.getElementById('temperature-value');
const topPSlider = document.getElementById('top-p-slider');
const topPValue = document.getElementById('top-p-value');
const maxTokensInput = document.getElementById('max-tokens-input');
const promptInput = document.getElementById('prompt-input');
const generateBtn = document.getElementById('generate-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const errorMessage = document.getElementById('error-message');
const tokenVisualization = document.getElementById('token-visualization');

// Application state
let config = {
    defaultModel: 'gpt-3.5-turbo-instruct',
    defaultTemperature: 0.7,
    defaultTopP: 1.0,
    defaultMaxTokens: 100,
    availableModels: []
};

// Initialize the application
async function initializeApp() {
    try {
        // Fetch application configuration
        const configResponse = await fetch('/api/config');
        if (!configResponse.ok) {
            throw new Error('Failed to load application configuration');
        }
        
        config = await configResponse.json();
        
        // Set default values
        temperatureSlider.value = config.default_temperature;
        temperatureValue.textContent = config.default_temperature;
        
        topPSlider.value = config.default_top_p;
        topPValue.textContent = config.default_top_p;
        
        maxTokensInput.value = config.default_max_tokens;
        
        // Fetch available models
        const modelsResponse = await fetch('/api/models');
        if (!modelsResponse.ok) {
            throw new Error('Failed to load available models');
        }
        
        const modelsData = await modelsResponse.json();
        
        // Populate model select dropdown
        populateModelSelect(modelsData.models || config.available_models);
        
    } catch (error) {
        showError(error.message);
        console.error('Initialization error:', error);
    }
}

// Populate model select dropdown
function populateModelSelect(models) {
    // Clear existing options
    modelSelect.innerHTML = '';
    
    // Add models to select dropdown
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = typeof model === 'string' ? model : model.id;
        option.textContent = typeof model === 'string' ? model : model.name;
        
        // Set default model as selected
        if (option.value === config.default_model) {
            option.selected = true;
        }
        
        modelSelect.appendChild(option);
    });
}

// Generate text and visualize token probabilities
async function generateText() {
    // Get current configuration values
    const model = modelSelect.value;
    const temperature = parseFloat(temperatureSlider.value);
    const topP = parseFloat(topPSlider.value);
    const maxTokens = parseInt(maxTokensInput.value);
    const prompt = promptInput.value.trim();
    
    // Validate input
    if (!prompt) {
        showError('Please enter a prompt');
        return;
    }
    
    try {
        // Show loading indicator
        showLoading(true);
        hideError();
        
        // Send request to API
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt,
                model,
                temperature,
                top_p: topP,
                max_tokens: maxTokens
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate text');
        }
        
        const data = await response.json();
        
        // Display the visualization
        tokenVisualization.innerHTML = data.html;
        
        // Initialize token tooltips
        initializeTokenTooltips();
        
    } catch (error) {
        showError(error.message);
        console.error('Generation error:', error);
    } finally {
        // Hide loading indicator
        showLoading(false);
    }
}

// Initialize token tooltips
function initializeTokenTooltips() {
    console.log('Initializing tooltips...'); // Log start
    const tokens = document.querySelectorAll('.token');
    console.log(`Found ${tokens.length} token elements.`); // Log count
    
    tokens.forEach((token, index) => {
        console.log(`Processing token ${index + 1}`); // Log each token
        try {
            // Get tooltip data from data attribute (as JSON)
            const tooltipJSON = token.getAttribute('data-tooltip');
            console.log('  Raw data-tooltip:', tooltipJSON); // Log raw JSON
            if (!tooltipJSON) {
                console.warn('  Token missing data-tooltip attribute.');
                return; // Skip if attribute is missing
            }
            
            const tooltipData = JSON.parse(tooltipJSON);
            console.log('  Parsed tooltip data:', tooltipData); // Log parsed data
            
            // --- Get the color class for the main token --- Needed for the tooltip text
            // We need to retrieve it from the parent token's class list
            let mainTokenColorClass = 'unknown-prob';
            const tokenClasses = token.className.split(' ');
            const probClasses = ['high-prob', 'medium-high-prob', 'medium-prob', 'medium-low-prob', 'low-prob'];
            for (const cls of tokenClasses) {
                if (probClasses.includes(cls)) {
                    mainTokenColorClass = cls;
                    break;
                }
            }
            // --- End getting main token color class ---
            
            // Create tooltip element
            const tooltip = document.createElement('div');
            tooltip.className = 'token-tooltip';
            
            // Create token info - Add span with color class for the token text
            let tooltipHTML = `<div class="token-info">Token: <span class="${mainTokenColorClass}">${tooltipData.text}</span></div>`;
            tooltipHTML += `<div class="token-info">Probability: ${tooltipData.probability}</div>`;
            tooltipHTML += `<div class="token-info">Log Probability: ${tooltipData.logprob}</div>`;
            // Add Selection Chance for main token
            if (tooltipData.selection_chance !== undefined) {
                 tooltipHTML += `<div class="token-info">Selection Chance (Top P): ${tooltipData.selection_chance}</div>`;
            }
            
            // Add alternatives if available
            if (tooltipData.alternatives && tooltipData.alternatives.length > 0) {
                tooltipHTML += '<div class="token-alternatives"><h4>Alternatives:</h4>';
                
                tooltipData.alternatives.forEach(alt => {
                    const altColorClass = alt.color_class || 'unknown-prob'; 
                    tooltipHTML += `<div class="alt-token ${altColorClass}">`; 
                    tooltipHTML += `<span class="alt-text"><span class="${altColorClass}">${alt.text}</span></span>`; 
                    tooltipHTML += `<span class="alt-prob">P: ${alt.probability}</span>`;
                    tooltipHTML += `<span class="alt-logprob">LogP: ${alt.logprob}</span>`;
                    // Add Selection Chance for alternative token
                    if (alt.selection_chance !== undefined) {
                        tooltipHTML += `<span class="alt-chance">Chance: ${alt.selection_chance}</span>`;
                    }
                    tooltipHTML += '</div>';
                });
                
                tooltipHTML += '</div>';
            }
            
            tooltip.innerHTML = tooltipHTML;
            console.log('  Generated tooltip HTML:', tooltipHTML); // Log generated HTML
            
            // Add tooltip to token
            token.appendChild(tooltip);
            console.log('  Appended tooltip element:', tooltip); // Log appended element
            
            // Remove data-tooltip attribute to avoid duplication
            token.removeAttribute('data-tooltip');
        } catch (error) {
            console.error(`Error creating tooltip for token ${index + 1}:`, error, 'Raw JSON:', tooltipJSON); // Log errors with context
        }
    });
    console.log('Tooltip initialization finished.'); // Log end
}

// Show/hide loading indicator
function showLoading(isLoading) {
    if (isLoading) {
        loadingIndicator.classList.remove('hidden');
        generateBtn.disabled = true;
    } else {
        loadingIndicator.classList.add('hidden');
        generateBtn.disabled = false;
    }
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// Hide error message
function hideError() {
    errorMessage.classList.add('hidden');
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    initializeApp();
    
    // Temperature slider
    temperatureSlider.addEventListener('input', () => {
        // Format to two decimal places
        temperatureValue.textContent = parseFloat(temperatureSlider.value).toFixed(2);
    });
    
    // Top P slider
    topPSlider.addEventListener('input', () => {
        // Format to two decimal places
        topPValue.textContent = parseFloat(topPSlider.value).toFixed(2);
    });
    
    // Generate button
    generateBtn.addEventListener('click', generateText);
    
    // Allow Enter key in prompt input to trigger generation
    promptInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && event.ctrlKey) {
            event.preventDefault();
            generateText();
        }
    });
});

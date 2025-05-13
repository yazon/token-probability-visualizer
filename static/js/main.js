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
const serviceTypeSelect = document.getElementById('service-type-select');

// Application state
let appConfig = {
    default_model: 'gpt-3.5-turbo-instruct',
    default_temperature: 0.8,
    default_top_p: 1.0,
    default_max_tokens: 10,
    startup_service_type: 'openai',
    azure_openai_endpoint: null
};
let currentModels = [];
let currentDefaultModel = '';

// Initialize the application
async function initializeApp() {
    try {
        // Fetch application configuration
        const configResponse = await fetch('/api/config');
        if (!configResponse.ok) {
            throw new Error('Failed to load application configuration');
        }
        appConfig = await configResponse.json();

        // Set UI defaults from fetched appConfig
        temperatureSlider.value = appConfig.default_temperature;
        temperatureValue.textContent = appConfig.default_temperature;
        topPSlider.value = appConfig.default_top_p;
        topPValue.textContent = appConfig.default_top_p;
        maxTokensInput.value = appConfig.default_max_tokens;

        // Configure Service Type Selector
        serviceTypeSelect.value = appConfig.startup_service_type;
        const azureOption = serviceTypeSelect.querySelector('option[value="azure"]');
        if (azureOption && (!appConfig.azure_openai_endpoint || appConfig.azure_openai_endpoint.trim() === '')) {
            azureOption.disabled = true;
            if (serviceTypeSelect.value === 'azure') {
                serviceTypeSelect.value = 'openai';
                showError('Azure OpenAI is not configured on the backend. Falling back to standard OpenAI.');
            }
        }
        
        // Add event listener for service type change
        serviceTypeSelect.addEventListener('change', async (event) => {
            const selectedService = event.target.value;
            await loadModelsForService(selectedService);
        });

        // Initial load of models for the selected/default service type
        await loadModelsForService(serviceTypeSelect.value);

    } catch (error) {
        showError(error.message);
        console.error('Initialization error:', error);
    }
}

// Load models based on service type
async function loadModelsForService(serviceType) {
    console.log(`Loading models for service: ${serviceType}`);
    modelSelect.disabled = true;
    modelSelect.innerHTML = '<option>Loading models...</option>';

    try {
        const modelsResponse = await fetch(`/api/models?service_type=${serviceType}`);
        if (!modelsResponse.ok) {
            const errorData = await modelsResponse.json();
            throw new Error(errorData.error || `Failed to load models for ${serviceType}`);
        }
        const modelsData = await modelsResponse.json();
        currentModels = modelsData.models || [];
        currentDefaultModel = modelsData.default_model || (serviceType === 'azure' ? 'gpt-35-turbo' : appConfig.default_model);
        
        populateModelSelect(currentModels, currentDefaultModel);

    } catch (error) {
        showError(`Error loading models: ${error.message}`);
        console.error('Model loading error:', error);
        modelSelect.innerHTML = '<option>Error loading</option>';
    } finally {
        modelSelect.disabled = false;
    }
}

// Populate model select dropdown
function populateModelSelect(models, defaultModelToSelect) {
    modelSelect.innerHTML = '';

    if (!models || models.length === 0) {
        const option = document.createElement('option');
        option.value = "";
        option.textContent = "No models available";
        modelSelect.appendChild(option);
        modelSelect.disabled = true;
        return;
    }
    modelSelect.disabled = false;

    models.forEach(model => {
        const option = document.createElement('option');
        option.value = typeof model === 'string' ? model : model.id;
        option.textContent = typeof model === 'string' ? model : model.name;
        if (option.value === defaultModelToSelect) {
            option.selected = true;
        }
        modelSelect.appendChild(option);
    });
}

// Generate text and visualize token probabilities
async function generateText() {
    const selectedServiceType = serviceTypeSelect.value;
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
                max_tokens: maxTokens,
                service_type: selectedServiceType
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
    console.log('Initializing tooltips...');
    const tokens = document.querySelectorAll('.token');
    console.log(`Found ${tokens.length} token elements.`);
    
    tokens.forEach((token, index) => {
        console.log(`Processing token ${index + 1}`);
        try {
            // Get tooltip data from data attribute (as JSON)
            const tooltipJSON = token.getAttribute('data-tooltip');
            console.log('  Raw data-tooltip:', tooltipJSON);
            if (!tooltipJSON) {
                console.warn('  Token missing data-tooltip attribute.');
                return;
            }
            
            const tooltipData = JSON.parse(tooltipJSON);
            console.log('  Parsed tooltip data:', tooltipData);
            
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
            console.log('  Generated tooltip HTML:', tooltipHTML);
            
            // Add tooltip to token
            token.appendChild(tooltip);
            console.log('  Appended tooltip element:', tooltip);
            
            // Remove data-tooltip attribute to avoid duplication
            token.removeAttribute('data-tooltip');
        } catch (error) {
            console.error(`Error creating tooltip for token ${index + 1}:`, error, 'Raw JSON:', tooltipJSON);
        }
    });
    console.log('Tooltip initialization finished.');
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
    const maxLength = 200; // Max length before truncation
    if (message.length > maxLength) {
        message = message.substring(0, maxLength - 3) + "...";
    }
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

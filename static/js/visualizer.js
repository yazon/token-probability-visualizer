/**
 * visualizer.js - Token visualization functionality for Token Probability Visualizer
 */

// Constants for visualization
const PROBABILITY_THRESHOLDS = {
    HIGH: 0.8,
    MEDIUM_HIGH: 0.6,
    MEDIUM: 0.4,
    MEDIUM_LOW: 0.2
};

const PROBABILITY_COLORS = {
    HIGH: '#00cc00',        // Bright green
    MEDIUM_HIGH: '#66cc33', // Light green
    MEDIUM: '#cccc00',      // Yellow
    MEDIUM_LOW: '#cc6600',  // Orange
    LOW: '#cc0000',         // Red
    UNKNOWN: '#808080'      // Gray
};

/**
 * Calculate color based on token probability
 * @param {number} probability - Token probability (0.0 to 1.0)
 * @returns {string} - Hex color code
 */
function calculateColor(probability) {
    if (probability === null || probability === undefined) {
        return PROBABILITY_COLORS.UNKNOWN;
    }
    
    if (probability > PROBABILITY_THRESHOLDS.HIGH) {
        return PROBABILITY_COLORS.HIGH;
    } else if (probability > PROBABILITY_THRESHOLDS.MEDIUM_HIGH) {
        return PROBABILITY_COLORS.MEDIUM_HIGH;
    } else if (probability > PROBABILITY_THRESHOLDS.MEDIUM) {
        return PROBABILITY_COLORS.MEDIUM;
    } else if (probability > PROBABILITY_THRESHOLDS.MEDIUM_LOW) {
        return PROBABILITY_COLORS.MEDIUM_LOW;
    } else {
        return PROBABILITY_COLORS.LOW;
    }
}

/**
 * Format probability value for display
 * @param {number} probability - Probability value
 * @param {number} decimalPlaces - Number of decimal places to show
 * @returns {string} - Formatted probability string
 */
function formatProbability(probability, decimalPlaces = 4) {
    if (probability === null || probability === undefined) {
        return 'N/A';
    }
    
    return probability.toFixed(decimalPlaces);
}

/**
 * Create HTML for token visualization
 * @param {Array} tokens - Array of token objects with probability information
 * @returns {string} - HTML string for visualization
 */
function createTokenVisualizationHTML(tokens) {
    let html = '<div class="token-container">';
    
    tokens.forEach(token => {
        const color = calculateColor(token.probability);
        const probText = formatProbability(token.probability);
        const logprobText = token.logprob !== null ? formatProbability(token.logprob) : 'N/A';
        
        // Create tooltip content - encode HTML entities to avoid HTML injection and encoding issues
        let tooltipData = {};
        tooltipData.text = token.text;
        tooltipData.probability = probText;
        tooltipData.logprob = logprobText;
        tooltipData.alternatives = [];
        
        // Add alternatives if available
        if (token.top_alternatives && token.top_alternatives.length > 0) {
            token.top_alternatives.forEach(alt => {
                tooltipData.alternatives.push({
                    text: alt.text,
                    probability: formatProbability(alt.probability),
                    logprob: alt.logprob !== null ? formatProbability(alt.logprob) : 'N/A',
                    color: calculateColor(alt.probability)
                });
            });
        }
        
        // Store the data as JSON in the data-tooltip attribute
        const tooltipJSON = JSON.stringify(tooltipData);
        
        // Create token element
        html += `<span class="token" style="background-color: ${color};" data-tooltip='${tooltipJSON}'>`;
        html += token.text;
        html += '</span>';
    });
    
    html += '</div>';
    return html;
}

/**
 * Process raw token data from API
 * @param {Array} rawTokens - Raw token data from API
 * @returns {Array} - Processed tokens with visualization data
 */
function processTokens(rawTokens) {
    return rawTokens.map(token => {
        const processed = {
            token: token.token || '',
            text: token.text || '',
            probability: token.probability,
            logprob: token.logprob,
            color: calculateColor(token.probability),
            top_alternatives: []
        };
        
        // Process alternatives
        if (token.top_logprobs) {
            for (const [text, info] of Object.entries(token.top_logprobs)) {
                processed.top_alternatives.push({
                    text: text,
                    probability: info.probability,
                    logprob: info.logprob,
                    color: calculateColor(info.probability)
                });
            }
            
            // Sort alternatives by probability
            processed.top_alternatives.sort((a, b) => 
                (b.probability || 0) - (a.probability || 0)
            );
        }
        
        return processed;
    });
}

// Export functions for use in main.js
window.TokenVisualizer = {
    calculateColor,
    formatProbability,
    createTokenVisualizationHTML,
    processTokens
};

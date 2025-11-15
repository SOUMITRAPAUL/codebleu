// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State
let generatedCode = '';
let currentFilename = '';

// DOM Elements
const languageSelect = document.getElementById('language');
const queryInput = document.getElementById('query');
const generateBtn = document.getElementById('generateBtn');
const referenceCodeInput = document.getElementById('referenceCode');
const validateBtn = document.getElementById('validateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const generatedCodeSection = document.getElementById('generatedCodeSection');
const generatedCodeElement = document.getElementById('generatedCode');
const validationResults = document.getElementById('validationResults');

// Event Listeners
generateBtn.addEventListener('click', generateCode);
validateBtn.addEventListener('click', validateCode);
downloadBtn.addEventListener('click', downloadCode);

// Check if generated code exists to enable validation
queryInput.addEventListener('input', () => {
    validateBtn.disabled = !generatedCode;
});

// Generate Code Function
async function generateCode() {
    const query = queryInput.value.trim();
    const language = languageSelect.value;

    if (!query) {
        showStatus('Please enter a code request', 'error');
        return;
    }

    setButtonLoading(generateBtn, true);

    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, language })
        });

        const data = await response.json();

        if (data.success) {
            generatedCode = data.code;
            currentFilename = data.filename;

            generatedCodeElement.textContent = generatedCode;
            generatedCodeSection.style.display = 'block';
            validateBtn.disabled = false;

            showStatus('Code generated successfully!', 'success');
        } else {
            showStatus(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Generation error:', error);
        showStatus('Failed to generate code. Make sure backend is running.', 'error');
    } finally {
        setButtonLoading(generateBtn, false);
    }
}

// Validate Code Function
async function validateCode() {
    const reference = referenceCodeInput.value.trim();
    const language = languageSelect.value;

    if (!reference) {
        showStatus('Please provide reference code for validation', 'error');
        return;
    }

    if (!generatedCode) {
        showStatus('Please generate code first', 'error');
        return;
    }

    setButtonLoading(validateBtn, true);

    try {
        const response = await fetch(`${API_BASE_URL}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                generated: generatedCodeElement.textContent, // full code
                reference: reference,
                language
            })
        });

        const data = await response.json();

        if (data.success) {
            displayValidationResults(data.results);
            showStatus('Validation complete!', 'success');
        } else {
            showStatus(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Validation error:', error);
        showStatus('Failed to validate code. Make sure backend is running.', 'error');
    } finally {
        setButtonLoading(validateBtn, false);
    }
}

// Display Validation Results
function displayValidationResults(results) {
    validationResults.style.display = 'block';

    document.getElementById('codebluScore').textContent = results.codebleu;
    document.getElementById('weightedNgramScore').textContent = results.weighted_ngram_match;
    document.getElementById('qualityBadge').textContent = results.quality;

    // Set quality color
    const score = parseFloat(results.codebleu);
    let color = 'rgba(239, 68, 68, 0.3)';
    if (score >= 0.8) color = 'rgba(16, 185, 129, 0.3)';
    else if (score >= 0.6) color = 'rgba(59, 130, 246, 0.3)';
    else if (score >= 0.4) color = 'rgba(251, 191, 36, 0.3)';
    document.getElementById('qualityBadge').style.background = color;

    // Component Scores
    document.getElementById('ngramScore').textContent = results.ngram_match;
    document.getElementById('syntaxScore').textContent = results.syntax_match;
    document.getElementById('dataflowScore').textContent = results.dataflow_match;

    // Progress Bars
    document.getElementById('ngramBar').style.width = `${results.ngram_match * 100}%`;
    document.getElementById('syntaxBar').style.width = `${results.syntax_match * 100}%`;
    document.getElementById('dataflowBar').style.width = `${results.dataflow_match * 100}%`;
    document.getElementById('weightedNgramBar').style.width = `${results.weighted_ngram_match * 100}%`;

    // Recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    results.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recommendationsList.appendChild(li);
    });

    validationResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download Code Function
function downloadCode() {
    if (!generatedCode) {
        showStatus('No code to download', 'error');
        return;
    }

    const language = languageSelect.value;
    const extensions = { python: 'py', cpp: 'cpp', java: 'java', javascript: 'js', c: 'c' };
    const ext = extensions[language] || 'txt';
    const filename = currentFilename || `generated_code_${Date.now()}.${ext}`;

    const blob = new Blob([generatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);

    showStatus('Code downloaded successfully!', 'success');
}

// Helper Functions
function setButtonLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const loader = button.querySelector('.loader');
    if (isLoading) {
        if (btnText) btnText.style.display = 'none';
        if (loader) loader.style.display = 'block';
        button.disabled = true;
    } else {
        if (btnText) btnText.style.display = 'block';
        if (loader) loader.style.display = 'none';
        button.disabled = false;
    }
}

function showStatus(message, type = 'info') {
    const statusMessage = document.getElementById('statusMessage');
    if (!statusMessage) return;
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
    setTimeout(() => { statusMessage.style.display = 'none'; }, 5000);
}

// Check backend health on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            console.log('✅ Backend connected:', data);
            showStatus('Connected to backend', 'success');
        }
    } catch (error) {
        console.error('Backend connection failed:', error);
        showStatus('⚠️ Backend not connected. Run: python backend/app.py', 'error');
    }
}

// Initialize
window.addEventListener('load', () => {
    checkBackendHealth();
});

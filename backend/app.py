"""
Flask API for AI Code Generator & Validator
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from code_generator import CodeGenerator
from code_validator import CodeValidator

app = Flask(__name__)
CORS(app)

# Initialize generator and validator
generator = CodeGenerator()
validator = CodeValidator()

# Create output directory
os.makedirs('output', exist_ok=True)

@app.route('/api/generate', methods=['POST'])
def generate_code():
    """Generate code based on user query"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        language = data.get('language', 'python').strip().lower()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Generate code
        code = generator.generate(query, language)
        filename = generator.save_to_file(code, language)
        
        return jsonify({
            'success': True,
            'code': code,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_code():
    """Validate generated code using CodeBLEU"""
    try:
        data = request.json
        generated = data.get('generated', '').strip()
        reference = data.get('reference', '').strip()
        language = data.get('language', 'python').strip().lower()
        
        if not generated or not reference:
            return jsonify({'error': 'Both generated and reference code are required'}), 400
        
        results = validator.validate(generated, reference, language)
        
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated code file"""
    filepath = os.path.join('output', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'model': generator.model_name, 'backend': 'ollama'})

@app.route('/')
def home():
    return jsonify({
        'message': 'AI Code Generator & Validator API',
        'endpoints': {
            'generate': '/api/generate [POST]',
            'validate': '/api/validate [POST]',
            'download': '/api/download/<filename> [GET]',
            'health': '/api/health [GET]'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting AI Code Generator API on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

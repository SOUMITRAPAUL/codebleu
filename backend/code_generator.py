"""
Code Generator using Local LLM Models
Generates full executable code for any query/task
Supports: Ollama, LLaMA.cpp, GPT4All
"""

import requests
import re
import os
from datetime import datetime

class CodeGenerator:
    def __init__(self, model_name="codellama:7b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.system_prompt = (
            "You are an expert programmer. "
            "Write full executable code only. "
            "Do not include explanations, comments, markdown, or extra text. "
            "Use best practices and standard libraries for the language."
        )

    def generate(self, query, language="python"):
        """
        Generate full executable code for a query in a given language.
        Falls back to template only if LLM fails.
        """
        try:
            return self._generate_llm(query, language)
        except Exception as e:
            print("⚠️ LLM generation failed, using fallback template:", e)
            return self._generate_template(query, language)

    def _generate_llm(self, query, language):
        prompt = f"Write {language} code for the following task:\n{query}\nReturn ONLY the code."
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "system": self.system_prompt,
                "temperature": 0.2,
                "stream": False
            },
            timeout=60
        )
        if response.status_code == 200:
            code = response.json().get("response", "")
            return self._clean_code(code)
        raise Exception(f"LLM API error {response.status_code}")

    def _clean_code(self, code):
        """Remove unwanted markdown or explanation lines."""
        code = re.sub(r'```[\w]*', '', code)
        code = re.sub(r'```', '', code)
        lines = [line for line in code.splitlines()
                 if not re.match(r'(here is|this code|example:|note:)', line.lower())]
        return "\n".join(lines).strip()

    def _generate_template(self, query, language):
        """Fallback template for basic code structure if LLM fails."""
        templates = {
            "python": f'def solution():\n    """Task: {query}"""\n    pass\n\nif __name__=="__main__":\n    print(solution())',
            "cpp": f'#include <iostream>\nusing namespace std;\n\nint main() {{\n    // Task: {query}\n    return 0;\n}}',
            "java": f'public class Solution {{\n    public static void main(String[] args) {{\n        // Task: {query}\n    }}\n}}',
            "javascript": f'function solution() {{\n    // Task: {query}\n}}\nconsole.log(solution());',
            "c": f'#include <stdio.h>\nint main() {{\n    // Task: {query}\n    return 0;\n}}'
        }
        return templates.get(language.lower(), templates["python"])

    def save_to_file(self, code, language):
        """Save generated code to a timestamped file."""
        extensions = {'python':'py','cpp':'cpp','c++':'cpp','java':'java','javascript':'js','js':'js','c':'c'}
        ext = extensions.get(language.lower(), 'txt')
        os.makedirs('output', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"generated_code_{timestamp}.{ext}"
        with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"✅ Code saved to output/{filename}")
        return filename

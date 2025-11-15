# backend/code_validator.py

from typing import Dict
import re

class CodeValidator:
    def __init__(self, weights=(0.4, 0.4, 0.1, 0.1)):
        # ngram, weighted_ngram, syntax, dataflow
        self.weights = weights

    def validate(self, generated_code: str, reference_code: str, language: str) -> Dict:
        # Tokenize
        gen_tokens = self._tokenize(generated_code)
        ref_tokens = self._tokenize(reference_code)

        # N-gram matches
        ngram_score = self._ngram_match(gen_tokens, ref_tokens)
        weighted_ngram_score = self._weighted_ngram_match(gen_tokens, ref_tokens)

        # Simulated syntax/dataflow (Windows-friendly)
        syntax_score = self._syntax_match(gen_tokens, ref_tokens)
        dataflow_score = self._dataflow_match(gen_tokens, ref_tokens)

        # Combined CodeBLEU
        codebleu = (
            self.weights[0] * ngram_score +
            self.weights[1] * weighted_ngram_score +
            self.weights[2] * syntax_score +
            self.weights[3] * dataflow_score
        )

        return {
            'codebleu': round(codebleu, 4),
            'ngram_match': round(ngram_score, 4),
            'weighted_ngram_match': round(weighted_ngram_score, 4),
            'syntax_match': round(syntax_score, 4),
            'dataflow_match': round(dataflow_score, 4),
            'quality': self._assess_quality(codebleu),
            'recommendations': self._generate_recommendations(
                ngram_score, syntax_score, dataflow_score
            )
        }

    # -------- Helper functions --------
    def _tokenize(self, code: str):
        # Remove comments
        code = re.sub(r'#.*$|//.*$|/\*.*?\*/', '', code, flags=re.MULTILINE|re.DOTALL)
        # Split tokens
        tokens = re.findall(r'\b\w+\b|[^\w\s]', code.lower())
        return [t for t in tokens if t.strip()]

    def _ngram_match(self, gen_tokens, ref_tokens, n_max=4):
        scores = []
        for n in range(1, n_max+1):
            gen_ngrams = [tuple(gen_tokens[i:i+n]) for i in range(len(gen_tokens)-n+1)]
            ref_ngrams = [tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens)-n+1)]
            if not gen_ngrams: continue
            matches = sum(1 for g in gen_ngrams if g in ref_ngrams)
            scores.append(matches / len(gen_ngrams))
        return sum(scores)/len(scores) if scores else 0.0

    def _weighted_ngram_match(self, gen_tokens, ref_tokens):
        keywords = {'def','class','if','else','for','while','return','import','from','try','except','with','function','var','let','const','public','private','static'}
        gen_set, ref_set = set(gen_tokens), set(ref_tokens)
        common = gen_set & ref_set
        common_kw = sum(2 if t in keywords else 1 for t in common)
        total_kw = sum(2 if t in keywords else 1 for t in ref_set)
        return common_kw / total_kw if total_kw > 0 else 0.0

    def _syntax_match(self, gen_tokens, ref_tokens):
        # Simple proxy: % of keywords present
        keywords = {'def','class','if','else','for','while','return','import','from','try','except','with','function','var','let','const','public','private','static'}
        gen_kw = set(gen_tokens) & keywords
        ref_kw = set(ref_tokens) & keywords
        return len(gen_kw & ref_kw) / len(ref_kw) if ref_kw else 1.0

    def _dataflow_match(self, gen_tokens, ref_tokens):
        # Simple proxy: common variable names
        gen_vars = {t for t in gen_tokens if t.isidentifier()}
        ref_vars = {t for t in ref_tokens if t.isidentifier()}
        return len(gen_vars & ref_vars) / len(ref_vars) if ref_vars else 1.0

    def _assess_quality(self, score: float):
        if score >= 0.8: return "Excellent - Production Ready"
        if score >= 0.6: return "Good - Minor Improvements Needed"
        if score >= 0.4: return "Fair - Significant Improvements Needed"
        if score >= 0.2: return "Poor - Major Revision Required"
        return "Very Poor - Complete Rewrite Recommended"

    def _generate_recommendations(self, ngram, syntax, dataflow):
        recs = []
        if ngram < 0.5: recs.append("Improve token-level similarity with reference code.")
        if syntax < 0.5: recs.append("Review code structure / syntax match.")
        if dataflow < 0.5: recs.append("Check semantic logic and variable usage consistency.")
        if ngram >= 0.7 and syntax >= 0.7 and dataflow >= 0.7: recs.append("Code quality is excellent! Ready for production use.")
        if not recs: recs.append("Code quality is good overall.")
        return recs

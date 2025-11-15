import re
from collections import Counter

LANG_KEYWORDS = {
    "python": {"def","return","if","elif","else","for","while","class","import","from","pass","yield","lambda"},
    "cpp": {"int","long","float","double","char","void","return","if","else","for","while","class","struct","include"},
    "java": {"class","public","private","protected","static","final","void","int","long","double","float","char","boolean","return"},
    "javascript": {"function","return","if","else","for","while","class","const","let","var","new","try","catch","throw"}
}

def tokenize_code(text: str):
    """Simple tokenizer: words and single symbols."""
    return re.findall(r"\w+|[^\s\w]", text)

def ngram_counts(tokens, n):
    return Counter(tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1))

def clipped_precision(candidate_tokens, reference_tokens, n):
    cand_counts = ngram_counts(candidate_tokens, n)
    ref_counts = ngram_counts(reference_tokens, n)
    clip = sum(min(c, ref_counts.get(ng, 0)) for ng, c in cand_counts.items())
    total = sum(cand_counts.values())
    return clip / total if total > 0 else 0.0

def bleu_4(candidate_tokens, reference_tokens):
    precisions = [clipped_precision(candidate_tokens, reference_tokens, n) for n in range(1, 5)]
    if any(p == 0 for p in precisions):
        geo_mean = 0.0
    else:
        prod = 1.0
        for p in precisions: prod *= p
        geo_mean = prod ** 0.25
    bp = 1.0 if len(candidate_tokens) > len(reference_tokens) else (len(candidate_tokens)/len(reference_tokens) if reference_tokens else 1.0)
    return bp * geo_mean

def keyword_weighted_precision(candidate_tokens, reference_tokens, language):
    keywords = LANG_KEYWORDS.get(language, set())
    weight_factor = 1.1
    score, total = 0.0, 0.0
    for n in range(1, 5):
        cand_counts = ngram_counts(candidate_tokens, n)
        ref_counts = ngram_counts(reference_tokens, n)
        for ng, c in cand_counts.items():
            w = weight_factor if any(tok in keywords for tok in ng) else 1.0
            total += w * c
            score += w * min(c, ref_counts.get(ng, 0))
    return score / total if total > 0 else 0.0

def syntax_overlap(candidate: str, reference: str):
    ops = ["=", "==", "!=", "<", ">", "+", "-", "*", "/", "%"]
    braces = ["(", ")", "{", "}", "[", "]", ";", ","]
    def freq(text, symbols): return Counter(tok for tok in tokenize_code(text) if tok in symbols)
    cand_ops, ref_ops = freq(candidate, ops), freq(reference, ops)
    cand_br, ref_br = freq(candidate, braces), freq(reference, braces)
    def jaccard_like(a, b):
        keys = set(a.keys()) | set(b.keys())
        inter = sum(min(a.get(k,0), b.get(k,0)) for k in keys)
        union = sum(max(a.get(k,0), b.get(k,0)) for k in keys)
        return inter/union if union>0 else 0.0
    return 0.5*jaccard_like(cand_ops, ref_ops) + 0.5*jaccard_like(cand_br, ref_br)

def compute_codebleu_detailed(reference: str, candidate: str, language: str="python") -> dict:
    ref_tokens, cand_tokens = tokenize_code(reference), tokenize_code(candidate)

    bleu = bleu_4(cand_tokens, ref_tokens)
    kw = keyword_weighted_precision(cand_tokens, ref_tokens, language)
    syn = syntax_overlap(candidate, reference)

    identifiers_ref = [tok for tok in ref_tokens if tok.isidentifier() and tok not in LANG_KEYWORDS.get(language, set())]
    identifiers_cand = [tok for tok in cand_tokens if tok.isidentifier() and tok not in LANG_KEYWORDS.get(language, set())]
    overlap = len(set(identifiers_ref) & set(identifiers_cand))
    penalty = overlap / max(len(set(identifiers_ref + identifiers_cand)), 1)

    final_score = (0.4*bleu + 0.4*kw + 0.2*syn) * penalty

    recommendations = []
    if penalty < 1.0:
        recommendations.append("Identifiers differ between candidate and reference.")
    if bleu < 0.7:
        recommendations.append("N-gram overlap is low, consider revising logic.")
    if kw < 0.7:
        recommendations.append("Keyword usage differs, check control structures.")
    if syn < 0.7:
        recommendations.append("Syntax structure mismatch, review operators/braces.")

    return {
        "BLEU-4": round(bleu, 4),
        "KeywordPrecision": round(kw, 4),
        "SyntaxOverlap": round(syn, 4),
        "IdentifierPenalty": round(penalty, 4),
        "FinalScore": round(final_score, 4),
        "Recommendations": recommendations or ["Code looks structurally similar."]
    }

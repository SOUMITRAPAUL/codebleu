from evaluator import compute_codebleu_detailed

def run_tests():
    reference = """def add(a, b):
    return a + b"""

    candidate_good = """def add(x, y):
    return x + y"""

    candidate_bad = """def multiply(a, b):
    return a * b"""

    print("=== Good Candidate ===")
    print(compute_codebleu_detailed(reference, candidate_good, "python"))

    print("\n=== Bad Candidate ===")
    print(compute_codebleu_detailed(reference, candidate_bad, "python"))

if __name__ == "__main__":
    run_tests()

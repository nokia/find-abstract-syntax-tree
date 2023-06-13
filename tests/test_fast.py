#!/usr/bin/env pytest-3

from fast import fast

def test_fast():
    samples = ["abc", "abcabc", "abcabcabc"]
    results = fast(samples)
    for (score, ast) in results:
        print(score, ast.to_infix_regexp_str())

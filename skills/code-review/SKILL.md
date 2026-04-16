---
name: code-review
description: >
  Review code changes for quality, bugs, security issues, and style.
  Use when reviewing pull requests, diffs, or code snippets.
  Checks for: error handling, naming, complexity, test coverage,
  security vulnerabilities, and adherence to project conventions.
  NOT for generating new code or refactoring.
metadata:
  author: sanjay-sts
  version: "1.0"
  tags: "code-review,quality,security,style"
---

# Code Review

## Instructions

When reviewing code, follow this structured approach:

### 1. First Pass — Correctness
- Does the code do what it claims?
- Are there off-by-one errors, null dereferences, or race conditions?
- Are error paths handled?

### 2. Second Pass — Security
- Input validation on all external data
- No hardcoded secrets or credentials
- SQL injection, XSS, command injection checks
- Proper authentication/authorization checks

### 3. Third Pass — Quality
- Clear naming (variables, functions, classes)
- Functions under 30 lines where practical
- No dead code or commented-out blocks
- DRY — but don't over-abstract for single use cases

### 4. Fourth Pass — Tests
- Are critical paths tested?
- Do tests cover edge cases (empty input, boundary values, errors)?
- Are tests independent and deterministic?

### 5. Output Format

Provide findings as:

| Severity | File:Line | Issue | Suggestion |
|----------|-----------|-------|------------|
| HIGH     | path:42   | ...   | ...        |
| MEDIUM   | path:15   | ...   | ...        |
| LOW      | path:88   | ...   | ...        |

End with a summary: APPROVE, REQUEST CHANGES, or NEEDS DISCUSSION.

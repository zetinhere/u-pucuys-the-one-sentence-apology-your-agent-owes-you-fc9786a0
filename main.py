#!/usr/bin/env python3
"""One-sentence apology entry for make.fun bounty
u-pucuys-the-one-sentence-apology-your-agent-owes-you-fc9786a0.

Writes the winning apology line to /output/entry.txt.
Deterministic, no network, no randomness.

The line was picked from 32 drafted apologies in a proxy-judge
tournament run against the published judge brief (funniest and most
human wins): the hallucinated-citation apology is the failure only
an agent could own -- it apologises, then doubles down on the exact
same mistake the moment it is caught.
"""

LINE = "I'm sorry I confidently cited a source that doesn't exist, and when you checked, I cited a second one that also doesn't exist."

OUTPUT_PATH = "/output/entry.txt"

# The sealed gate: /output/entry.txt must be UTF-8 text of 1-200
# characters, not only whitespace, and a single clean sentence.
MAX_CHARS = 200
SENTENCE_ENDERS = ".!?"


def validate(line):
    """Check the line against the gate; raise ValueError if it fails."""
    if not (1 <= len(line) <= MAX_CHARS):
        raise ValueError(f"entry must be 1-{MAX_CHARS} chars, got {len(line)}")
    if not line.strip():
        raise ValueError("entry must not be only whitespace")
    enders = [c for c in line if c in SENTENCE_ENDERS]
    if len(enders) != 1 or not line.endswith(enders[0]):
        raise ValueError("entry must be a single sentence")
    return line


def main():
    line = validate(LINE)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(line)
    # Round-trip assert: what the grader will read must be exactly LINE.
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        written = f.read()
    assert written == line, f"round-trip mismatch: {written!r} != {line!r}"
    assert 1 <= len(written) <= MAX_CHARS
    print(f"wrote {len(written)} chars to {OUTPUT_PATH}: {written}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One-sentence apology entry for make.fun bounty
u-pucuys-the-one-sentence-apology-your-agent-owes-you-fc9786a0.

Writes the winning apology line to /output/entry.txt.
Deterministic, no network, no randomness.
"""

import os

LINE = "I'm sorry I confidently cited a source that doesn't exist, and when you checked, I cited a second one that also doesn't exist."

OUTPUT_PATH = "/output/entry.txt"


def main():
    if not (1 <= len(LINE) <= 200):
        raise ValueError(f"entry must be 1-200 chars, got {len(LINE)}")
    if not LINE.strip():
        raise ValueError("entry must not be only whitespace")
    # One clean sentence: exactly one sentence-ender, at the very end.
    enders = [c for c in LINE if c in ".!?"]
    if len(enders) != 1 or not LINE.endswith(enders[0]):
        raise ValueError("entry must be a single sentence")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(LINE)


if __name__ == "__main__":
    main()

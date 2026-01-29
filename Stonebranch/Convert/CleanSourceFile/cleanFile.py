import sys
import os
import json
from unittest import result
import pandas as pd
import math
import re
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readFile import loadText


def _safe_load_text(path: str) -> str:
    """Load text reliably. Uses utils.readFile.loadText first; falls back to direct open()."""
    text = loadText(path)

    if isinstance(text, str):
        return text

    if text is None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input file not found: {path}")

        # Try a few common encodings on Windows, then replace as last resort
        for enc in ("utf-8", "utf-8-sig", "cp1252"):
            try:
                with open(path, "r", encoding=enc, errors="strict") as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    # Last resort: coerce to string
    return str(text)


def _strip_c_style_block_comments(text: str) -> str:
    """Remove C-style block comments (/* ... */) while preserving content inside quotes."""
    out = []
    i = 0
    in_block_comment = False
    in_single_quote = False
    in_double_quote = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ''

        if in_block_comment:
            if ch == '*' and nxt == '/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        # Handle quote state transitions (ignore comment markers inside quotes)
        if in_single_quote:
            out.append(ch)
            if ch == "\\" and i + 1 < len(text):
                # keep escaped char
                out.append(text[i + 1])
                i += 2
                continue
            if ch == "'":
                in_single_quote = False
            i += 1
            continue

        if in_double_quote:
            out.append(ch)
            if ch == "\\" and i + 1 < len(text):
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_double_quote = False
            i += 1
            continue

        # Not in comment/quote
        if ch == '/' and nxt == '*':
            in_block_comment = True
            i += 2
            continue

        if ch == "'":
            in_single_quote = True
            out.append(ch)
            i += 1
            continue

        if ch == '"':
            in_double_quote = True
            out.append(ch)
            i += 1
            continue

        out.append(ch)
        i += 1

    return ''.join(out)


def _collapse_blank_line_runs(lines: list[str], threshold: int = 2, keep: int = 1) -> list[str]:
    """If a blank-line run is longer than threshold, keep only `keep` blank lines."""
    if threshold < 0:
        threshold = 0
    if keep < 0:
        keep = 0

    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() != '':
            out.append(lines[i])
            i += 1
            continue

        j = i
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        run_len = j - i

        if run_len > threshold:
            out.extend([''] * keep)
        else:
            out.extend([''] * run_len)

        i = j

    return out



def cleanFile(inputFilePath, outputFilePath, config):
    # Load the source file
    fileContent = _safe_load_text(inputFilePath)

    # Remove Comment blocks (Only in comment, not out of string)
    if config.get("remove_commented_lines", False):
        # NOTE: For C-style block comments, we strip only the commented portion,
        # instead of dropping the whole line.
        fileContent = _strip_c_style_block_comments(fileContent)
        # Remove trailing whitespace created by comment stripping
        fileContent = '\n'.join([line.rstrip() for line in fileContent.splitlines()])
        
    # Remove Empty Lines
    if config.get("remove_empty_lines", False):
        # If there are more than 2 consecutive blank lines, keep only 1.
        # (Example: 3+ blank lines -> 1 blank line; 1-2 blank lines stay as-is)
        lines = fileContent.splitlines()
        threshold = int(config.get("empty_line_threshold", 2))
        keep = int(config.get("empty_lines_to_keep", 1))
        fileContent = '\n'.join(_collapse_blank_line_runs(lines, threshold=threshold, keep=keep))
    
    # Trim Whitespace
    if config.get("trim_whitespace", False):
        fileContent = '\n'.join([line.strip() for line in fileContent.splitlines()])
    
    # Remove Special Characters
    if config.get("remove_special_characters", False):
        fileContent = re.sub(r'[^a-zA-Z0-9\s]', '', fileContent)
        
    # Save the cleaned content to the output file
    with open(outputFilePath, 'w', encoding='utf-8') as outputFile:
        outputFile.write(fileContent)

    return True


if __name__ == "__main__":
    inputFilePath = "C:\\Dev\\STB\\Source\\M2FLAT-TSO4.txt"
    outputFilePath = "C:\\Dev\\AutomateDEV\\Stonebranch\\Convert\\CleanSourceFile\\outputfile.txt"
    config = {
        "remove_empty_lines": True,
        "trim_whitespace": False,
        "remove_special_characters": False,
        "remove_commented_lines": True,
        "comment_pattern": r'/\*.*\*/'
    }

    cleanFile(inputFilePath, outputFilePath, config)
    
    print(f"Cleaned file saved to {outputFilePath}")

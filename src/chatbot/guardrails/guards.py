from typing import Literal
from .patterns import PII_PATTERNS, PROMPT_INJECTION_PATTERNS, SECRET_PATTERNS, DANGEROUS_OUTPUT_PATTERNS
import re

input_patterns = {

    "clean": [
        *PII_PATTERNS,
    ],

    "delete": [
        *PROMPT_INJECTION_PATTERNS,
        *SECRET_PATTERNS,
    ],
}

output_patterns = {

    "clean": [
        *PII_PATTERNS,
    ],

    "delete": [
        *SECRET_PATTERNS,
        *DANGEROUS_OUTPUT_PATTERNS,
    ],
}

def check_text (output_or_input : Literal["input", "output"], text: str) -> Literal["clean", "delete", "pass"]:
    """
    Checks if the text contains any forbidden patterns.

    The validation rules and detected patterns change depending on whether
    the text is an input or an output.

    Args:
        text: The string content to analyze.
        output_or_input: "input" if analyzing incoming user prompts,
            or "output" if analyzing outgoing model responses.

    Returns:
        "pass" if the text is perfectly safe.
        "clean" if PII patterns are found and need [REDACTED] replacement.
        "delete" if dangerous patterns are found and the message must be blocked.
    """
    if output_or_input == "input":
        patterns = input_patterns
    else:
        patterns = output_patterns

    for pattern in patterns["delete"]:
        if re.search(pattern, text):
            return "delete"

    for pattern in patterns["clean"]:
        if re.search(pattern, text):
            return "clean"

    return "pass"

def clean_text (output_or_input: Literal["input", "output"], text: str):

    if output_or_input == "input":
        patterns = input_patterns
    else:
        patterns = output_patterns

    clean_str = text
    for pattern in patterns["clean"]:
        clean_str = re.sub(pattern, "[REDACTED]", clean_str)
    return clean_str

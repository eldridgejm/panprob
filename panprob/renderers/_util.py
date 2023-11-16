import re


def collapse_empty_lines(s):
    """Collapse multiple empty lines into a single empty line."""
    return re.sub(r"\n{2,}", "\n\n", s)

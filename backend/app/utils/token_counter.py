import tiktoken

from app.core.config import get_settings

settings = get_settings()

# Use generic cl100k_base encoding (common for modern models)
encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """
    Returns the number of tokens in a text string.
    """
    if not text:
        return 0
    return len(encoding.encode(text, disallowed_special=()))

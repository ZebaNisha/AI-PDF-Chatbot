import re
import unicodedata


def clean_extracted_text(text: str) -> str:
    """
    Cleans raw text extracted from PDFs.
    - Normalizes unicode characters
    - Removes null bytes
    - Condenses multiple whitespaces and newlines
    - Strips leading/trailing whitespace
    """
    if not text:
        return ""

    # Normalize unicode to NFKC (combines characters like ﬁ into fi)
    text = unicodedata.normalize("NFKC", text)

    # Remove null bytes
    text = text.replace("\x00", "")

    # Replace multiple spaces with a single space
    text = re.sub(r"[^\S\r\n]+", " ", text)

    # Replace 3 or more consecutive newlines with 2 newlines (paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace
    return text.strip()

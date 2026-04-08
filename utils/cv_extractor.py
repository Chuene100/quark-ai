import fitz
import os
from pathlib import Path



def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file and returns it as a clean string.

    Args:
        pdf_path: path to the PDF file

    Returns:
        Extract text as a single string

    Raises:
        FileNotFOundError: if the PDF doesn't extst
        ValueError: if the PDF has no extractable text
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"CV not found: {pdf_path}")
    
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")
    
    doc = fitz.open(str(path))

    if doc.page_count == 0:
        raise ValueError("PDF has no pages.")
    
    pages_text = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text("text") # "text" mode preserves reading order
        pages_text.append(text)

    doc.close()

    full_text = "\n\n".join(pages_text).strip()

    if not full_text:
        raise ValueError(
            "No text could be extracted." \
            "The PDF may be scanned (image-based)" \
            "Try exporting your CV as a text-based PDF from Word or Google Docs"
        )
    return full_text

def get_cv_summary(pdf_path: str, max_chars: int = 8000) -> str:
    """
    Extracts CV text and truncates it to a sage length for API calls.
    Claude has a context window limit -  we stay well within it.

    Args:
        pdf_path: path to the PDF
        max_chars: character limit (default 8000 is safe for all models)

    Returns:
        Truncated CV text

    """
    text = extract_text_from_pdf(pdf_path)

    if len(text) > max_chars:
        print(
            f"CV text truncated from {len(text)} to {max_chars} characters."
        )
        return text[:max_chars]
    return text
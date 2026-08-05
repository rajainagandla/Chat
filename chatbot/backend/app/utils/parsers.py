"""Document parsers for extracting text from various file types."""
from pathlib import Path


def parse_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def parse_docx(path: Path) -> str:
    import docx

    document = docx.Document(str(path))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def parse_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_md(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


PARSERS = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".txt": parse_txt,
    ".md": parse_md,
}


def extract_text(filepath: str) -> str:
    """Extract raw text from a file based on its extension."""
    path = Path(filepath)
    parser = PARSERS.get(path.suffix.lower())
    if parser is None:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    text = parser(path)
    if not text.strip():
        raise ValueError("Extracted text is empty")
    return text

import os


def extract_text(file_path: str) -> str:
    """Extract text from a file.

    Behavior:
    - If the file does not exist, raise FileNotFoundError.
    - For known text extensions (.txt, .md, .csv, .log), read as UTF-8.
    - For other files, attempt to read in binary and decode as UTF-8
      with replacement of undecodable bytes so we always return a string.

    Raises an exception on I/O errors so callers can handle/report them.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text_exts = {'.txt', '.md', '.csv', '.log'}
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        if ext in text_exts:
            # Preferred path for plain text files
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        if ext == '.pdf':
            # Try PyPDF2 first, then pdfminer as fallback
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    pages = []
                    for p in reader.pages:
                        try:
                            pages.append(p.extract_text() or '')
                        except Exception:
                            pages.append('')
                    return '\n'.join(pages)
            except Exception:
                try:
                    from pdfminer.high_level import extract_text as pdf_extract_text

                    return pdf_extract_text(file_path)
                except Exception:
                    raise IOError(
                        "PDF extraction requires 'PyPDF2' or 'pdfminer.six'.\n"
                        "Install with: pip install PyPDF2 pdfminer.six"
                    )
        else:
            # Fallback: try text read first, then binary decode with replacement
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    return data.decode('utf-8', errors='replace')
    except Exception as e:
        # Re-raise as IOError to be explicit about read failures
        raise IOError(f"Error reading file '{file_path}': {e}")
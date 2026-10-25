"""
services/pdf_parser.py - Robust PDF parsing and validation using PyMuPDF (fitz).
Detects scanned/image-only PDFs, password-protected files, and normalizes extracted text.
"""
import re
import pymupdf as fitz  # PyMuPDF modern import


class PDFParsingError(Exception):
    """Custom exception raised for user-actionable PDF processing failures."""
    pass


class PDFParser:
    """Handles PDF validation, extraction, and diagnostic checks."""
    
    MIN_WORD_COUNT_THRESHOLD = 30  # Below this threshold for multi-line PDFs, likely scanned/empty

    @classmethod
    def extract_text_from_bytes(cls, pdf_bytes: bytes, filename: str = "resume.pdf") -> dict:
        """
        Parses raw PDF bytes using PyMuPDF.
        
        Returns:
            dict containing:
                - text: normalized clean full text
                - raw_text: original extracted text
                - page_count: int
                - word_count: int
                - char_count: int
                - is_scanned: bool
                - pages: list of str (page-by-page text)
        """
        if not pdf_bytes:
            raise PDFParsingError("Uploaded file is empty (0 bytes). Please upload a valid PDF document.")
        
        # Verify PDF header magic bytes (%PDF)
        if not pdf_bytes.startswith(b"%PDF"):
            raise PDFParsingError("The uploaded file does not have a valid PDF header format. Please verify it is an actual PDF.")

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise PDFParsingError(f"Unable to read PDF file format: {str(e)}")

        try:
            # Check for encryption
            if doc.is_encrypted:
                raise PDFParsingError("The uploaded PDF is password-protected or encrypted. Please remove the password protection and re-upload.")

            page_count = len(doc)
            if page_count == 0:
                raise PDFParsingError("The uploaded PDF contains no pages.")

            pages_text = []
            has_images = False

            for page_index in range(page_count):
                page = doc[page_index]
                # Check for images on page to enrich error context if no text is found
                if len(page.get_images()) > 0:
                    has_images = True
                
                # Extract text using standard layout preservation
                page_text = page.get_text("text") or ""
                pages_text.append(page_text)

            full_raw_text = "\n\n".join(pages_text).strip()
            normalized_text = cls.normalize_text(full_raw_text)
            
            words = [w for w in normalized_text.split() if w]
            word_count = len(words)
            char_count = len(normalized_text)

            # Check if document appears to be an image-only / scanned PDF
            if word_count < cls.MIN_WORD_COUNT_THRESHOLD:
                if has_images:
                    raise PDFParsingError(
                        "This PDF appears to be a scanned or image-based document without selectable text. "
                        "Parichay requires a digital, text-based PDF (exported from Google Docs, Word, Canva, or LaTeX) "
                        "to accurately analyze your qualifications."
                    )
                else:
                    raise PDFParsingError(
                        "The uploaded PDF contains very little or no readable text. "
                        "Please upload a comprehensive resume containing your education, experience, and skills."
                    )

            return {
                "text": normalized_text,
                "raw_text": full_raw_text,
                "page_count": page_count,
                "word_count": word_count,
                "char_count": char_count,
                "is_scanned": False,
                "pages": pages_text
            }

        finally:
            doc.close()

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Cleans and standardizes extracted text:
        - Normalizes unicode quotation marks, hyphens, and whitespace
        - Reconnects hyphenated words split across lines (e.g. 'engi-\nneer' -> 'engineer')
        - Standardizes bullet characters to standard bullet points
        - Removes excessive repeating blank lines
        """
        if not text:
            return ""

        # Normalize non-breaking and unusual spaces
        text = text.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")
        
        # Normalize typographic quotes and dashes
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = text.replace("—", " - ").replace("–", " - ")

        # Standardize common resume bullets (•, ⁃, ◦, ▪, ▸, etc.) to '-'
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25B8\u27A2]', '\n- ', text)

        # Fix hyphenated words broken across linebreaks
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        # Normalize horizontal whitespace
        text = re.sub(r'[ \t]+', ' ', text)

        # Clean excessive consecutive newlines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

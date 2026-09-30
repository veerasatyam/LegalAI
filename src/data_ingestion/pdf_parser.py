from PyPDF2 import PdfReader
import re
from pathlib import Path

class IPCPDFParser:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.reader = PdfReader(pdf_path)

    def extract_sections(self):
        """
        Extract text while preserving section structure.
        Returns: List of pages with text
        """
        pages = []
        for page_num in range(len(self.reader.pages)):
            page = self.reader.pages[page_num]
            text = page.extract_text()

            # Clean the text
            text = self._clean_text(text)

            pages.append({
                'page_number': page_num + 1,
                'text': text
            })

        return pages

    def _clean_text(self, text):
        """Remove extra whitespace, fix common PDF issues"""
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove extra spaces
        text = re.sub(r' +', ' ', text)
        # Fix hyphenated line breaks
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        return text.strip()

    def save_raw_text(self, output_dir):
        """Save each page as separate text file for inspection"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        pages = self.extract_sections()
        for page in pages:
            with open(output_dir / f"page_{page['page_number']:03d}.txt", 'w', encoding='utf-8') as f:
                f.write(page['text'])

        return pages
import fitz
import re
import json
from pathlib2 import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file with page numbers."""
    try:
        doc = fitz.open(pdf_path)
        text_by_page = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            text_by_page.append({"page": page_num, "text": text})
        doc.close()
        return text_by_page
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return []

def clean_text(text):
    """Clean text by removing extra spaces, newlines, and special characters."""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    return text

def extract_title(text_by_page):
    """Extract the document title from the first page."""
    if not text_by_page:
        return ""
    first_page_text = text_by_page[0]["text"]
    lines = first_page_text.split('\n')[:3]  # Check first three lines for title
    for line in lines:
        cleaned_line = clean_text(line)
        if cleaned_line and len(cleaned_line.split()) <= 10:  # Assume title is concise
            return cleaned_line
    return ""

def extract_outline(text_by_page):
    """Extract outline with H1-H4 levels based on numbering and formatting."""
    outline = []
    heading_pattern = re.compile(
        r'^((\d+\.)+\s+.*?|Appendix [A-Z]:.*?|[A-Z][a-zA-Z\s\-:]+?)(?=\n|$)',
        re.MULTILINE
    )
    for page in text_by_page:
        page_num = page["page"]
        text = page["text"]
        lines = text.split('\n')
        for line in lines:
            cleaned_line = clean_text(line)
            if not cleaned_line or "TOPJUMP" in cleaned_line.upper():
                continue  # Skip noisy text
            match = heading_pattern.match(cleaned_line)
            if match:
                heading_text = match.group(1).strip()
                # Determine heading level based on numbering
                if re.match(r'^\d+\.\s', heading_text):
                    level = "H1"
                elif re.match(r'^\d+\.\d+\s', heading_text):
                    level = "H2"
                elif re.match(r'^\d+\.\d+\.\d+\s', heading_text):
                    level = "H3"
                elif re.match(r'^\d+\.\d+\.\d+\.\d+\s', heading_text):
                    level = "H4"
                elif heading_text.startswith("Appendix"):
                    level = "H2"
                elif heading_text.isupper() or ":" in heading_text:
                    level = "H1"  # Fallback for descriptive or capitalized headings
                else:
                    continue
                outline.append({
                    "level": level,
                    "text": heading_text,
                    "page": page_num
                })
    return outline

def save_to_json(data, output_path):
    """Save data to a JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON to {output_path}: {e}")
        return False
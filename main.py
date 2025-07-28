import argparse
from pathlib2 import Path
import utils

def process_pdf(pdf_path, output_dir, verbose=False):
    """Process a single PDF and save the outline to a JSON file."""
    if verbose:
        print(f"Processing {pdf_path}")
    text_by_page = utils.extract_text_from_pdf(pdf_path)
    if not text_by_page:
        print(f"No text extracted from {pdf_path}")
        return False
    title = utils.extract_title(text_by_page)
    outline = utils.extract_outline(text_by_page)
    output_data = {
        "title": title,
        "outline": outline
    }
    output_filename = output_dir / f"{pdf_path.stem}.json"
    if utils.save_to_json(output_data, output_filename):
        if verbose:
            print(f"Saved output to {output_filename}")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Extract PDF outlines to JSON")
    parser.add_argument("--input", type=str, required=True, help="Input directory containing PDFs")
    parser.add_argument("--output", type=str, required=True, help="Output directory for JSON files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        return

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    for pdf_file in pdf_files:
        process_pdf(pdf_file, output_dir, args.verbose)

if __name__ == "__main__":
    main()
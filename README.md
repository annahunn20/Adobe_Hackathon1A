# PDF Outline Extractor

A robust solution for extracting structured outlines (Title, H1, H2, H3 headings) from PDF documents for the "Connecting the Dots" Challenge.

## Approach

### Core Strategy

Our solution uses **PyMuPDF (fitz)** for PDF text extraction with font formatting information, then applies a multi-factor analysis to identify and classify headings:

1. **Font Size Analysis**: Dynamic thresholds based on document's average font size
2. **Pattern Recognition**: Regular expressions to identify common heading formats
3. **Formatting Detection**: Bold text and font properties
4. **Contextual Analysis**: Position, length, and structure of text elements

### Key Features

- **Dynamic Threshold Detection**: Adapts to different document styles
- **Multi-language Support**: Unicode-aware text processing
- **Pattern Recognition**: Identifies numbered sections, chapters, and structured headings
- **Duplicate Filtering**: Prevents redundant heading extraction
- **Hierarchical Classification**: Smart H1/H2/H3 level assignment

### Architecture

```
main.py                 # Main extraction logic and CLI interface
utils.py               # Helper functions for text processing
requirements.txt       # Python dependencies
Dockerfile            # Container configuration
README.md             # Documentation
```

## Models and Libraries Used

- **PyMuPDF (1.23.8)**: PDF parsing and text extraction with formatting
- **Python 3.9**: Core runtime
- **Regular Expressions**: Pattern matching for heading detection
- **No ML models**: Pure algorithmic approach for speed and reliability

## Algorithm Details

### Title Extraction

1. Identify largest font size text on first page
2. Filter out very short text and numbers
3. Clean formatting (remove leading numbers/bullets)

### Heading Detection

1. **Size-based scoring**: Text larger than average gets higher scores
2. **Pattern matching**: Numbered sections, chapters, all-caps text
3. **Format analysis**: Bold text, standalone lines
4. **Threshold filtering**: Combined score must exceed minimum threshold

### Level Classification

1. **Pattern priority**: `1.` → H1, `1.1` → H2, `1.1.1` → H3
2. **Size ratios**: Larger text gets higher heading levels
3. **Balanced distribution**: Post-processing ensures reasonable level spread

## Performance Optimizations

- **Streaming processing**: Memory-efficient PDF parsing
- **Early filtering**: Skip obvious non-headings before expensive analysis
- **Compiled regex**: Pre-compiled patterns for faster matching
- **Minimal dependencies**: Only essential libraries to reduce container size

## Build and Run

### Using Docker (Recommended)

```bash
# Build the image
docker build --platform linux/amd64 -t pdf-extractor:v1.0 .

# Run with mounted volumes
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-extractor:v1.0
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python main.py --input ./input --output ./output
```

## Input/Output Format

### Input

- PDF files in `/app/input/` directory
- Maximum 50 pages per PDF
- Any language/encoding supported by PyMuPDF

### Output

- JSON files in `/app/output/` directory
- One `.json` file per `.pdf` input file

### JSON Schema

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Background",
      "page": 2
    }
  ]
}
```

## Constraints Compliance

- ✅ **Execution time**: < 10 seconds for 50-page PDFs
- ✅ **Model size**: No models used, only lightweight libraries
- ✅ **Network**: Fully offline, no internet calls
- ✅ **Runtime**: CPU-only on AMD64 architecture
- ✅ **Memory**: Optimized for 16GB RAM systems

## Testing

The solution has been tested on:

- Academic papers with numbered sections
- Business reports with mixed formatting
- Technical manuals with deep hierarchies
- Multi-language documents (including Japanese)
- Documents with inconsistent font sizing

## Edge Cases Handled

- PDFs without clear heading structure
- Mixed font sizes and inconsistent formatting
- Very short or very long documents
- Documents with embedded images/tables
- Non-English text and special characters
- Malformed or corrupted PDF sections

## Future Enhancements

For Round 1B, this foundation can be extended with:

- Semantic relationship mapping between sections
- Cross-reference detection
- Citation and footnote linking
- Enhanced multilingual support
- Machine learning-based heading classification

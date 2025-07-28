#!/usr/bin/env python3
"""
Test script for PDF Outline Extractor
"""

import json
import tempfile
import shutil
from pathlib import Path
from main import PDFOutlineExtractor

def create_test_pdf():
    """Create a simple test PDF for validation"""
    try:
        import fitz
        
        # Create a simple PDF with headings
        doc = fitz.open()
        page = doc.new_page()
        
        # Add title
        page.insert_text((72, 100), "Test Document Title", fontsize=18, color=(0, 0, 0))
        
        # Add headings
        page.insert_text((72, 150), "1. Introduction", fontsize=14, color=(0, 0, 0))
        page.insert_text((72, 200), "1.1 Background", fontsize=12, color=(0, 0, 0))
        page.insert_text((72, 250), "1.2 Objectives", fontsize=12, color=(0, 0, 0))
        page.insert_text((72, 300), "2. Methodology", fontsize=14, color=(0, 0, 0))
        
        # Add some body text
        page.insert_text((72, 350), "This is regular body text that should not be detected as a heading.", fontsize=10)
        
        return doc
    except ImportError:
        print("PyMuPDF not available for test PDF creation")
        return None

def test_extractor():
    """Test the PDF extractor with various scenarios"""
    extractor = PDFOutlineExtractor()
    
    # Test 1: Create and test with synthetic PDF
    print("Test 1: Synthetic PDF")
    test_doc = create_test_pdf()
    if test_doc:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            test_doc.save(tmp_file.name)
            test_doc.close()
            
            result = extractor.extract_outline(tmp_file.name)
            print(f"Title: {result['title']}")
            print(f"Outline entries: {len(result['outline'])}")
            for item in result['outline']:
                print(f"  {item['level']}: {item['text']} (page {item['page']})")
            
            Path(tmp_file.name).unlink()  # Clean up
    
    # Test 2: Test with empty input
    print("\nTest 2: Empty input handling")
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()
        
        extractor.process_directory(str(input_dir), str(output_dir))
        
        output_files = list(output_dir.glob("*.json")) if output_dir.exists() else []
        print(f"Output files created: {len(output_files)}")

def validate_json_format(json_file: str) -> bool:
    """Validate that JSON output matches expected format"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required fields
        if 'title' not in data or 'outline' not in data:
            print(f"Missing required fields in {json_file}")
            return False
        
        # Validate outline format
        for item in data['outline']:
            required_fields = ['level', 'text', 'page']
            if not all(field in item for field in required_fields):
                print(f"Missing outline fields in {json_file}")
                return False
            
            if item['level'] not in ['H1', 'H2', 'H3']:
                print(f"Invalid heading level in {json_file}: {item['level']}")
                return False
            
            if not isinstance(item['page'], int) or item['page'] < 1:
                print(f"Invalid page number in {json_file}: {item['page']}")
                return False
        
        print(f"✓ {json_file} format is valid")
        return True
        
    except Exception as e:
        print(f"✗ Error validating {json_file}: {str(e)}")
        return False

def performance_test():
    """Basic performance testing"""
    import time
    
    print("\nPerformance Test:")
    print("Creating test scenario...")
    
    # This would ideally test with actual PDFs of various sizes
    # For now, we'll test the utility functions
    from utils import is_likely_heading, determine_heading_level
    
    test_cases = [
        ("1. Introduction", 14, True, 10),
        ("Regular paragraph text", 10, False, 10),
        ("CHAPTER ONE", 16, True, 10),
        ("1.1 Background", 12, True, 10),
        ("Figure 1: Sample image", 10, False, 10),
    ]
    
    start_time = time.time()
    
    for text, size, is_bold, avg_size in test_cases:
        is_heading = is_likely_heading(text, size, is_bold, avg_size)
        if is_heading:
            level = determine_heading_level(text, size, avg_size)
            print(f"  '{text}' -> {level}")
        else:
            print(f"  '{text}' -> Not a heading")
    
    end_time = time.time()
    print(f"Processing time: {(end_time - start_time) * 1000:.2f}ms")

if __name__ == "__main__":
    print("PDF Outline Extractor Test Suite")
    print("=" * 40)
    
    test_extractor()
    performance_test()
    
    print("\nTest completed!")
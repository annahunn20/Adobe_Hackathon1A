#!/bin/bash

# Build and test script for PDF Outline Extractor
# Usage: ./build.sh [test|build|run]

set -e  # Exit on any error

DOCKER_IMAGE="pdf-extractor"
DOCKER_TAG="v1.0"
FULL_IMAGE_NAME="${DOCKER_IMAGE}:${DOCKER_TAG}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build Docker image
build_docker() {
    log_info "Building Docker image: ${FULL_IMAGE_NAME}"
    
    if docker build --platform linux/amd64 -t "${FULL_IMAGE_NAME}" .; then
        log_info "Docker image built successfully"
        
        # Show image size
        IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}" --format "table {{.Size}}" | tail -n1)
        log_info "Image size: ${IMAGE_SIZE}"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    log_info "Running local tests..."
    
    # Check if Python dependencies are available locally
    if python3 -c "import fitz" 2>/dev/null; then
        log_info "Running Python tests locally"
        python3 test.py
    else
        log_warn "PyMuPDF not available locally, skipping local tests"
    fi
}

# Function to test Docker container
test_docker() {
    log_info "Testing Docker container..."
    
    # Create test directories
    mkdir -p test_input test_output
    
    # Create a simple test PDF if PyMuPDF is available
    if python3 -c "import fitz" 2>/dev/null; then
        python3 -c "
import fitz
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 100), 'Test Document', fontsize=18)
page.insert_text((72, 150), '1. Introduction', fontsize=14)
page.insert_text((72, 200), '1.1 Background', fontsize=12)
page.insert_text((72, 250), '2. Methods', fontsize=14)
doc.save('test_input/test.pdf')
doc.close()
print('Test PDF created')
"
    else
        log_warn "Cannot create test PDF, PyMuPDF not available"
        echo '{"title": "Test", "outline": []}' > test_input/dummy.txt
    fi
    
    # Run Docker container
    if docker run --rm \
        -v "$(pwd)/test_input:/app/input" \
        -v "$(pwd)/test_output:/app/output" \
        --network none \
        "${FULL_IMAGE_NAME}"; then
        
        log_info "Docker container ran successfully"
        
        # Check output
        if [ -d "test_output" ] && [ "$(ls -A test_output)" ]; then
            log_info "Output files generated:"
            ls -la test_output/
            
            # Validate JSON if files were created
            for json_file in test_output/*.json; do
                if [ -f "$json_file" ]; then
                    if python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
                        log_info "✓ $json_file is valid JSON"
                    else
                        log_error "✗ $json_file is invalid JSON"
                    fi
                fi
            done
        else
            log_warn "No output files generated"
        fi
    else
        log_error "Docker container failed to run"
        exit 1
    fi
    
    # Cleanup
    rm -rf test_input test_output
}

# Function to run the container with custom input/output
run_docker() {
    if [ ! -d "input" ]; then
        log_error "Input directory 'input' not found"
        log_info "Please create an 'input' directory and place PDF files in it"
        exit 1
    fi
    
    mkdir -p output
    
    log_info "Running Docker container with input/output directories..."
    docker run --rm \
        -v "$(pwd)/input:/app/input" \
        -v "$(pwd)/output:/app/output" \
        --network none \
        "${FULL_IMAGE_NAME}"
    
    log_info "Processing complete. Check the 'output' directory for results."
}

# Function to show help
show_help() {
    echo "PDF Outline Extractor Build Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build    Build the Docker image"
    echo "  test     Run local tests (requires PyMuPDF)"
    echo "  docker   Test the Docker container with sample data"
    echo "  run      Run the container with input/output directories"
    echo "  all      Build, test, and run Docker tests"
    echo "  help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build        # Build Docker image"
    echo "  $0 all          # Full build and test cycle"
    echo "  $0 run          # Process PDFs in ./input directory"
}

# Main script logic
case "${1:-help}" in
    "build")
        build_docker
        ;;
    "test")
        run_tests
        ;;
    "docker")
        build_docker
        test_docker
        ;;
    "run")
        build_docker
        run_docker
        ;;
    "all")
        log_info "Running full build and test cycle"
        build_docker
        run_tests
        test_docker
        log_info "All tests completed successfully!"
        ;;
    "help"|*)
        show_help
        ;;
esac
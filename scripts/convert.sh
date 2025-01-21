#!/bin/bash

set -eo pipefail

# Default values
PYTHON_SCRIPT_NAME="convert.py"
REQUIREMENTS_FILE="requirements.txt"

# Print usage information
usage() {
    echo "Usage: $0 -f <openapi-source> -o <output-file> [-t <bearer-token>] [-h]"
    echo
    echo "Options:"
    echo "  -f    Path or URL to OpenAPI specification (required)"
    echo "  -o    Output file path for KrakenD endpoints (required)"
    echo "  -t    Bearer token for API authentication"
    echo "  -h    Show this help message"
    exit 1
}

# Function to setup Python virtual environment
setup_venv() {
    echo "Setting up Python virtual environment..."
    python3 -m venv .venv 2>/dev/null || {
        echo "Warning: Could not create virtual environment. Continuing with system Python..."
        return 1
    }
    
    source .venv/bin/activate

    # Create requirements.txt if it doesn't exist
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        echo "Creating $REQUIREMENTS_FILE..."
        cat > "$REQUIREMENTS_FILE" << EOF
pyyaml
requests
EOF
    fi

    echo "Installing Python dependencies..."
    python3 -m pip install --quiet --upgrade pip
    python3 -m pip install --quiet -r "$REQUIREMENTS_FILE" || {
        echo "Installing dependencies in user space..."
        python3 -m pip install --quiet --user -r "$REQUIREMENTS_FILE"
    }
}

# Function to cleanup
cleanup() {
    if [ -d ".venv" ]; then
        echo "Cleaning up virtual environment..."
        deactivate 2>/dev/null || true
        rm -rf .venv
    fi
}

# Parse command line arguments
openapi_source=""
output_file=""
bearer_token=""

while getopts "f:o:t:h" opt; do
    case $opt in
        f) openapi_source="$OPTARG" ;;
        o) output_file="$OPTARG" ;;
        t) bearer_token="$OPTARG" ;;
        h) usage ;;
        ?) usage ;;
    esac
done

# Check required arguments
if [ -z "$openapi_source" ] || [ -z "$output_file" ]; then
    echo "Error: OpenAPI source and output file are required"
    usage
fi

# Check if convert.py exists
if [ ! -f "$PYTHON_SCRIPT_NAME" ]; then
    echo "Error: $PYTHON_SCRIPT_NAME not found in current directory"
    exit 1
fi

# Check Python installation
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Setup trap for cleanup
trap cleanup EXIT

# Setup virtual environment
setup_venv

# Main execution
echo "Starting OpenAPI to KrakenD conversion..."
echo "Source: $openapi_source"
echo "Output: $output_file"

# Build command with optional token
cmd="python3 $PYTHON_SCRIPT_NAME -f \"$openapi_source\" -o \"$output_file\""
if [ -n "$bearer_token" ]; then
    cmd="$cmd -t \"$bearer_token\""
fi

# Run the converter
eval "$cmd"

# Check if conversion was successful
if [ $? -eq 0 ]; then
    echo "Conversion completed successfully"
    echo "KrakenD endpoints file is available at: $output_file"
else
    echo "Error: Conversion failed"
    exit 1
fi
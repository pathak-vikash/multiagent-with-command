#!/bin/bash

# LangGraph Multi-Agent Supervisor System - Startup Script
# This script provides options to run either the Streamlit web interface
# or the console interface.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        echo "Creating .env file from template..."
        if [ -f "env_template.txt" ]; then
            cp env_template.txt .env
            print_status ".env file created from template"
            print_warning "Please edit .env file and add your OpenAI API key"
            echo "   OPENAI_API_KEY=your_actual_api_key_here"
            echo ""
        else
            print_error "env_template.txt not found!"
            exit 1
        fi
    fi
}

# Function to check if required packages are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        print_warning "uv package manager not found. Installing dependencies with pip..."
        pip3 install -r requirements.txt
    else
        print_status "uv found, checking if dependencies are installed..."
        # Try to import key modules
        if ! python3 -c "import langgraph, streamlit, openai" 2>/dev/null; then
            print_warning "Some dependencies missing. Installing with uv..."
            uv add langgraph langchain-openai langchain-core pydantic python-dotenv openai streamlit
        fi
    fi
    
    print_status "Dependencies check completed"
}

# Function to run Streamlit app
run_streamlit() {
    print_header "Starting Streamlit Web Interface"
    print_status "Opening web interface at http://localhost:8501"
    print_status "Press Ctrl+C to stop the server"
    echo ""
    
    # Check if streamlit is available
    if ! python3 -c "import streamlit" 2>/dev/null; then
        print_error "Streamlit not installed. Installing..."
        if command -v uv &> /dev/null; then
            uv add streamlit
        else
            pip3 install streamlit
        fi
    fi
    
    # Run Streamlit
    python3 -m streamlit run streamlit_app.py --server.port 8501 --server.address localhost
}

# Function to run console interface
run_console() {
    print_header "Starting Console Interface"
    print_status "Running in interactive mode"
    print_status "Type 'help' for example questions"
    print_status "Type 'quit', 'exit', or 'bye' to end the session"
    echo ""
    
    # Run the main script
    python3 main.py --interactive
}

# Function to run demo mode
run_demo() {
    print_header "Running Demo Mode"
    print_status "This will run predefined examples to demonstrate the system"
    echo ""
    
    # Run the main script in demo mode
    python3 main.py --demo
}

# Function to run tests
run_tests() {
    print_header "Running Tests"
    print_status "Testing graph composition and module imports..."
    echo ""
    
    # Run the test script
    python3 test_graph.py
}

# Function to show help
show_help() {
    print_header "LangGraph Multi-Agent Supervisor System"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  streamlit, web, s    Start Streamlit web interface (default)"
    echo "  console, cli, c      Start console interface"
    echo "  demo, d              Run demo mode with predefined examples"
    echo "  test, t              Run tests to verify installation"
    echo "  help, h              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Start Streamlit (default)"
    echo "  $0 console           # Start console interface"
    echo "  $0 demo              # Run demo mode"
    echo "  $0 test              # Run tests"
    echo ""
    echo "Features:"
    echo "  🤖 Multi-agent system with intelligent routing"
    echo "  📅 Appointment booking and scheduling"
    echo "  🎫 Customer support and warranty claims"
    echo "  💰 Price quotes and estimates"
    echo "  📋 Business information and recommendations"
    echo ""
}

# Main script logic
main() {
    # Check if we're in the right directory
    if [ ! -f "main.py" ] || [ ! -f "streamlit_app.py" ]; then
        print_error "Please run this script from the project root directory"
        print_error "Make sure main.py and streamlit_app.py are present"
        exit 1
    fi
    
    # Check environment file
    check_env_file
    
    # Check dependencies
    check_dependencies
    
    # Parse command line arguments
    case "${1:-streamlit}" in
        "streamlit"|"web"|"s"|"")
            run_streamlit
            ;;
        "console"|"cli"|"c")
            run_console
            ;;
        "demo"|"d")
            run_demo
            ;;
        "test"|"t")
            run_tests
            ;;
        "help"|"h"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

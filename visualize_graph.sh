#!/bin/bash

# Graph Visualization Shell Script
# This script provides an easy way to visualize LangGraph graphs

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/.venv"

# Available graphs
declare -A GRAPHS=(
    ["appointment"]="Appointment Sub-Graph"
    ["main"]="Main Orchestration Graph"
    ["general"]="General Agent Sub-Graph"
    ["support"]="Support Agent Sub-Graph"
    ["estimate"]="Estimate Agent Sub-Graph"
    ["advisor"]="Advisor Agent Sub-Graph"
)

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if virtual environment exists
check_venv() {
    if [[ ! -d "$VENV_PATH" ]]; then
        print_error "Virtual environment not found at $VENV_PATH"
        print_info "Please run: python -m venv .venv"
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [[ -f "$VENV_PATH/bin/activate" ]]; then
        source "$VENV_PATH/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Could not activate virtual environment"
        exit 1
    fi
}

# Function to list available graphs
list_graphs() {
    print_header "Available Graphs"
    for key in "${!GRAPHS[@]}"; do
        echo -e "${CYAN}$key${NC}: ${GRAPHS[$key]}"
    done
    echo
}

# Function to show usage
show_usage() {
    cat << EOF
Graph Visualization Tool

Usage: $0 [OPTIONS] [GRAPH_NAME]

OPTIONS:
    -h, --help              Show this help message
    -l, --list              List all available graphs
    -a, --all               Visualize all graphs
    -m, --mermaid           Include Mermaid diagram (default)
    --no-mermaid            Disable Mermaid diagram
    -c, --config            Include JSON configuration
    -s, --save              Save visualization files to disk
    -i, --interactive       Interactive mode

GRAPH_NAME:
    Name of the graph to visualize (appointment, main, general, support, estimate, advisor)

EXAMPLES:
    $0 --list                    # List all graphs
    $0 appointment               # Visualize appointment graph
    $0 main --config             # Visualize main graph with config
    $0 --all --save              # Visualize all graphs and save files
    $0 --interactive             # Interactive mode

INTERACTIVE MODE:
    When using --interactive, you can:
    - Select graphs from a menu
    - Choose output options
    - Preview before saving

EOF
}

# Function to run visualization
run_visualization() {
    local graph_name="$1"
    local include_mermaid="$2"
    local include_config="$3"
    local save_files="$4"
    
    print_header "Visualizing $graph_name Graph"
    
    # Build command
    local cmd="python visualize_graphs.py $graph_name"
    
    if [[ "$include_mermaid" == "false" ]]; then
        cmd="$cmd --no-mermaid"
    fi
    
    if [[ "$include_config" == "true" ]]; then
        cmd="$cmd --config"
    fi
    
    if [[ "$save_files" == "true" ]]; then
        cmd="$cmd --save"
    fi
    
    print_info "Running: $cmd"
    echo
    
    # Execute command
    if eval "$cmd"; then
        print_success "Visualization completed for $graph_name"
    else
        print_error "Visualization failed for $graph_name"
        return 1
    fi
}

# Function to run all visualizations
run_all_visualizations() {
    local include_mermaid="$1"
    local include_config="$2"
    local save_files="$3"
    
    print_header "Visualizing All Graphs"
    
    # Build command
    local cmd="python visualize_graphs.py all"
    
    if [[ "$include_mermaid" == "false" ]]; then
        cmd="$cmd --no-mermaid"
    fi
    
    if [[ "$include_config" == "true" ]]; then
        cmd="$cmd --config"
    fi
    
    if [[ "$save_files" == "true" ]]; then
        cmd="$cmd --save"
    fi
    
    print_info "Running: $cmd"
    echo
    
    # Execute command
    if eval "$cmd"; then
        print_success "All visualizations completed"
    else
        print_error "Some visualizations failed"
        return 1
    fi
}

# Function for interactive mode
interactive_mode() {
    print_header "Interactive Graph Visualization"
    
    # Select graph
    echo "Select a graph to visualize:"
    echo "0) All graphs"
    local i=1
    for key in "${!GRAPHS[@]}"; do
        echo "$i) $key - ${GRAPHS[$key]}"
        ((i++))
    done
    echo
    
    read -p "Enter your choice (0-$((i-1))): " choice
    
    # Validate choice
    if [[ ! "$choice" =~ ^[0-9]+$ ]] || [[ "$choice" -lt 0 ]] || [[ "$choice" -gt $((i-1)) ]]; then
        print_error "Invalid choice"
        exit 1
    fi
    
    # Get graph name
    local graph_name=""
    if [[ "$choice" -eq 0 ]]; then
        graph_name="all"
    else
        local keys=("${!GRAPHS[@]}")
        graph_name="${keys[$((choice-1))]}"
    fi
    
    echo
    
    # Select options
    echo "Select visualization options:"
    read -p "Include Mermaid diagram? (y/n, default: y): " mermaid_choice
    read -p "Include JSON configuration? (y/n, default: n): " config_choice
    read -p "Save files to disk? (y/n, default: n): " save_choice
    
    # Set defaults
    mermaid_choice=${mermaid_choice:-y}
    config_choice=${config_choice:-n}
    save_choice=${save_choice:-n}
    
    # Convert to boolean
    local include_mermaid="true"
    local include_config="false"
    local save_files="false"
    
    if [[ "$mermaid_choice" =~ ^[Nn]$ ]]; then
        include_mermaid="false"
    fi
    
    if [[ "$config_choice" =~ ^[Yy]$ ]]; then
        include_config="true"
    fi
    
    if [[ "$save_choice" =~ ^[Yy]$ ]]; then
        save_files="true"
    fi
    
    echo
    
    # Run visualization
    if [[ "$graph_name" == "all" ]]; then
        run_all_visualizations "$include_mermaid" "$include_config" "$save_files"
    else
        run_visualization "$graph_name" "$include_mermaid" "$include_config" "$save_files"
    fi
}

# Function to validate graph name
validate_graph_name() {
    local graph_name="$1"
    if [[ -z "${GRAPHS[$graph_name]}" ]]; then
        print_error "Invalid graph name: $graph_name"
        print_info "Use --list to see available graphs"
        exit 1
    fi
}

# Main function
main() {
    # Check if we're in the right directory
    if [[ ! -f "visualize_graphs.py" ]]; then
        print_error "visualize_graphs.py not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Check and activate virtual environment
    check_venv
    activate_venv
    
    # Parse command line arguments
    local graph_name=""
    local list_only=false
    local all_graphs=false
    local interactive=false
    local include_mermaid=true
    local include_config=false
    local save_files=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -l|--list)
                list_only=true
                shift
                ;;
            -a|--all)
                all_graphs=true
                shift
                ;;
            -i|--interactive)
                interactive=true
                shift
                ;;
            -m|--mermaid)
                include_mermaid=true
                shift
                ;;
            --no-mermaid)
                include_mermaid=false
                shift
                ;;
            -c|--config)
                include_config=true
                shift
                ;;
            -s|--save)
                save_files=true
                shift
                ;;
            -*)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [[ -z "$graph_name" ]]; then
                    graph_name="$1"
                else
                    print_error "Multiple graph names specified"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Handle different modes
    if [[ "$list_only" == "true" ]]; then
        list_graphs
        exit 0
    fi
    
    if [[ "$interactive" == "true" ]]; then
        interactive_mode
        exit 0
    fi
    
    if [[ "$all_graphs" == "true" ]]; then
        run_all_visualizations "$include_mermaid" "$include_config" "$save_files"
        exit 0
    fi
    
    if [[ -z "$graph_name" ]]; then
        print_error "No graph name specified"
        print_info "Use --help for usage information"
        exit 1
    fi
    
    # Validate graph name
    validate_graph_name "$graph_name"
    
    # Run visualization
    run_visualization "$graph_name" "$include_mermaid" "$include_config" "$save_files"
}

# Run main function with all arguments
main "$@"

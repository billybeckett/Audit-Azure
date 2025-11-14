#!/usr/bin/env bash

###############################################################################
# Azure Infrastructure Audit Script
#
# This script orchestrates the complete Azure infrastructure discovery and
# documentation generation process.
#
# Usage:
#   ./audit-azure.sh [--login] [--help]
#
# Options:
#   --login    Perform Azure CLI login before running audit
#   --help     Display this help message
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/scripts/azure_discovery.py"

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Azure Infrastructure Audit Tool${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

show_help() {
    cat << EOF
Azure Infrastructure Audit Tool

This tool discovers all resources in your Azure account and generates
comprehensive documentation in markdown format.

USAGE:
    ./audit-azure.sh [OPTIONS]

OPTIONS:
    --login         Perform Azure CLI login before running audit
    -v, --verbose   Enable verbose mode (shows all Azure CLI commands)
    --help          Display this help message

REQUIREMENTS:
    - Azure CLI installed and configured
    - Python 3.7 or higher
    - Valid Azure subscription access

EXAMPLES:
    # Run audit with current authentication
    ./audit-azure.sh

    # Login and then run audit
    ./audit-azure.sh --login

    # Run audit with verbose output
    ./audit-azure.sh --verbose

    # Login and run with verbose mode
    ./audit-azure.sh --login --verbose

OUTPUT:
    Documentation will be generated in the 'docs/' directory:
    - docs/README.md              - Main index with overview
    - docs/resources/networking.md - Networking resources
    - docs/resources/compute.md   - Compute resources
    - docs/resources/storage.md   - Storage resources
    - docs/resources/databases.md - Database resources
    - docs/resources/dns.md       - DNS resources
    - docs/resources/security.md  - Security resources

For more information, visit: https://docs.microsoft.com/cli/azure/

EOF
}

check_azure_cli() {
    print_info "Checking Azure CLI installation..."
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed"
        echo ""
        echo "Please install Azure CLI:"
        echo "  macOS:   brew install azure-cli"
        echo "  Linux:   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        echo "  Windows: Download from https://aka.ms/installazurecliwindows"
        echo ""
        exit 1
    fi
    AZ_VERSION=$(az version --output tsv | head -n1 | awk '{print $2}')
    print_success "Azure CLI installed (version $AZ_VERSION)"
}

check_python() {
    print_info "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 3 installed (version $PYTHON_VERSION)"
}

check_azure_auth() {
    print_info "Checking Azure authentication..."
    if ! az account show &> /dev/null; then
        print_error "Not authenticated to Azure"
        echo ""
        echo "Please run: az login"
        echo "Or use: ./audit-azure.sh --login"
        echo ""
        exit 1
    fi
    ACCOUNT_NAME=$(az account show --query "name" -o tsv)
    print_success "Authenticated to Azure (subscription: $ACCOUNT_NAME)"
}

perform_login() {
    print_info "Initiating Azure login..."
    az login
    if [ $? -eq 0 ]; then
        print_success "Successfully logged in to Azure"
    else
        print_error "Login failed"
        exit 1
    fi
}

run_audit() {
    local verbose_flag="$1"
    print_info "Starting Azure infrastructure discovery..."
    echo ""

    if [ -f "$PYTHON_SCRIPT" ]; then
        python3 "$PYTHON_SCRIPT" $verbose_flag
        if [ $? -eq 0 ]; then
            echo ""
            print_success "Audit completed successfully!"
            echo ""
            print_info "Documentation generated in: ${SCRIPT_DIR}/docs/"
            echo ""
            echo "View the report:"
            echo "  cd docs && open README.md"
            echo ""
        else
            echo ""
            print_error "Audit failed"
            exit 1
        fi
    else
        print_error "Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
}

# Main execution
main() {
    local DO_LOGIN=false
    local VERBOSE_FLAG=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --login)
                DO_LOGIN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE_FLAG="--verbose"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    print_header

    # Check prerequisites
    check_azure_cli
    check_python

    # Perform login if requested
    if [ "$DO_LOGIN" = true ]; then
        perform_login
    fi

    # Check authentication
    check_azure_auth

    # Run the audit
    run_audit "$VERBOSE_FLAG"
}

# Run main function
main "$@"

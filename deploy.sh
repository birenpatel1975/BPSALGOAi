#!/bin/bash
# ROBOAi Trading Platform - Comprehensive Deployment Script
# Checks prerequisites and deploys the platform on Linux/Mac systems

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "================================================================"
    echo "          $1"
    echo "================================================================"
    echo ""
}

# Prerequisite checks
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local all_ok=true
    
    # Check Python installation
    log_info "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python is not installed!"
        log_error "Please install Python 3.10 or higher:"
        log_error "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        log_error "  RHEL/Fedora: sudo dnf install python3 python3-pip"
        log_error "  macOS: brew install python@3.10"
        all_ok=false
        PYTHON_CMD=""
    fi
    
    if [ -n "$PYTHON_CMD" ]; then
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        log_success "Python $PYTHON_VERSION detected"
        
        # Check Python version (should be 3.10+)
        PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
        PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
        
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
            log_error "Python 3.10 or higher is required!"
            log_error "Current version: $PYTHON_VERSION"
            all_ok=false
        else
            log_success "Python version is compatible (>= 3.10)"
        fi
    fi
    
    # Check pip
    log_info "Checking pip installation..."
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        PIP_VERSION=$($PYTHON_CMD -m pip --version | awk '{print $2}')
        log_success "pip $PIP_VERSION detected"
    else
        log_error "pip is not installed!"
        log_error "Please install pip:"
        log_error "  Ubuntu/Debian: sudo apt-get install python3-pip"
        log_error "  RHEL/Fedora: sudo dnf install python3-pip"
        log_error "  macOS: python3 -m ensurepip --upgrade"
        all_ok=false
    fi
    
    # Check venv module
    log_info "Checking venv module..."
    if $PYTHON_CMD -c "import venv" 2>/dev/null; then
        log_success "venv module is available"
    else
        log_error "venv module is not installed!"
        log_error "Please install venv:"
        log_error "  Ubuntu/Debian: sudo apt-get install python3-venv"
        log_error "  RHEL/Fedora: included with python3"
        all_ok=false
    fi
    
    # Check git (optional but recommended)
    log_info "Checking git installation..."
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        log_success "git $GIT_VERSION detected"
    else
        log_warning "git is not installed (optional but recommended)"
    fi
    
    # Check system dependencies for common Python packages
    log_info "Checking system dependencies..."
    
    # Check for build-essential or equivalent
    if command -v gcc &> /dev/null || command -v clang &> /dev/null; then
        log_success "C compiler detected"
    else
        log_warning "No C compiler detected (may be needed for some packages)"
        log_warning "Install with: sudo apt-get install build-essential (Ubuntu/Debian)"
    fi
    
    # Check for pkg-config
    if command -v pkg-config &> /dev/null; then
        log_success "pkg-config detected"
    else
        log_warning "pkg-config not found (may be needed for some packages)"
    fi
    
    # Check disk space
    log_info "Checking disk space..."
    AVAILABLE_SPACE=$(df -BM . | awk 'NR==2 {print $4}' | sed 's/M//')
    if [ "$AVAILABLE_SPACE" -gt 500 ]; then
        log_success "Sufficient disk space available (${AVAILABLE_SPACE}MB)"
    else
        log_warning "Low disk space: ${AVAILABLE_SPACE}MB (recommended: 500MB+)"
    fi
    
    # Check internet connectivity
    log_info "Checking internet connectivity..."
    if ping -c 1 pypi.org &> /dev/null || ping -c 1 8.8.8.8 &> /dev/null; then
        log_success "Internet connectivity confirmed"
    else
        log_warning "Cannot verify internet connectivity (required for package installation)"
    fi
    
    echo ""
    if [ "$all_ok" = false ]; then
        log_error "Some prerequisites are missing!"
        log_error "Please install the missing components and try again."
        exit 1
    else
        log_success "All prerequisites are satisfied!"
    fi
}

# Create backup
create_backup() {
    if [ -f "config.yaml" ] || [ -d "data" ] || [ -d "logs" ]; then
        print_header "Creating Backup"
        
        BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        if [ -f "config.yaml" ]; then
            cp config.yaml "$BACKUP_DIR/"
            log_success "Backed up config.yaml"
        fi
        
        if [ -d "data" ] && [ "$(ls -A data 2>/dev/null)" ]; then
            cp -r data "$BACKUP_DIR/"
            log_success "Backed up data directory"
        fi
        
        if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
            cp -r logs "$BACKUP_DIR/"
            log_success "Backed up logs directory"
        fi
        
        log_success "Backup created in $BACKUP_DIR"
    else
        log_info "No existing data to backup"
    fi
}

# Setup virtual environment
setup_virtualenv() {
    print_header "Setting Up Virtual Environment"
    
    if [ -d "venv" ]; then
        log_info "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Removing existing virtual environment..."
            rm -rf venv
        else
            log_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    log_info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    
    if [ -f "venv/bin/activate" ]; then
        log_success "Virtual environment created"
    else
        log_error "Failed to create virtual environment"
        exit 1
    fi
}

# Activate virtual environment
activate_virtualenv() {
    log_info "Activating virtual environment..."
    source venv/bin/activate
    log_success "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    log_info "Upgrading pip..."
    $PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1
    PIP_VERSION=$($PYTHON_CMD -m pip --version | awk '{print $2}')
    log_success "pip upgraded to version $PIP_VERSION"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found!"
        exit 1
    fi
    
    log_info "Installing Python packages (this may take several minutes)..."
    echo ""
    
    # Install with progress
    $PYTHON_CMD -m pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo ""
        log_success "All dependencies installed successfully"
    else
        echo ""
        log_error "Failed to install some dependencies"
        log_error "Please check the error messages above"
        exit 1
    fi
}

# Setup configuration
setup_config() {
    print_header "Setting Up Configuration"
    
    if [ -f "config.yaml" ]; then
        log_info "config.yaml already exists"
        log_info "Keeping existing configuration"
    else
        if [ -f "config.example.yaml" ]; then
            cp config.example.yaml config.yaml
            log_success "Created config.yaml from example"
            log_warning "Please edit config.yaml to add your API credentials (if using live trading)"
        else
            log_error "config.example.yaml not found!"
            exit 1
        fi
    fi
}

# Create directories
create_directories() {
    log_info "Creating required directories..."
    
    mkdir -p data
    mkdir -p logs
    mkdir -p backups
    
    log_success "Directories created"
}

# Run tests
run_tests() {
    print_header "Running Platform Tests"
    
    if [ -f "test_platform.py" ]; then
        log_info "Running test suite..."
        echo ""
        
        $PYTHON_CMD test_platform.py
        
        if [ $? -eq 0 ]; then
            echo ""
            log_success "All tests passed!"
        else
            echo ""
            log_warning "Some tests failed, but deployment can continue"
            log_warning "Review the test output above for details"
        fi
    else
        log_warning "test_platform.py not found, skipping tests"
    fi
}

# Display summary
display_summary() {
    print_header "Deployment Complete!"
    
    echo "The ROBOAi Trading Platform has been successfully deployed!"
    echo ""
    echo "Quick Start Options:"
    echo ""
    echo "  [A] Web Dashboard (Recommended):"
    echo "      ./start_dashboard.sh"
    echo "      Then open: http://localhost:5000"
    echo ""
    echo "  [B] Console Mode:"
    echo "      ./start_roboai.sh"
    echo ""
    echo "Configuration:"
    echo "  - Configuration file: config.yaml"
    echo "  - Default mode: PAPER TRADING (safe for testing)"
    echo "  - For live trading: Edit config.yaml and add mStock API credentials"
    echo ""
    echo "Documentation:"
    echo "  - README.md - Complete guide"
    echo "  - INSTALL.md - Installation details"
    echo "  - DASHBOARD_GUIDE.md - Web dashboard guide"
    echo ""
    echo "Next Steps:"
    echo "  1. Review config.yaml"
    echo "  2. Start the platform with ./start_roboai.sh or ./start_dashboard.sh"
    echo "  3. Test in PAPER TRADING mode before considering live trading"
    echo ""
    echo "⚠️  IMPORTANT REMINDERS:"
    echo "  - Trading involves substantial risk"
    echo "  - Start with paper trading to learn the platform"
    echo "  - Never trade with money you cannot afford to lose"
    echo "  - Always test thoroughly before live trading"
    echo ""
    echo "================================================================"
    echo ""
}

# Main deployment process
main() {
    print_header "ROBOAi Trading Platform - Deployment Script"
    
    echo "This script will:"
    echo "  1. Check all prerequisites"
    echo "  2. Create a backup (if needed)"
    echo "  3. Set up virtual environment"
    echo "  4. Install dependencies"
    echo "  5. Configure the platform"
    echo "  6. Run tests"
    echo ""
    
    read -p "Continue with deployment? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ -n $REPLY ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    # Run deployment steps
    check_prerequisites
    create_backup
    setup_virtualenv
    activate_virtualenv
    upgrade_pip
    install_dependencies
    setup_config
    create_directories
    run_tests
    display_summary
    
    # Final success message
    log_success "Deployment completed successfully! 🚀"
}

# Run main function
main

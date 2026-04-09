#!/bin/bash
# Memvid Installer for macOS and Linux
# v1 - System package managers only, install-if-missing

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print success message
print_success() {
    echo -e "${GREEN}✔${NC} $1"
}

# Print error message
print_error() {
    echo -e "${RED}✖${NC} $1"
}

# Print info message
print_info() {
    echo -e "${BLUE}→${NC} $1"
}

# Print warning message
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PKG_MANAGER="brew"
        
        # Check if Homebrew is installed
        if ! command_exists brew; then
            print_error "Homebrew is not installed"
            print_info "Please install Homebrew first:"
            print_info "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO_NAME="${PRETTY_NAME:-${NAME:-$ID}}"
        
        if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
            OS="linux"
            PKG_MANAGER="apt"
            DISTRO_FAMILY="debian"
        elif [[ "$ID" == "fedora" ]] || [[ "$ID" == "rhel" ]] || [[ "$ID" == "centos" ]] || [[ "$ID" == "rocky" ]] || [[ "$ID" == "almalinux" ]]; then
            OS="linux"
            PKG_MANAGER="dnf"
            DISTRO_FAMILY="rhel"
        elif [[ "$ID" == "arch" ]] || [[ "$ID" == "manjaro" ]]; then
            OS="linux"
            PKG_MANAGER="pacman"
            DISTRO_FAMILY="arch"
        elif [[ "$ID" == "alpine" ]]; then
            OS="linux"
            PKG_MANAGER="apk"
            DISTRO_FAMILY="alpine"
        else
            print_error "Unsupported Linux distribution: $ID"
            print_info "Supported distributions: Ubuntu, Debian, Fedora, RHEL, CentOS, Arch, Alpine"
            exit 1
        fi
        
        # Check if sudo is available (except for Alpine which might use su)
        if ! command_exists sudo && [[ "$DISTRO_FAMILY" != "alpine" ]]; then
            print_error "sudo is not available"
            print_info "Please install sudo or run as root"
            exit 1
        fi
    else
        print_error "Unable to detect operating system"
        exit 1
    fi
    
    if [[ "$OS" == "linux" ]]; then
        print_info "Detected OS: $OS ($DISTRO_NAME)"
    else
        print_info "Detected OS: $OS"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Xcode Command Line Tools on macOS
check_xcode_cli_tools() {
    if [[ "$OS" != "macos" ]]; then
        return 0
    fi
    
    # Check if Xcode CLI Tools are installed
    if xcode-select -p &>/dev/null; then
        print_success "Xcode Command Line Tools already installed"
        return 0
    else
        print_error "Xcode Command Line Tools not found"
        print_warning "Xcode Command Line Tools are required for everything to work properly"
        echo ""
        
        # Ask for confirmation
        if [[ -t 0 ]] && [[ -t 1 ]]; then
            read -p "Install Xcode Command Line Tools now? [Y/n] " -n 1 -r
            echo
        elif [[ -c /dev/tty ]]; then
            read -p "Install Xcode Command Line Tools now? [Y/n] " -n 1 -r < /dev/tty
            echo
        else
            REPLY="Y"
        fi
        
        if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! $REPLY == "" ]]; then
            print_error "Xcode Command Line Tools are required for everything to work properly"
            print_info "Please install them manually with: xcode-select --install"
            exit 1
        fi
        
        print_info "Installing Xcode Command Line Tools..."
        xcode-select --install
        
        print_info "Please complete the Xcode Command Line Tools installation in the popup window"
        print_info "Then run this installer again"
        exit 0
    fi
}

# Install system dependencies for Linux
install_system_deps() {
    if [[ "$OS" != "linux" ]]; then
        return 0
    fi
    
    print_info "Checking system dependencies..."
    
    NEEDS_DEPS=false
    DEPS_TO_INSTALL=()
    
    # Check and collect missing dependencies
    if [[ "$DISTRO_FAMILY" == "debian" ]]; then
        if ! dpkg -l | grep -q "^ii.*ca-certificates"; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("ca-certificates")
        fi
        if ! command_exists curl; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("curl")
        fi
        if ! dpkg -l | grep -q "^ii.*libssl3"; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("libssl3")
        fi
    elif [[ "$DISTRO_FAMILY" == "rhel" ]]; then
        if ! rpm -q ca-certificates &>/dev/null; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("ca-certificates")
        fi
        if ! command_exists curl; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("curl")
        fi
        if ! rpm -q openssl &>/dev/null; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("openssl")
        fi
    elif [[ "$DISTRO_FAMILY" == "arch" ]]; then
        if ! pacman -Q ca-certificates &>/dev/null; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("ca-certificates")
        fi
        if ! command_exists curl; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("curl")
        fi
        if ! pacman -Q openssl &>/dev/null; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("openssl")
        fi
    elif [[ "$DISTRO_FAMILY" == "alpine" ]]; then
        if ! apk info -e ca-certificates &>/dev/null; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("ca-certificates")
        fi
        if ! command_exists curl; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("curl")
        fi
        if ! apk info -e openssl &>/dev/null; then
            NEEDS_DEPS=true
            DEPS_TO_INSTALL+=("openssl")
        fi
    fi
    
    if [[ "$NEEDS_DEPS" == false ]]; then
        print_success "All system dependencies are installed"
        return 0
    fi
    
    print_info "Installing system dependencies: ${DEPS_TO_INSTALL[*]}..."
    
    if [[ "$DISTRO_FAMILY" == "debian" ]]; then
        sudo apt-get update
        sudo apt-get install -y --no-install-recommends "${DEPS_TO_INSTALL[@]}"
    elif [[ "$DISTRO_FAMILY" == "rhel" ]]; then
        sudo dnf install -y "${DEPS_TO_INSTALL[@]}"
    elif [[ "$DISTRO_FAMILY" == "arch" ]]; then
        sudo pacman -S --noconfirm "${DEPS_TO_INSTALL[@]}"
    elif [[ "$DISTRO_FAMILY" == "alpine" ]]; then
        if command_exists sudo; then
            sudo apk add --no-cache "${DEPS_TO_INSTALL[@]}"
        else
            apk add --no-cache "${DEPS_TO_INSTALL[@]}"
        fi
    fi
    
    print_success "System dependencies installed successfully"
}

# Check for git
check_git() {
    if command_exists git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "git already installed (version $GIT_VERSION)"
        return 0
    else
        print_error "git not found"
        return 1
    fi
}

# Check for node
check_node() {
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "node already installed ($NODE_VERSION)"
        
        # Check if it's LTS (rough check - version should be even major version)
        MAJOR_VERSION=$(echo "$NODE_VERSION" | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$((MAJOR_VERSION % 2))" -eq 0 ]; then
            print_info "Node version appears to be LTS-compatible"
        fi
        
        # Check for npm
        if command_exists npm; then
            NPM_VERSION=$(npm --version)
            print_success "npm already installed (version $NPM_VERSION)"
            return 0
        else
            print_error "npm not found (should come with node)"
            return 1
        fi
    else
        print_error "node not found"
        return 1
    fi
}

# Install git
install_git() {
    print_info "Installing git using $PKG_MANAGER..."
    
    if [[ "$OS" == "macos" ]]; then
        brew install git
    elif [[ "$OS" == "linux" ]]; then
        if [[ "$DISTRO_FAMILY" == "debian" ]]; then
            sudo apt-get update
            sudo apt-get install -y git
        elif [[ "$DISTRO_FAMILY" == "rhel" ]]; then
            sudo dnf install -y git
        elif [[ "$DISTRO_FAMILY" == "arch" ]]; then
            sudo pacman -S --noconfirm git
        elif [[ "$DISTRO_FAMILY" == "alpine" ]]; then
            if command_exists sudo; then
                sudo apk add --no-cache git
            else
                apk add --no-cache git
            fi
        fi
    fi
    
    if command_exists git; then
        print_success "git installed successfully"
    else
        print_error "git installation failed"
        exit 1
    fi
}

# Install node (LTS)
install_node() {
    print_info "Installing node (LTS) using $PKG_MANAGER..."
    
    if [[ "$OS" == "macos" ]]; then
        brew install node@lts
        # Add to PATH if needed
        if ! command_exists node; then
            print_info "Adding node to PATH..."
            # Detect Homebrew prefix (Apple Silicon vs Intel)
            if [[ -d "/opt/homebrew" ]]; then
                BREW_PREFIX="/opt/homebrew"
            else
                BREW_PREFIX="/usr/local"
            fi
            
            # Detect shell
            if [[ "$SHELL" == *"zsh"* ]]; then
                SHELL_RC="$HOME/.zshrc"
            else
                SHELL_RC="$HOME/.bash_profile"
            fi
            
            echo "export PATH=\"$BREW_PREFIX/opt/node@lts/bin:\$PATH\"" >> "$SHELL_RC"
            export PATH="$BREW_PREFIX/opt/node@lts/bin:$PATH"
        fi
    elif [[ "$OS" == "linux" ]]; then
        if [[ "$DISTRO_FAMILY" == "debian" ]]; then
            # Install Node.js LTS from NodeSource
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y --no-install-recommends nodejs
        elif [[ "$DISTRO_FAMILY" == "rhel" ]]; then
            # Install Node.js LTS from NodeSource
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo -E bash -
            sudo dnf install -y nodejs
        elif [[ "$DISTRO_FAMILY" == "arch" ]]; then
            sudo pacman -S --noconfirm nodejs npm
        elif [[ "$DISTRO_FAMILY" == "alpine" ]]; then
            if command_exists sudo; then
                sudo apk add --no-cache nodejs npm
            else
                apk add --no-cache nodejs npm
            fi
        fi
    fi
    
    if command_exists node && command_exists npm; then
        NODE_VERSION=$(node --version)
        NPM_VERSION=$(npm --version)
        print_success "node installed successfully ($NODE_VERSION)"
        print_success "npm installed successfully (version $NPM_VERSION)"
    else
        print_error "node installation failed"
        exit 1
    fi
}

# Check if memvid is already installed
check_memvid() {
    if command_exists memvid; then
        # Get version - output format is "memvid 2.0.131"
        MEMVID_VERSION=$(memvid --version 2>&1 | awk '{print $2}')
        print_success "memvid already installed ($MEMVID_VERSION)"
        return 0
    else
        print_error "memvid not found"
        return 1
    fi
}

# Install missing tools
install_missing() {
    NEEDS_GIT=false
    NEEDS_NODE=false
    NEEDS_MEMVID=false
    
    if ! check_git; then
        NEEDS_GIT=true
    fi
    
    if ! check_node; then
        NEEDS_NODE=true
    fi
    
    if ! check_memvid; then
        NEEDS_MEMVID=true
    fi
    
    if [[ "$NEEDS_GIT" == false ]] && [[ "$NEEDS_NODE" == false ]] && [[ "$NEEDS_MEMVID" == false ]]; then
        print_info "All dependencies are already installed"
        return 0
    fi
    
    # Show what will be installed
    echo ""
    print_warning "The following tools will be installed:"
    [[ "$NEEDS_GIT" == true ]] && echo "  - git"
    [[ "$NEEDS_NODE" == true ]] && echo "  - node (LTS)"
    [[ "$NEEDS_MEMVID" == true ]] && echo "  - memvid-cli (latest)"
    echo ""
    
    # Ask for confirmation
    # Read from /dev/tty to ensure it works when piped via curl | bash
    if [[ -t 0 ]] && [[ -t 1 ]]; then
        # Interactive terminal - read normally
        read -p "Continue? [Y/n] " -n 1 -r
        echo
    elif [[ -c /dev/tty ]]; then
        # Piped input - read from terminal device
        read -p "Continue? [Y/n] " -n 1 -r < /dev/tty
        echo
    else
        # No terminal available - proceed automatically (non-interactive mode)
        print_info "No terminal detected, proceeding with installation..."
        REPLY="Y"
    fi
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! $REPLY == "" ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    
    # Install missing tools
    [[ "$NEEDS_GIT" == true ]] && install_git
    [[ "$NEEDS_NODE" == true ]] && install_node
    [[ "$NEEDS_MEMVID" == true ]] && install_memvid
}

# Install memvid
install_memvid() {
    print_info "Installing memvid globally..."
    
    if [[ "$OS" == "linux" ]]; then
        # Linux requires sudo for global npm installs
        if sudo npm install -g memvid-cli@latest; then
            print_success "memvid installed successfully"
        else
            print_error "memvid installation failed"
            exit 1
        fi
    else
        # macOS typically doesn't need sudo if npm was installed via Homebrew
        if npm install -g memvid-cli@latest; then
            print_success "memvid installed successfully"
        else
            print_error "memvid installation failed"
            exit 1
        fi
    fi
}

# Verify installation
verify() {
    print_info "Verifying installation..."
    
    if command_exists memvid; then
        # Get version - output format is "memvid 2.0.131"
        MEMVID_VERSION=$(memvid --version 2>&1 | awk '{print $2}')
        
        print_success "memvid is installed and accessible"
        print_info "Version: $MEMVID_VERSION"
        echo ""
        print_success "Installation complete! You can now use 'memvid' command."
    else
        print_error "memvid verification failed"
        print_info "The installation may have completed, but 'memvid' command is not in PATH"
        print_info "Please check your npm global bin directory and add it to PATH if needed"
        print_info "Or try: npm list -g memvid-cli"
        exit 1
    fi
}

# Main execution
main() {
    echo "Memvid Installer"
    echo "Checking system requirements…"
    echo ""
    
    detect_os
    echo ""
    
    # Check Xcode CLI Tools on macOS
    if [[ "$OS" == "macos" ]]; then
        check_xcode_cli_tools
        echo ""
    fi
    
    # Install system dependencies on Linux
    if [[ "$OS" == "linux" ]]; then
        install_system_deps
        echo ""
    fi
    
    install_missing
    echo ""
    
    verify
}

# Run main function
main

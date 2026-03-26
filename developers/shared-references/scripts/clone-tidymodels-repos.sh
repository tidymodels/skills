#!/bin/bash

################################################################################
# Clone Tidymodels Repositories
#
# Description:
#   Clones tidymodels package repositories (yardstick, recipes) for development
#   reference. Creates repos/ directory, clones with shallow clone for speed,
#   and updates .gitignore and .Rbuildignore to prevent committing cloned code.
#
# Usage:
#   ./clone-tidymodels-repos.sh yardstick
#   ./clone-tidymodels-repos.sh recipes
#   ./clone-tidymodels-repos.sh yardstick recipes
#   ./clone-tidymodels-repos.sh all
#
# Exit Codes:
#   0 - Success
#   1 - Git not found
#   2 - Clone failed (network/disk space)
#   3 - Permission error
#
# Target Platforms:
#   macOS, Linux, WSL, Git Bash on Windows
################################################################################

set -e  # Exit on error (we'll handle specific errors)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository configuration (compatible with bash 3.2+)
# Format: "name|url" pairs
REPOS=(
    "yardstick|https://github.com/tidymodels/yardstick.git"
    "recipes|https://github.com/tidymodels/recipes.git"
)

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to get repo URL by name
get_repo_url() {
    local name="$1"
    for repo in "${REPOS[@]}"; do
        local repo_name="${repo%%|*}"
        local repo_url="${repo##*|}"
        if [ "$repo_name" = "$name" ]; then
            echo "$repo_url"
            return 0
        fi
    done
    return 1
}

# Function to check if repo name is valid
is_valid_repo() {
    local name="$1"
    for repo in "${REPOS[@]}"; do
        local repo_name="${repo%%|*}"
        if [ "$repo_name" = "$name" ]; then
            return 0
        fi
    done
    return 1
}

# Function to check if git is installed
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed."
        echo ""
        echo "Please install git to use this script:"
        echo "  - macOS: Install Xcode Command Line Tools or visit https://git-scm.com/downloads"
        echo "  - Linux: Use your package manager (apt-get install git, yum install git, etc.)"
        echo "  - Windows: Download from https://git-scm.com/downloads"
        exit 1
    fi
    print_success "Git is installed ($(git --version))"
}

# Function to update .gitignore
update_gitignore() {
    local gitignore_path=".gitignore"

    if [ -f "$gitignore_path" ]; then
        # Check if repos/ already exists in .gitignore
        if grep -q "^repos/$" "$gitignore_path"; then
            print_info ".gitignore already contains 'repos/'"
        else
            echo "repos/" >> "$gitignore_path"
            print_success "Added 'repos/' to .gitignore"
        fi
    else
        echo "repos/" > "$gitignore_path"
        print_success "Created .gitignore with 'repos/'"
    fi
}

# Function to update .Rbuildignore
update_rbuildignore() {
    local rbuildignore_path=".Rbuildignore"
    local entry="^repos\$"

    if [ -f "$rbuildignore_path" ]; then
        # Check if ^repos$ already exists in .Rbuildignore
        if grep -qF "$entry" "$rbuildignore_path"; then
            print_info ".Rbuildignore already contains '^repos\$'"
        else
            echo "$entry" >> "$rbuildignore_path"
            print_success "Added '^repos\$' to .Rbuildignore"
        fi
    else
        echo "$entry" > "$rbuildignore_path"
        print_success "Created .Rbuildignore with '^repos\$'"
    fi
}

# Function to clone a repository
clone_repo() {
    local repo_name="$1"
    local repo_url="$2"
    local repo_path="repos/$repo_name"

    print_info "Processing $repo_name..."

    # Check if repository already exists
    if [ -d "$repo_path" ]; then
        print_warning "Repository already exists at $repo_path (skipping)"
        return 0
    fi

    # Clone repository with shallow clone
    print_info "Cloning $repo_name from $repo_url..."
    if git clone --depth 1 "$repo_url" "$repo_path" 2>&1 | sed 's/^/  /'; then
        print_success "Cloned $repo_name to $repo_path"

        # Verify shallow clone
        if [ -f "$repo_path/.git/shallow" ]; then
            print_success "Shallow clone verified (.git/shallow exists)"
        fi

        return 0
    else
        print_error "Failed to clone $repo_name"
        return 2
    fi
}

# Main script
main() {
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "  Tidymodels Repository Cloning Script"
    echo "═══════════════════════════════════════════════════════"
    echo ""

    # Check if arguments provided
    if [ $# -eq 0 ]; then
        print_error "No packages specified."
        echo ""
        echo "Usage: $0 <package> [<package> ...]"
        echo "  Packages: yardstick, recipes, all"
        echo ""
        echo "Examples:"
        echo "  $0 yardstick"
        echo "  $0 recipes"
        echo "  $0 yardstick recipes"
        echo "  $0 all"
        exit 1
    fi

    # Step 1: Check git installation
    print_info "Step 1/4: Checking git installation..."
    check_git
    echo ""

    # Step 2: Create repos/ directory
    print_info "Step 2/4: Creating repos/ directory..."
    if [ ! -d "repos" ]; then
        if mkdir -p repos 2>/dev/null; then
            print_success "Created repos/ directory"
        else
            print_error "Failed to create repos/ directory (permission denied)"
            exit 3
        fi
    else
        print_info "repos/ directory already exists"
    fi
    echo ""

    # Step 3: Clone repositories
    print_info "Step 3/4: Cloning repositories..."

    # Determine which packages to clone
    packages_to_clone=()

    for arg in "$@"; do
        if [ "$arg" = "all" ]; then
            # Clone all repositories
            for repo in "${REPOS[@]}"; do
                repo_name="${repo%%|*}"
                packages_to_clone+=("$repo_name")
            done
            break
        elif is_valid_repo "$arg"; then
            packages_to_clone+=("$arg")
        else
            print_warning "Unknown package: $arg (skipping)"
        fi
    done

    if [ ${#packages_to_clone[@]} -eq 0 ]; then
        print_error "No valid packages specified"
        exit 1
    fi

    # Clone each repository
    clone_failed=0
    for package in "${packages_to_clone[@]}"; do
        repo_url=$(get_repo_url "$package")
        if ! clone_repo "$package" "$repo_url"; then
            clone_failed=1
        fi
    done

    if [ $clone_failed -eq 1 ]; then
        echo ""
        print_error "Some repositories failed to clone"
        echo ""
        echo "Possible issues:"
        echo "  - Network connectivity problems"
        echo "  - Insufficient disk space (~5-8 MB per repository)"
        echo "  - Repository URL changed (unlikely)"
        exit 2
    fi
    echo ""

    # Step 4: Update ignore files
    print_info "Step 4/4: Updating .gitignore and .Rbuildignore..."
    update_gitignore
    update_rbuildignore
    echo ""

    # Success summary
    echo "═══════════════════════════════════════════════════════"
    print_success "Repository setup complete!"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "Cloned repositories:"
    for package in "${packages_to_clone[@]}"; do
        if [ -d "repos/$package" ]; then
            echo "  ✓ repos/$package/"
        fi
    done
    echo ""
    echo "Modified files:"
    echo "  ✓ .gitignore (added 'repos/')"
    echo "  ✓ .Rbuildignore (added '^repos\$')"
    echo ""
    print_info "These repositories are now available for reference during development."
    echo ""
}

# Run main function
main "$@"

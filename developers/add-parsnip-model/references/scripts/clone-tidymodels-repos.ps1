<#
.SYNOPSIS
    Clone Tidymodels Repositories for development reference.

.DESCRIPTION
    Clones tidymodels package repositories (yardstick, recipes, dials, parsnip)
    for development reference. Creates repos\ directory, clones with shallow
    clone for speed, and updates .gitignore and .Rbuildignore to prevent
    committing cloned code.

.PARAMETER Packages
    One or more package names to clone: yardstick, recipes, dials, parsnip, or all

.EXAMPLE
    .\clone-tidymodels-repos.ps1 yardstick

.EXAMPLE
    .\clone-tidymodels-repos.ps1 recipes

.EXAMPLE
    .\clone-tidymodels-repos.ps1 dials

.EXAMPLE
    .\clone-tidymodels-repos.ps1 parsnip

.EXAMPLE
    .\clone-tidymodels-repos.ps1 yardstick recipes dials parsnip

.EXAMPLE
    .\clone-tidymodels-repos.ps1 all

.NOTES
    Exit Codes:
      0 - Success
      1 - Git not found
      2 - Clone failed (network/disk space)
      3 - Permission error

    Target Platform:
      Windows (PowerShell 5.1+, pre-installed on Windows 7+)

    Execution Policy:
      If you encounter execution policy errors, run:
      Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

      Or run with bypass:
      powershell -ExecutionPolicy Bypass -File .\clone-tidymodels-repos.ps1 yardstick
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false, Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Packages
)

# Repository configuration
$Repos = @{
    "yardstick" = "https://github.com/tidymodels/yardstick.git"
    "recipes"   = "https://github.com/tidymodels/recipes.git"
    "dials"     = "https://github.com/tidymodels/dials.git"
    "parsnip"   = "https://github.com/tidymodels/parsnip.git"
}

# Function to print colored messages
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO]" -ForegroundColor Blue -NoNewline
    Write-Host " $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK]" -ForegroundColor Green -NoNewline
    Write-Host " $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN]" -ForegroundColor Yellow -NoNewline
    Write-Host " $Message"
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR]" -ForegroundColor Red -NoNewline
    Write-Host " $Message"
}

# Function to check if git is installed
function Test-GitInstalled {
    $gitPath = Get-Command git.exe -ErrorAction SilentlyContinue

    if (-not $gitPath) {
        Write-Error "Git is not installed."
        Write-Host ""
        Write-Host "Please install git to use this script:"
        Write-Host "  - Download from https://git-scm.com/downloads"
        Write-Host "  - Or install via winget: winget install Git.Git"
        Write-Host "  - Or install via Chocolatey: choco install git"
        exit 1
    }

    $ErrorActionPreference = 'Continue'
    $gitVersion = git --version 2>&1
    Write-Success "Git is installed ($gitVersion)"
}

# Function to update .gitignore
function Update-GitIgnore {
    $gitignorePath = ".gitignore"
    $entry = "repos/"

    if (Test-Path $gitignorePath) {
        $content = Get-Content $gitignorePath -Raw

        if ($content -match [regex]::Escape($entry)) {
            Write-Info ".gitignore already contains '$entry'"
        }
        else {
            Add-Content -Path $gitignorePath -Value $entry -NoNewline:$false
            Write-Success "Added '$entry' to .gitignore"
        }
    }
    else {
        Set-Content -Path $gitignorePath -Value $entry -NoNewline:$false
        Write-Success "Created .gitignore with '$entry'"
    }
}

# Function to update .Rbuildignore
function Update-RBuildIgnore {
    $rbuildignorePath = ".Rbuildignore"
    $entry = "^repos$"

    if (Test-Path $rbuildignorePath) {
        $content = Get-Content $rbuildignorePath -Raw

        if ($content -match [regex]::Escape($entry)) {
            Write-Info ".Rbuildignore already contains '$entry'"
        }
        else {
            Add-Content -Path $rbuildignorePath -Value $entry -NoNewline:$false
            Write-Success "Added '$entry' to .Rbuildignore"
        }
    }
    else {
        Set-Content -Path $rbuildignorePath -Value $entry -NoNewline:$false
        Write-Success "Created .Rbuildignore with '$entry'"
    }
}

# Function to clone a repository
function Clone-Repository {
    param(
        [string]$RepoName,
        [string]$RepoUrl
    )

    $repoPath = "repos\$RepoName"

    Write-Info "Processing $RepoName..."

    # Check if repository already exists
    if (Test-Path $repoPath) {
        Write-Warning "Repository already exists at $repoPath (skipping)"
        return $true
    }

    # Clone repository with shallow clone
    Write-Info "Cloning $RepoName from $RepoUrl..."

    $ErrorActionPreference = 'Continue'
    $output = git clone --depth 1 $RepoUrl $repoPath 2>&1
    $output | ForEach-Object { Write-Host "  $_" }

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone $RepoName"
        return $false
    }

    Write-Success "Cloned $RepoName to $repoPath"

    # Verify shallow clone
    $shallowFile = Join-Path $repoPath ".git\shallow"
    if (Test-Path $shallowFile) {
        Write-Success "Shallow clone verified (.git\shallow exists)"
    }

    return $true
}

# Main script
function Main {
    Write-Host ""
    Write-Host "======================================================="
    Write-Host "  Tidymodels Repository Cloning Script"
    Write-Host "======================================================="
    Write-Host ""

    # Check if packages were provided
    if (-not $Packages -or $Packages.Count -eq 0) {
        Write-Error "No packages specified."
        Write-Host ""
        Write-Host "Usage: .\clone-tidymodels-repos.ps1 PACKAGE [PACKAGE ...]"
        Write-Host "  Packages: yardstick, recipes, dials, parsnip, all"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\clone-tidymodels-repos.ps1 yardstick"
        Write-Host "  .\clone-tidymodels-repos.ps1 recipes"
        Write-Host "  .\clone-tidymodels-repos.ps1 dials"
        Write-Host "  .\clone-tidymodels-repos.ps1 parsnip"
        Write-Host "  .\clone-tidymodels-repos.ps1 yardstick recipes dials parsnip"
        Write-Host "  .\clone-tidymodels-repos.ps1 all"
        exit 1
    }

    # Step 1: Check git installation
    Write-Info "Step 1/4: Checking git installation..."
    Test-GitInstalled
    Write-Host ""

    # Step 2: Create repos\ directory
    Write-Info "Step 2/4: Creating repos\ directory..."
    if (-not (Test-Path "repos")) {
        try {
            New-Item -ItemType Directory -Path "repos" -ErrorAction Stop | Out-Null
            Write-Success "Created repos\ directory"
        }
        catch {
            Write-Error "Failed to create repos\ directory (permission denied)"
            exit 3
        }
    }
    else {
        Write-Info "repos\ directory already exists"
    }
    Write-Host ""

    # Step 3: Clone repositories
    Write-Info "Step 3/4: Cloning repositories..."

    # Determine which packages to clone
    $packagesToClone = @()

    foreach ($package in $Packages) {
        if ($package -eq "all") {
            $packagesToClone = $Repos.Keys
            break
        }
        elseif ($Repos.ContainsKey($package)) {
            $packagesToClone += $package
        }
        else {
            Write-Warning "Unknown package: $package (skipping)"
        }
    }

    if ($packagesToClone.Count -eq 0) {
        Write-Error "No valid packages specified"
        Write-Host ""
        Write-Host "Usage: .\clone-tidymodels-repos.ps1 PACKAGE [PACKAGE ...]"
        Write-Host "  Packages: yardstick, recipes, dials, parsnip, all"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\clone-tidymodels-repos.ps1 yardstick"
        Write-Host "  .\clone-tidymodels-repos.ps1 recipes"
        Write-Host "  .\clone-tidymodels-repos.ps1 dials"
        Write-Host "  .\clone-tidymodels-repos.ps1 parsnip"
        Write-Host "  .\clone-tidymodels-repos.ps1 yardstick recipes dials parsnip"
        Write-Host "  .\clone-tidymodels-repos.ps1 all"
        exit 1
    }

    # Clone each repository
    $cloneFailed = $false
    foreach ($package in $packagesToClone) {
        $success = Clone-Repository -RepoName $package -RepoUrl $Repos[$package]
        if (-not $success) {
            $cloneFailed = $true
        }
    }

    if ($cloneFailed) {
        Write-Host ""
        Write-Error "Some repositories failed to clone"
        Write-Host ""
        Write-Host "Possible issues:"
        Write-Host "  - Network connectivity problems"
        Write-Host "  - Insufficient disk space (~5-8 MB per repository)"
        Write-Host "  - Repository URL changed (unlikely)"
        exit 2
    }
    Write-Host ""

    # Step 4: Update ignore files
    Write-Info "Step 4/4: Updating .gitignore and .Rbuildignore..."
    Update-GitIgnore
    Update-RBuildIgnore
    Write-Host ""

    # Success summary
    Write-Host "======================================================="
    Write-Success "Repository setup complete!"
    Write-Host "======================================================="
    Write-Host ""
    Write-Host "Cloned repositories:"
    foreach ($package in $packagesToClone) {
        if (Test-Path "repos\$package") {
            Write-Host "  - repos\$package\"
        }
    }
    Write-Host ""
    Write-Host "Modified files:"
    Write-Host "  - .gitignore (added 'repos/')"
    Write-Host "  - .Rbuildignore (added '^repos$')"
    Write-Host ""
    Write-Info "These repositories are now available for reference during development."
    Write-Host ""
}

# Run main function
Main

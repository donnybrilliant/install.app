#!/bin/bash

# Update macOS
echo "Updating macOS..."
softwareupdate -i -a

# Install Homebrew
if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Update and check Homebrew
echo "Checking Homebrew installation..."
brew update && brew doctor

# Add your other commands here

#!/bin/zsh

# Update macOS
echo "Updating macOS..."
softwareupdate -i -a
echo "Installing Rosetta.."
softwareupdate --install-rosetta --agree-to-license >/dev/null 2>&1

# Install Homebrew

echo "Installing Homebrew..."
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Update and Check Homebrew
echo "Checking Homebrew installation..."
brew update && brew doctor

export HOMEBREW_NO_INSTALL_CLEANUP=1

# Install Homebrew Packages
echo "Installing Homebrew packages..."
#BREWPACKAGES#

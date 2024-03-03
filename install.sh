#!/bin/zsh

# Update macOS
echo "Updating macOS..."
softwareupdate -i -a
echo "Installing Rosetta.."
softwareupdate --install-rosetta --agree-to-license # >/dev/null 2>&1

# Install Homebrew

echo "Installing Homebrew..."
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # >/dev/null
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Update and Check Homebrew
echo "Checking Homebrew installation..."
brew update && brew doctor

export HOMEBREW_NO_INSTALL_CLEANUP=1

# Install Homebrew Packages
echo "Installing Homebrew packages..."
#BREWPACKAGES#

# Install NVM
echo "Installing NVM..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Clean up Homebrew
echo "Cleaning up..."
brew update && brew upgrade && brew cleanup && brew doctor
mkdir -p ~/Library/LaunchAgents
brew tap homebrew/autoupdate
brew autoupdate start 86400 --upgrade --cleanup --immediate --sudo

# Install ohmyzsh
echo "Installing ohmyzsh!"
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

#!/bin/bash

# Enable error tracing
set -x

echo "Starting setup script..."

# Function to log and execute command
run_cmd() {
    echo "Running: $@"
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "Error executing: $@" >&2
        return $status
    fi
    return 0
}

# Initialize git and mark directory as safe
echo "Initializing git..."
run_cmd git config --global init.defaultBranch main
run_cmd git config --global user.email "dev@example.com"
run_cmd git config --global user.name "Developer"
# Mark the workspace as a safe directory
run_cmd git config --global --add safe.directory /workspaces/ecowitt_iot

# Check if we're in a git repo, if not initialize one
if [ ! -d .git ]; then
    echo "Creating git repository..."
    run_cmd git init
fi

# Show git status
echo "Git status:"
run_cmd git status

# Install Python requirements
echo "Installing Python requirements..."
run_cmd python3 -m pip install --upgrade pip
run_cmd pip install -r requirements_test.txt

# Install pre-commit
echo "Installing pre-commit..."
run_cmd pre-commit install

# Validate pre-commit configuration
echo "Validating pre-commit configuration..."
run_cmd pre-commit validate-config

echo "Setup complete!"

# If we get here, everything worked
exit 0

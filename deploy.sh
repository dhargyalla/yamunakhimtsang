#!/bin/bash

# Set the repository URL and project directory
REPO_URL="git@github.com:dhargyalla/yamunakhimtsang.git"
PROJECT_DIR="/home/u347881787/domains/tenzinquilling.com/public_html/yamunakhimtsang"

echo "Deployment start"
echo "Repository URL: $REPO_URL"

# Check if project directory exists and create it if it doesn't
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Project directory does not exist, creating it"
    mkdir -p $PROJECT_DIR
    if [ $? -eq 0 ]; then
        echo "Project directory created"
    else
        echo "Failed to create project directory"
        exit 1
    fi
fi

# Navigate to project directory
cd $PROJECT_DIR || { echo "Failed to enter project directory"; exit 1; }

# Check if project directory is empty
if [ -z "$(ls -A $PROJECT_DIR)" ]; then
    echo "Project directory is empty"
    echo "Cloning code repository"
    git clone $REPO_URL $PROJECT_DIR
    if [ $? -eq 0 ]; then
        echo "Repository successfully cloned"
    else
        echo "Failed to clone repository"
        exit 1
    fi
else
    echo "Project directory is not empty"

    # Remove any existing tarball to avoid conflicts
    if [ -f "yamunakhimtsang_with_venv.tar.gz" ]; then
        echo "Removing existing yamunakhimtsang_with_venv.tar.gz"
        rm yamunakhimtsang_with_venv.tar.gz
    fi

    echo "Pulling latest changes from repository"
    git pull || { echo "Failed to update repository"; exit 1; }
fi

# Check if the virtual environment exists and create it if it doesn't
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating it."
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
fi

# Activate the virtual environment
echo "Activating the virtual environment"
source venv/bin/activate

# Check if requirements.txt file exists
echo "Looking for requirements.txt file"
if [ -f "requirements.txt" ]; then
    echo "requirements.txt file found"
    echo "Installing dependencies"
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "Dependencies successfully installed"
    else
        echo "Failed to install dependencies"
        exit 1
    fi
else
    echo "requirements.txt file was not found"
fi

echo "Deployment end"

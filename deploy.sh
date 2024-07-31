#!/bin/bash

# Set the repository URL and project directory
REPO_URL="git@github.com:dhargyalla/yamunakhimtsang.git"
PROJECT_DIR="/home/u347881787/domains/tenzinquilling.com/public_html"

echo "Deployment start"
echo "Repository URL: $REPO_URL"

# Check if project directory is empty
echo "Checking if project directory is empty"
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
    echo "Pulling latest changes from repository"
    cd $PROJECT_DIR
    git pull
    if [ $? -eq 0 ]; then
        echo "Repository successfully updated"
    else
        echo "Failed to update repository"
        exit 1
    fi
fi

# Ensure we are in the project directory
cd $PROJECT_DIR || { echo "Failed to enter project directory"; exit 1; }

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

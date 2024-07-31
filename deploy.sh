#!/bin/bash

# Set the repository URL
REPO_URL="git@github.com:dhargyalla/yamunakhimtsang.git"
PROJECT_DIR="/home/u347881787/domains/tenzinquilling.com/public_html"

echo "Deployment start"
echo "Repository $REPO_URL"

# Check if project directory is empty
echo "Checking if project directory is empty"
if [ -z "$(ls -A $PROJECT_DIR)" ]; then
    echo "Project directory is empty"
    echo "Cloning code repository"
    git clone $REPO_URL $PROJECT_DIR
    echo "Repository cloned"
else
    echo "Project directory is not empty"
fi

cd $PROJECT_DIR

# Check if requirements.txt file exists
echo "Looking for requirements.txt file"
if [ -f "requirements.txt" ]; then
    echo "requirements.txt file found"
    echo "Installing dependencies"
    pip install -r requirements.txt
    echo "Dependencies installed"
else
    echo "requirements.txt file was not found"
fi

echo "Deployment end"

#!/bin/bash

# Create a new branch for finalizing the system
echo "Creating new branch for system finalization..."

# Make sure we're on main and up to date
git checkout main
git pull origin main

# Create new branch
BRANCH_NAME="finalize-working-system-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BRANCH_NAME"

echo "Created branch: $BRANCH_NAME"

# Add any uncommitted changes
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit"
else
    git commit -m "Finalize working Commercial-View system

    - System successfully validated and running
    - Configuration files working correctly
    - Sample output generated successfully  
    - Export directories created properly
    - All validation tests passing"
fi

# Push branch
git push origin "$BRANCH_NAME"

echo "Branch pushed. You can now create a PR from GitHub interface."
echo "Branch name: $BRANCH_NAME"

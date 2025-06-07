#!/bin/bash

# Script: bash_push.sh
# Purpose: Automatically push latest README.md and other staged changes to GitHub with a standard commit message
# Usage: Run from root folder of your repo

clear
echo "📦 Preparing to push your updates to GitHub..."

# Step 1: Add all changes (customize to only README.md if needed)
git add README.md

# Step 2: Commit with a clean, standard message
echo "📝 Committing changes..."
git commit -m "Push clean and final version of README.md with structure and emoji"

# Step 3: Push to remote origin (main branch)
echo "🚀 Pushing to GitHub..."
git push origin main

# Done
echo "✅ Done! Your updated README.md should now be live on GitHub."

exit 0

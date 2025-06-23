#!/bin/bash

# Script: bash_push_improved.sh
# Purpose: Stages, commits, pulls, and pushes all changes to GitHub with user prompt.
# Usage: Run from the root folder of your repo

clear
echo "📦 Preparing to sync your project with GitHub..."

# Met à jour un fichier à chaque push pour forcer un nouveau commit
date > .timestamp

# Récupère la branche courante automatiquement
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# 1. Ajoute TOUS les changements (modifiés et nouveaux)
echo "➕ Staging all changes..."
git add .

# 2. Demande un message de commit personnalisé
echo "📝 Please enter your commit message:"
read -p "> " COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
  echo "❌ Commit message cannot be empty. Aborting."
  exit 1
fi

# 3. Commit avec le message
git commit -m "$COMMIT_MESSAGE"

# 4. Pull les dernières modifications de la branche courante
echo "🔄 Pulling latest changes from GitHub ($BRANCH)..."
git pull origin "$BRANCH"

# 5. Push vers la branche courante
echo "🚀 Pushing to GitHub ($BRANCH)..."
git push origin "$BRANCH"

echo "✅ Done! Your project should now be fully synced with GitHub."

exit 0
#!/bin/bash

# Script: bash_push_improved.sh
# Purpose: Automatically stage all changes, ask for a commit message, pull, and push updates to GitHub.
# Usage: Run from root folder of your repo

clear
echo "📦 Preparing to sync your project with GitHub..."

# Étape 1 : Ajoute TOUS les changements en cours (fichiers modifiés et nouveaux)
echo "➕ Staging all changes..."
git add .

# Étape 2 : Demande un message de commit personnalisé
echo "📝 Please enter your commit message:"
read -p "> " COMMIT_MESSAGE

# Étape 3 : Fait le commit avec votre message
git commit -m "$COMMIT_MESSAGE"

# Étape 4 : TIRE les dernières modifications de GitHub pour éviter les conflits
echo "🔄 Pulling latest changes from GitHub..."
git pull origin main

# Étape 5 : Pousse TOUT vers GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

# Terminé
echo "✅ Done! Your project should now be fully synced with GitHub."

exit 0
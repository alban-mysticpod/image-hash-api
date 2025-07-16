#!/bin/bash

echo "🚀 Démarrage de l'API Image Hash Template"
echo "========================================"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip n'est pas installé"
    exit 1
fi

# Installer les dépendances si requirements.txt existe
if [ -f "requirements.txt" ]; then
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de l'installation des dépendances"
        exit 1
    fi
    echo "✅ Dépendances installées"
else
    echo "⚠️  Fichier requirements.txt introuvable"
fi

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p data/uploads
echo "✅ Répertoires créés"

# Démarrer l'API
echo "🌟 Démarrage de l'API sur http://localhost:8080"
echo "📚 Documentation disponible sur http://localhost:8080/docs"
echo ""
echo "Pour arrêter l'API, appuyez sur Ctrl+C"
echo ""

uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload 
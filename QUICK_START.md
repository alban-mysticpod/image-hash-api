# 🚀 Quick Start - Image Hash Template API

## ⚡ Démarrage en 30 secondes

```bash
# 1. Installer les dépendances
pip install fastapi uvicorn imagehash pillow python-multipart

# 2. Démarrer l'API
./start_local.sh
# OU: uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload

# 3. Ouvrir http://localhost:8080/docs dans votre navigateur
```

## 🎯 Test Rapide

```bash
# Démarrer l'API dans un terminal
./start_local.sh

# Dans un autre terminal, tester
python3 example_usage.py
```

## 📋 Commandes Essentielles

### Hasher une image
```bash
curl -X POST "http://localhost:8080/hash-image" \
  -F "file=@votre_image.jpg"
```

### Ajouter un template
```bash
curl -X POST "http://localhost:8080/add-template" \
  -F "name=Mon Template" \
  -F "hash_value=auto" \
  -F "reference_image_path=auto" \
  -F "file=@template.jpg"
```

### Chercher un template
```bash
curl -X POST "http://localhost:8080/match-template" \
  -d "hash_value=votre_hash_ici&threshold=5"
```

## 📁 Structure du Projet

```
image-hash-api/
├── api/main.py              # 🌟 API FastAPI
├── utils/
│   ├── hash_utils.py        # 🔢 Fonctions de hashing
│   └── template_manager.py  # 📊 Gestionnaire de templates
├── data/templates.json      # 💾 Stockage des templates
├── README.md               # 📖 Documentation complète
├── example_usage.py        # 🧪 Exemple d'utilisation
├── test_api.py            # 🧪 Tests automatiques
├── start_local.sh         # 🚀 Script de démarrage (dev)
└── render.yaml            # ☁️ Config déploiement Render
```

## 🎪 Fonctionnalités

✅ **Hash perceptuel (pHash)** - Reconnaît les images similaires  
✅ **Templates JSON** - Stockage simple et portable  
✅ **Distance de Hamming** - Comparaison précise  
✅ **API REST complète** - Tous les endpoints nécessaires  
✅ **Documentation Swagger** - Interface interactive  
✅ **Tests automatiques** - Validation du fonctionnement  
✅ **Exemples complets** - Code prêt à l'emploi  

## 🎛️ Paramètres Importants

- **Seuil par défaut**: 5 (distance de Hamming)
- **Port par défaut**: 8080 (local) / $PORT (Render)
- **Formats supportés**: JPEG, PNG, BMP, TIFF, WebP
- **Taille max**: 16MB par fichier

---

**Prêt à reconnaître vos templates d'images ! 🎉** 
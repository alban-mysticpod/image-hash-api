# Image Hash Template API

FastAPI API for automatic image template recognition via perceptual hashing (pHash).

## 🎯 Objective

This API allows you to:
- Calculate perceptual hash (pHash) of images
- Store image templates with their hashes
- Automatically identify matching template for new images
- Compare images by visual similarity

## 🚀 Installation and Startup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API

```bash
# Method 1: Directly with Python
python api/main.py

# Method 2: With uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload

# Method 3: In background
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload &
```

The API will be accessible at `http://localhost:8080`

### 3. Interactive documentation

Access Swagger UI documentation: `http://localhost:8080/docs`

## 📋 Available Endpoints

### 🔍 **GET /** - API Information
Returns general information and list of endpoints.

### 🖼️ **POST /hash-image** - Hash an image

Calculate pHash of a sent image.

**Usage with curl:**
```bash
curl -X POST "http://localhost:8080/hash-image" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg"
```

**Example response:**
```json
{
  "success": true,
  "hash": "ff00aaff00aaff00",
  "filename": "mockup_template.jpg",
  "content_type": "image/jpeg",
  "file_size": 125432,
  "generated_at": "2024-01-15T10:30:45.123456"
}
```

### 🎯 **POST /match-template** - Find matching template

Find the most similar template to a given hash.

**Usage with curl:**
```bash
curl -X POST "http://localhost:8080/match-template" \
  -H "accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "hash_value=ff00aaff00aaff00&threshold=5"
```

**Response if match found:**
```json
{
  "success": true,
  "match_found": true,
  "template": {
    "id": 1,
    "name": "Template iPhone Mockup",
    "hash": "ff00aaff00aaff01",
    "reference_image_path": "templates/iphone_mockup.jpg",
    "created_at": "2024-01-15T09:00:00",
    "usage_count": 5
  },
  "hamming_distance": 1,
  "similarity_score": 95
}
```

**Réponse si aucun match :**
```json
{
  "success": true,
  "match_found": false,
  "message": "Aucun template trouvé avec une distance < 5",
  "suggestions": {
    "create_new_template": "POST /add-template avec ce hash: ff00aaff00aaff00",
    "try_higher_threshold": "Essayez avec un seuil plus élevé"
  }
}
```

### ➕ **POST /add-template** - Ajouter un nouveau template

Ajoute un template dans le fichier `templates.json`.

**Méthode 1: Avec hash manuel**
```bash
curl -X POST "http://localhost:8080/add-template" \
  -H "accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Mon Template&hash_value=ff00aaff00aaff00&reference_image_path=/path/to/image.jpg"
```

**Méthode 2: Avec fichier image (hash auto-calculé)**
```bash
curl -X POST "http://localhost:8080/add-template" \
  -H "accept: application/json" \
  -F "name=Mon Template" \
  -F "hash_value=auto" \
  -F "reference_image_path=auto" \
  -F "file=@template_image.jpg"
```

### 📋 **GET /templates** - Lister tous les templates

```bash
curl -X GET "http://localhost:8080/templates"
```

### 🔍 **GET /templates/{template_id}** - Récupérer un template

```bash
curl -X GET "http://localhost:8080/templates/1"
```

### 🗑️ **DELETE /templates/{template_id}** - Supprimer un template

```bash
curl -X DELETE "http://localhost:8080/templates/1"
```

### ⚖️ **POST /compare-hashes** - Comparer deux hash

```bash
curl -X POST "http://localhost:8080/compare-hashes" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "hash1=ff00aaff00aaff00&hash2=ff00aaff00aaff01"
```

## 📁 Structure du Projet

```
image-hash-api/
├── api/
│   ├── __init__.py
│   └── main.py              # API FastAPI principale
├── utils/
│   ├── __init__.py
│   ├── hash_utils.py        # Fonctions de hashing et distance
│   └── template_manager.py  # Gestion des templates
├── data/
│   ├── templates.json       # Stockage des templates
│   └── uploads/            # Images uploadées (créé automatiquement)
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```

## 🔧 Utilisation Programmatique

### Exemple complet en Python

```python
import requests

# 1. Hasher une image
with open("mon_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8080/hash-image",
        files={"file": f}
    )
    hash_result = response.json()
    image_hash = hash_result["hash"]

# 2. Chercher un template correspondant
response = requests.post(
    "http://localhost:8080/match-template",
    data={"hash_value": image_hash, "threshold": 5}
)
match_result = response.json()

if match_result["match_found"]:
    print(f"Template trouvé: {match_result['template']['name']}")
    print(f"Similarité: {match_result['similarity_score']}%")
else:
    # 3. Ajouter comme nouveau template
    with open("mon_image.jpg", "rb") as f:
        response = requests.post(
            "http://localhost:8080/add-template",
            data={
                "name": "Nouveau Template",
                "hash_value": "auto",
                "reference_image_path": "auto"
            },
            files={"file": f}
        )
    print("Nouveau template créé")
```

## 📊 Algorithme de Similarité

- **pHash (Perceptual Hash)** : Génère un hash de 64 bits basé sur la structure visuelle de l'image
- **Distance de Hamming** : Compte le nombre de bits différents entre deux hash
- **Seuil par défaut** : Distance < 5 considérée comme "même template"
- **Score de similarité** : `max(0, 100 - (distance * 5))`

## 🎛️ Configuration

### Seuils de similarité recommandés :
- **Distance < 3** : Images quasi-identiques
- **Distance < 5** : Même template avec variations mineures (défaut)
- **Distance < 10** : Templates similaires mais distincts
- **Distance > 15** : Templates différents

### Formats d'images supportés :
- JPEG / JPG
- PNG
- BMP
- TIFF
- WebP

## 🐛 Debugging

### Vérifier que l'API fonctionne :
```bash
curl http://localhost:8080/
```

### Tester avec une image simple :
```bash
# Télécharger une image de test
curl -o test.jpg "https://via.placeholder.com/300x200.jpg"

# La hasher
curl -X POST "http://localhost:8080/hash-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.jpg"
```

### Logs en temps réel :
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload --log-level debug
```

## 📝 Notes Techniques

- Les templates sont stockés dans `data/templates.json`
- Les images uploadées sont sauvées dans `data/uploads/`
- Le hash pHash est déterministe : même image = même hash
- L'API est thread-safe pour la lecture, mais les écritures sont séquentielles
- Taille maximale de fichier par défaut : 16MB (FastAPI)

## 🔮 Évolutions Futures

- [ ] Support de Supabase pour le stockage
- [ ] Clustering automatique (DBSCAN)
- [ ] API pour batch processing
- [ ] Métriques de performance
- [ ] Cache des hash calculés
- [ ] Support des formats vidéo (frames)

---

**API créée avec FastAPI + ImageHash + Pillow** 
# 🚀 Déploiement sur Render.com

## Étapes de déploiement

### 1. Créer un compte sur Render.com
- Allez sur https://render.com
- Connectez-vous avec votre compte GitHub

### 2. Créer un nouveau Web Service
1. Cliquez sur "New" > "Web Service"
2. Connectez votre repository GitHub `mystcai/vibe-coding`
3. Choisissez la branche `main`

### 3. Configuration du service

**Build & Deploy:**
- **Root Directory:** `image-hash-api`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Python Version:** 3.9.16
- **Environment Variables:**
  - `PYTHONPATH` = `.`

### 4. Déployer
- Cliquez sur "Create Web Service"
- Render va automatiquement déployer votre API
- Vous obtiendrez une URL publique comme `https://votre-app.onrender.com`

## ✅ Avantages de Render

- ✅ **Gratuit** pour les petits projets
- ✅ **Déploiement automatique** à chaque push
- ✅ **HTTPS** automatique
- ✅ **Support Python/FastAPI** natif
- ✅ **Logs** en temps réel
- ✅ **Pas de limite de build time**

## 🔗 URL après déploiement

Une fois déployé, votre API sera accessible sur :
```
https://votre-app-name.onrender.com
```

### Endpoints disponibles :
- `GET /` - Informations sur l'API
- `GET /docs` - Documentation Swagger
- `POST /hash-image` - Calculer hash d'une image
- `POST /match-template` - Trouver template correspondant
- `POST /match-template-from-url` - Match depuis une URL
- `POST /add-template-from-url` - Ajouter template depuis URL
- Et tous les autres endpoints...

## 🔍 Monitoring

- **Logs :** Accessible via le dashboard Render
- **Métriques :** CPU, RAM, requêtes par seconde
- **Health checks :** Endpoint `/` vérifié automatiquement 
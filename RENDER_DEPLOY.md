# Déploiement sur Render

## 🚀 Configuration automatique

Ce projet est configuré pour un déploiement automatique sur Render via le fichier `render.yaml`.

## 📋 Fichiers de démarrage

- **`render.yaml`** : Configuration de production pour Render (utilisé automatiquement)
- **`start_local.sh`** : Script de démarrage pour développement local uniquement
- **`Procfile`** : Configuration pour Heroku (si besoin)

## ⚙️ Configuration Render

Le `render.yaml` configure :

```yaml
startCommand: python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**Points importants :**
- ✅ `--host 0.0.0.0` : Bind sur toutes les interfaces (requis par Render)
- ✅ `--port $PORT` : Utilise le port dynamique fourni par Render
- ✅ Pas de `--reload` : Mode production (pas de rechargement automatique)

## 🔧 Déploiement

1. **Push vers GitHub** :
   ```bash
   git push origin master
   ```

2. **Sur Render Dashboard** :
   - Le déploiement démarre automatiquement
   - Vérifiez les logs pour confirmer le démarrage
   - Attendez le message "Your service is live"

3. **Vérifier le déploiement** :
   ```bash
   curl https://VOTRE-URL.onrender.com/
   ```

## 🐛 Troubleshooting

### Erreur "No open ports detected on 0.0.0.0"

**Cause** : L'application ne bind pas sur `0.0.0.0` ou n'utilise pas `$PORT`.

**Solution** : 
- ✅ Vérifiez que `render.yaml` contient `--host 0.0.0.0 --port $PORT`
- ✅ Supprimez/renommez `start.sh` s'il existe (Render le détecte automatiquement)
- ✅ Assurez-vous qu'aucun fichier ne force le binding sur `127.0.0.1`

### L'application démarre en mode `--reload`

**Cause** : Un fichier `start.sh` existe et est détecté par Render.

**Solution** : Renommez `start.sh` en `start_local.sh` pour le développement local uniquement.

## 📱 Développement local

Pour développer localement :

```bash
./start_local.sh
```

Ou directement :

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
```

## 🔗 URLs importantes

- **Documentation API** : `https://VOTRE-URL.onrender.com/docs`
- **Health Check** : `https://VOTRE-URL.onrender.com/`
- **Render Dashboard** : https://dashboard.render.com/

## 📊 Variables d'environnement

Les variables suivantes sont configurées automatiquement :

- `PYTHON_VERSION`: 3.9.16
- `PYTHONPATH`: /opt/render/project/src
- `PORT`: Fourni automatiquement par Render

## 🎯 Commandes utiles

### Tester la configuration localement
```bash
python3 -c "from api.main import app; print('✅ API OK')"
```

### Vérifier les imports
```bash
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8080
```


# Guide de Contribution

Merci de votre intérêt pour contribuer à ce projet ! Voici quelques lignes directrices pour vous aider à démarrer.

## Configuration de l'Environnement

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/vibe-coding.git
cd vibe-coding/mockup-feature
```

2. Configurez le backend :
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Sur Windows : .\venv\Scripts\activate
pip install -r requirements.txt
python download_weights.py
```

3. Configurez le frontend :
```bash
cd ..
npm install
```

4. Créez un fichier `.env` basé sur `.env.example` et ajoutez vos clés API.

## Démarrage du Projet

1. Démarrez le backend :
```bash
cd backend
source venv/bin/activate
python -m uvicorn app:app --reload
```

2. Dans un autre terminal, démarrez le frontend :
```bash
npm run dev
```

## Structure du Projet

- `backend/` : API FastAPI avec ZoeDepth
- `src/` : Frontend React/Vite
- `weights/` : Poids des modèles (téléchargés automatiquement)

## Processus de Contribution

1. Créez une branche pour votre fonctionnalité :
```bash
git checkout -b feature/nom-de-la-fonctionnalite
```

2. Faites vos modifications et testez-les.

3. Committez vos changements :
```bash
git add .
git commit -m "Description claire des changements"
```

4. Poussez votre branche :
```bash
git push origin feature/nom-de-la-fonctionnalite
```

5. Ouvrez une Pull Request sur GitHub.

## Standards de Code

- Utilisez des noms de variables et de fonctions descriptifs
- Commentez votre code quand nécessaire
- Suivez les conventions PEP 8 pour Python
- Utilisez ESLint pour JavaScript/TypeScript

## Tests

- Testez vos changements localement avant de soumettre une PR
- Assurez-vous que tous les tests existants passent
- Ajoutez des tests pour les nouvelles fonctionnalités

## Questions ?

Si vous avez des questions, n'hésitez pas à ouvrir une issue sur GitHub. 
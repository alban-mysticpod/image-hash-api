import os
import uvicorn

if __name__ == "__main__":
    # S'assurer que nous sommes dans le dossier backend
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Démarrer le serveur
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 
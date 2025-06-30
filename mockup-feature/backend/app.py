import os
import sys

# Ajouter le dossier parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import torch
import numpy as np
from TilingZoeDepth_GUI.zoedepth.models.zoedepth.zoedepth_v1 import ZoeDepth
from TilingZoeDepth_GUI.zoedepth.utils.config import get_config

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",  # Vite default port
        "http://localhost:8000",  # Backend server
        "http://127.0.0.1:8000"   # Backend server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration globale
TILE_SIZE = 512
OVERLAP = 64
MODEL = None

@app.on_event("startup")
async def startup_event():
    global MODEL
    try:
        # Charger le modèle ZoeDepth
        conf = get_config("zoedepth", "infer")
        MODEL = ZoeDepth.build_from_config(conf)
        MODEL.eval()
        if torch.cuda.is_available():
            MODEL = MODEL.cuda()
        print("Modèle ZoeDepth chargé avec succès")
    except Exception as e:
        print(f"Erreur lors du chargement du modèle : {str(e)}")

def process_tile(tile, model):
    """Traite une tuile d'image avec le modèle."""
    with torch.no_grad():
        if torch.cuda.is_available():
            tile = tile.cuda()
        depth = model.infer(tile)
        if torch.cuda.is_available():
            depth = depth.cpu()
        return depth.numpy()

@app.post("/generate-depth")
async def generate_depth(file: UploadFile):
    try:
        # Lire l'image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Obtenir les dimensions
        width, height = image.size
        
        # Initialiser la carte de profondeur
        depth_map = np.zeros((height, width), dtype=np.float32)
        
        # Traiter l'image par tuiles
        for y in range(0, height, TILE_SIZE - OVERLAP):
            for x in range(0, width, TILE_SIZE - OVERLAP):
                # Extraire la tuile
                tile = image.crop((
                    x, 
                    y,
                    min(x + TILE_SIZE, width),
                    min(y + TILE_SIZE, height)
                ))
                
                # Traiter la tuile
                tile_depth = process_tile(tile, MODEL)
                
                # Fusionner la tuile dans la carte de profondeur finale
                y_end = min(y + tile.height, height)
                x_end = min(x + tile.width, width)
                depth_map[y:y_end, x:x_end] = tile_depth[:y_end-y, :x_end-x]
        
        # Convertir en PNG 16 bits
        depth_map = (depth_map * 65535).astype(np.uint16)
        output = Image.fromarray(depth_map)
        
        # Sauvegarder en mémoire
        output_bytes = io.BytesIO()
        output.save(output_bytes, format='PNG')
        output_bytes.seek(0)
        
        return Response(
            content=output_bytes.read(),
            media_type="image/png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
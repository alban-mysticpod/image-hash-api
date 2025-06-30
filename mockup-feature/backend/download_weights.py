import torch
import os

def download_weights():
    # Créer le dossier pour les poids si nécessaire
    weights_dir = "weights"
    os.makedirs(weights_dir, exist_ok=True)
    
    # Télécharger les poids depuis le hub torch
    model = torch.hub.load("isl-org/ZoeDepth", "ZoeD_NK", pretrained=True)
    
    # Sauvegarder les poids localement
    torch.save(model.state_dict(), os.path.join(weights_dir, "ZoeD_NK.pt"))
    
    print("Poids téléchargés avec succès !")

if __name__ == "__main__":
    download_weights() 
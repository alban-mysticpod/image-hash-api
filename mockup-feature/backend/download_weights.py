import torch
import os

def download_weights():
    # Create weights folder if necessary
    weights_dir = "weights"
    os.makedirs(weights_dir, exist_ok=True)
    
    # Download weights from torch hub
    model = torch.hub.load("isl-org/ZoeDepth", "ZoeD_NK", pretrained=True)
    
    # Save weights locally
    torch.save(model.state_dict(), os.path.join(weights_dir, "ZoeD_NK.pt"))
    
    print("Weights downloaded successfully!")

if __name__ == "__main__":
    download_weights() 
#!/usr/bin/env python3
"""
Example usage of the Image Hash Template API.

This script shows how to use the API to:
1. Hash an image
2. Add a template
3. Search for a matching template
"""
import requests
import json
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:8080"

def create_sample_image(width=300, height=200, color="red", save_path=None):
    """Create a sample image."""
    img = Image.new('RGB', (width, height), color)
    if save_path:
        img.save(save_path, "JPEG")
    return img

def example_workflow():
    """Démontre un workflow complet."""
    print("🎯 Exemple d'utilisation de l'API Image Hash Template")
    print("=" * 60)
    
    try:
        # 1. Vérifier que l'API est accessible
        print("\n1️⃣  Vérification de l'API...")
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code != 200:
            print("❌ L'API n'est pas accessible. Démarrez-la avec: uvicorn api.main:app --reload")
            return
        print("✅ API accessible")
        
        # 2. Créer une image d'exemple
        print("\n2️⃣  Création d'une image d'exemple...")
        create_sample_image(300, 200, "blue", "sample_mockup.jpg")
        print("✅ Image créée: sample_mockup.jpg")
        
        # 3. Hasher l'image
        print("\n3️⃣  Calcul du hash de l'image...")
        with open("sample_mockup.jpg", "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/hash-image",
                files={"file": f}
            )
        
        if response.status_code == 200:
            hash_result = response.json()
            image_hash = hash_result["hash"]
            print(f"✅ Hash calculé: {image_hash}")
        else:
            print(f"❌ Erreur lors du hashing: {response.text}")
            return
        
        # 4. Ajouter comme nouveau template
        print("\n4️⃣  Ajout comme nouveau template...")
        response = requests.post(
            f"{API_BASE_URL}/add-template",
            data={
                "name": "Template Mockup Bleu",
                "hash_value": image_hash,
                "reference_image_path": "sample_mockup.jpg"
            }
        )
        
        if response.status_code == 200:
            template_result = response.json()
            template_id = template_result["template"]["id"]
            print(f"✅ Template ajouté avec l'ID: {template_id}")
        else:
            print(f"❌ Erreur lors de l'ajout: {response.text}")
            return
        
        # 5. Créer une image similaire pour tester le matching
        print("\n5️⃣  Création d'une image similaire...")
        create_sample_image(300, 200, "lightblue", "similar_mockup.jpg")
        
        # 6. Hasher la nouvelle image
        print("\n6️⃣  Hash de l'image similaire...")
        with open("similar_mockup.jpg", "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/hash-image",
                files={"file": f}
            )
        
        if response.status_code == 200:
            similar_hash = response.json()["hash"]
            print(f"✅ Hash de l'image similaire: {similar_hash}")
        else:
            print(f"❌ Erreur: {response.text}")
            return
        
        # 7. Chercher le template correspondant
        print("\n7️⃣  Recherche du template correspondant...")
        response = requests.post(
            f"{API_BASE_URL}/match-template",
            data={
                "hash_value": similar_hash,
                "threshold": 10  # Seuil plus élevé pour des images de couleurs similaires
            }
        )
        
        if response.status_code == 200:
            match_result = response.json()
            if match_result["match_found"]:
                print(f"✅ Template trouvé: {match_result['template']['name']}")
                print(f"   Distance de Hamming: {match_result['hamming_distance']}")
                print(f"   Score de similarité: {match_result['similarity_score']}%")
            else:
                print("❌ Aucun template correspondant trouvé")
        else:
            print(f"❌ Erreur lors de la recherche: {response.text}")
            return
        
        # 8. Lister tous les templates
        print("\n8️⃣  Liste de tous les templates...")
        response = requests.get(f"{API_BASE_URL}/templates")
        
        if response.status_code == 200:
            templates_result = response.json()
            print(f"✅ {templates_result['count']} template(s) trouvé(s):")
            for template in templates_result['templates']:
                print(f"   - {template['name']} (ID: {template['id']}, Usage: {template['usage_count']})")
        else:
            print(f"❌ Erreur: {response.text}")
        
        # 9. Comparer les deux hashes directement
        print("\n9️⃣  Comparaison directe des hashes...")
        response = requests.post(
            f"{API_BASE_URL}/compare-hashes",
            data={
                "hash1": image_hash,
                "hash2": similar_hash
            }
        )
        
        if response.status_code == 200:
            comparison = response.json()
            print(f"✅ Comparaison effectuée:")
            print(f"   Distance de Hamming: {comparison['hamming_distance']}")
            print(f"   Score de similarité: {comparison['similarity_score']}%")
            print(f"   Considérés comme similaires: {'Oui' if comparison['are_similar'] else 'Non'}")
        else:
            print(f"❌ Erreur: {response.text}")
        
        print("\n🎉 Example completed successfully!")
        print("\n💡 Tips:")
        print("   - Images with similar colors will have similar hashes")
        print("   - Adjust threshold according to your needs (5 by default)")
        print("   - Check interactive docs at http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Unable to connect to API")
        print("💡 Start API with: uvicorn api.main:app --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    example_workflow() 
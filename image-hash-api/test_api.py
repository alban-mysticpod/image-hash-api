#!/usr/bin/env python3
"""
Test script for the Image Hash Template API.
"""
import requests
import json
import os
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:8080"

def create_test_image(width=200, height=200, color="red"):
    """Create a simple test image."""
    img = Image.new('RGB', (width, height), color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_api_health():
    """Test de santé de l'API."""
    print("🏥 Test de santé de l'API...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API inaccessible - Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("💡 Assurez-vous que l'API est démarrée avec: uvicorn api.main:app --reload")
        return False

def test_hash_image():
    """Test de hashing d'image."""
    print("\n🔢 Test de hashing d'image...")
    
    # Créer une image de test
    test_img = create_test_image(200, 200, "blue")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/hash-image",
            files={"file": ("test.jpg", test_img, "image/jpeg")}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hash calculé: {result['hash']}")
            return result['hash']
        else:
            print(f"❌ Erreur lors du hashing - Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception lors du hashing: {e}")
        return None

def test_add_template(hash_value):
    """Test d'ajout de template."""
    print("\n➕ Test d'ajout de template...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/add-template",
            data={
                "name": "Template Test Blue",
                "hash_value": hash_value,
                "reference_image_path": "/test/blue_template.jpg"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Template ajouté: {result['template']['name']}")
            return result['template']['id']
        else:
            print(f"❌ Erreur lors de l'ajout - Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception lors de l'ajout: {e}")
        return None

def test_match_template(hash_value):
    """Test de matching de template."""
    print("\n🎯 Test de matching de template...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/match-template",
            data={
                "hash_value": hash_value,
                "threshold": 5
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['match_found']:
                print(f"✅ Match trouvé: {result['template']['name']}")
                print(f"   Distance: {result['hamming_distance']}")
                print(f"   Similarité: {result['similarity_score']}%")
            else:
                print("❌ Aucun match trouvé")
            return result
        else:
            print(f"❌ Erreur lors du matching - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception lors du matching: {e}")
        return None

def test_list_templates():
    """Test de listage des templates."""
    print("\n📋 Test de listage des templates...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/templates")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['count']} template(s) trouvé(s)")
            for template in result['templates']:
                print(f"   - {template['name']} (ID: {template['id']})")
            return result['templates']
        else:
            print(f"❌ Erreur lors du listage - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception lors du listage: {e}")
        return None

def test_compare_hashes():
    """Test de comparaison de hashes."""
    print("\n⚖️ Test de comparaison de hashes...")
    
    # Créer deux images similaires
    img1 = create_test_image(200, 200, "red")
    img2 = create_test_image(200, 200, "blue")
    
    try:
        # Hasher la première image
        response1 = requests.post(
            f"{API_BASE_URL}/hash-image",
            files={"file": ("test1.jpg", img1, "image/jpeg")}
        )
        hash1 = response1.json()['hash']
        
        # Hasher la deuxième image
        response2 = requests.post(
            f"{API_BASE_URL}/hash-image",
            files={"file": ("test2.jpg", img2, "image/jpeg")}
        )
        hash2 = response2.json()['hash']
        
        # Comparer les hashes
        response = requests.post(
            f"{API_BASE_URL}/compare-hashes",
            data={
                "hash1": hash1,
                "hash2": hash2
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Comparaison effectuée")
            print(f"   Hash 1: {result['hash1']}")
            print(f"   Hash 2: {result['hash2']}")
            print(f"   Distance: {result['hamming_distance']}")
            print(f"   Similarité: {result['similarity_score']}%")
            print(f"   Similaires: {result['are_similar']}")
            return True
        else:
            print(f"❌ Erreur lors de la comparaison - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception lors de la comparaison: {e}")
        return False

def run_complete_test():
    """Lance tous les tests."""
    print("🚀 Lancement des tests complets de l'API Image Hash Template\n")
    
    # Test 1: Santé de l'API
    if not test_api_health():
        return False
    
    # Test 2: Hash d'image
    hash_value = test_hash_image()
    if not hash_value:
        return False
    
    # Test 3: Ajout de template
    template_id = test_add_template(hash_value)
    if not template_id:
        return False
    
    # Test 4: Matching de template
    match_result = test_match_template(hash_value)
    if not match_result:
        return False
    
    # Test 5: Listage des templates
    templates = test_list_templates()
    if templates is None:
        return False
    
    # Test 6: Comparaison de hashes
    if not test_compare_hashes():
        return False
    
    print("\n🎉 Tous les tests sont passés avec succès !")
    print("\n📊 Résumé:")
    print("   ✅ API accessible")
    print("   ✅ Hashing d'images fonctionnel")
    print("   ✅ Ajout de templates fonctionnel")
    print("   ✅ Matching de templates fonctionnel")
    print("   ✅ Listage des templates fonctionnel")
    print("   ✅ Comparaison de hashes fonctionnelle")
    
    return True

if __name__ == "__main__":
    run_complete_test() 
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
    """API health test."""
    print("🏥 API health test...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_hash_image():
    """Image hashing test."""
    print("\n🔢 Image hashing test...")
    
    # Create test image
    test_img = create_test_image(200, 200, "blue")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/hash-image",
            files={"file": ("test.jpg", test_img, "image/jpeg")}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hash calculated: {result['hash']}")
            return result['hash']
        else:
            print(f"❌ Error during hashing - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception during hashing: {e}")
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
            print(f"❌ Error during addition - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception during addition: {e}")
        return None

def test_match_template(hash_value):
    """Template matching test."""
    print("\n🎯 Template matching test...")
    
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
                print(f"✅ Match found: {result['template']['name']}")
                print(f"   Distance: {result['hamming_distance']}")
                print(f"   Similarity: {result['similarity_score']}%")
            else:
                print("❌ No match found")
            return result
        else:
            print(f"❌ Error during matching - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception during matching: {e}")
        return None

def test_list_templates():
    """Template listing test."""
    print("\n📋 Template listing test...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/templates")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['count']} template(s) found")
            for template in result['templates']:
                print(f"   - {template['name']} (ID: {template['id']})")
            return result['templates']
        else:
            print(f"❌ Error during listing - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception during listing: {e}")
        return None

def test_compare_hashes():
    """Hash comparison test."""
    print("\n⚖️ Hash comparison test...")
    
    # Create two similar images
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
            print(f"✅ Comparison completed")
            print(f"   Hash 1: {result['hash1']}")
            print(f"   Hash 2: {result['hash2']}")
            print(f"   Distance: {result['hamming_distance']}")
            print(f"   Similarity: {result['similarity_score']}%")
            print(f"   Similar: {result['are_similar']}")
            return True
        else:
            print(f"❌ Error during comparison - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception during comparison: {e}")
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
    
    # Test 6: Hash comparison
    if not test_compare_hashes():
        return False
    
    print("\n🎉 All tests passed successfully!")
    print("\n📊 Summary:")
    print("   ✅ API accessible")
    print("   ✅ Image hashing functional")
    print("   ✅ Template addition functional")
    print("   ✅ Template matching functional")
    print("   ✅ Template listing functional")
    print("   ✅ Hash comparison functional")
    
    return True

if __name__ == "__main__":
    run_complete_test() 
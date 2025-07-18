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
    """Demonstrates a complete workflow."""
    print("🎯 Image Hash Template API Usage Example")
    print("=" * 60)
    
    try:
        # 1. Check that API is accessible
        print("\n1️⃣  API verification...")
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code != 200:
            print("❌ API is not accessible. Start it with: uvicorn api.main:app --reload")
            return
        print("✅ API accessible")
        
        # 2. Create example image
        print("\n2️⃣  Creating example image...")
        create_sample_image(300, 200, "blue", "sample_mockup.jpg")
        print("✅ Image created: sample_mockup.jpg")
        
        # 3. Hash the image
        print("\n3️⃣  Calculating image hash...")
        with open("sample_mockup.jpg", "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/hash-image",
                files={"file": f}
            )
        
        if response.status_code == 200:
            hash_result = response.json()
            image_hash = hash_result["hash"]
            print(f"✅ Hash calculated: {image_hash}")
        else:
            print(f"❌ Error during hashing: {response.text}")
            return
        
        # 4. Add as new template
        print("\n4️⃣  Adding as new template...")
        response = requests.post(
            f"{API_BASE_URL}/add-template",
            data={
                "name": "Blue Mockup Template",
                "hash_value": image_hash,
                "reference_image_path": "sample_mockup.jpg"
            }
        )
        
        if response.status_code == 200:
            template_result = response.json()
            template_id = template_result["template"]["id"]
            print(f"✅ Template added with ID: {template_id}")
        else:
            print(f"❌ Error during addition: {response.text}")
            return
        
        # 5. Create similar image to test matching
        print("\n5️⃣  Creating similar image...")
        create_sample_image(300, 200, "lightblue", "similar_mockup.jpg")
        
        # 6. Hash the new image
        print("\n6️⃣  Hashing similar image...")
        with open("similar_mockup.jpg", "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/hash-image",
                files={"file": f}
            )
        
        if response.status_code == 200:
            similar_hash = response.json()["hash"]
            print(f"✅ Similar image hash: {similar_hash}")
        else:
            print(f"❌ Error: {response.text}")
            return
        
        # 7. Search for matching template
        print("\n7️⃣  Searching for matching template...")
        response = requests.post(
            f"{API_BASE_URL}/match-template",
            data={
                "hash_value": similar_hash,
                "threshold": 10  # Higher threshold for similar color images
            }
        )
        
        if response.status_code == 200:
            match_result = response.json()
            if match_result["match_found"]:
                print(f"✅ Template found: {match_result['template']['name']}")
                print(f"   Hamming distance: {match_result['hamming_distance']}")
                print(f"   Similarity score: {match_result['similarity_score']}%")
            else:
                print("❌ No matching template found")
        else:
            print(f"❌ Error during search: {response.text}")
            return
        
        # 8. List all templates
        print("\n8️⃣  Listing all templates...")
        response = requests.get(f"{API_BASE_URL}/templates")
        
        if response.status_code == 200:
            templates_result = response.json()
            print(f"✅ {templates_result['count']} template(s) found:")
            for template in templates_result['templates']:
                print(f"   - {template['name']} (ID: {template['id']}, Usage: {template['usage_count']})")
        else:
            print(f"❌ Error: {response.text}")
        
        # 9. Compare the two hashes directly
        print("\n9️⃣  Direct hash comparison...")
        response = requests.post(
            f"{API_BASE_URL}/compare-hashes",
            data={
                "hash1": image_hash,
                "hash2": similar_hash
            }
        )
        
        if response.status_code == 200:
            comparison = response.json()
            print(f"✅ Comparison completed:")
            print(f"   Hamming distance: {comparison['hamming_distance']}")
            print(f"   Similarity score: {comparison['similarity_score']}%")
            print(f"   Considered similar: {'Yes' if comparison['are_similar'] else 'No'}")
        else:
            print(f"❌ Error: {response.text}")
        
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
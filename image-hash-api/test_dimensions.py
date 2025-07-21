#!/usr/bin/env python3
"""
Test script for image dimension extraction functionality.
"""
import requests
import json
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:8083"

def create_test_image(width=300, height=200, color="blue"):
    """Create a test image with specific dimensions."""
    img = Image.new('RGB', (width, height), color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_api_connectivity():
    """Test if API is accessible."""
    print("🔗 Testing API connectivity...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is accessible")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        return False

def test_image_dimensions_endpoint():
    """Test the /image-dimensions endpoint."""
    print("\n📏 Testing /image-dimensions endpoint...")
    
    # Create test image with known dimensions
    test_width, test_height = 400, 300
    test_img = create_test_image(test_width, test_height, "red")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/image-dimensions",
            files={"file": ("test.jpg", test_img, "image/jpeg")}
        )
        
        if response.status_code == 200:
            result = response.json()
            returned_width = result.get("width")
            returned_height = result.get("height")
            
            if returned_width == test_width and returned_height == test_height:
                print(f"✅ Dimensions correct: {returned_width}x{returned_height}")
                return True
            else:
                print(f"❌ Wrong dimensions: expected {test_width}x{test_height}, got {returned_width}x{returned_height}")
                return False
        else:
            print(f"❌ Error - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_hash_image_with_dimensions():
    """Test that /hash-image now includes dimensions."""
    print("\n🔢 Testing /hash-image endpoint with dimensions...")
    
    # Create test image with known dimensions
    test_width, test_height = 250, 150
    test_img = create_test_image(test_width, test_height, "green")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/hash-image",
            files={"file": ("test.jpg", test_img, "image/jpeg")}
        )
        
        if response.status_code == 200:
            result = response.json()
            has_hash = "hash" in result
            has_width = "width" in result
            has_height = "height" in result
            returned_width = result.get("width")
            returned_height = result.get("height")
            
            if has_hash and has_width and has_height:
                if returned_width == test_width and returned_height == test_height:
                    print(f"✅ Hash with dimensions: {result['hash']}, {returned_width}x{returned_height}")
                    return True
                else:
                    print(f"❌ Wrong dimensions: expected {test_width}x{test_height}, got {returned_width}x{returned_height}")
                    return False
            else:
                missing = []
                if not has_hash: missing.append("hash")
                if not has_width: missing.append("width")
                if not has_height: missing.append("height")
                print(f"❌ Missing fields: {', '.join(missing)}")
                return False
        else:
            print(f"❌ Error - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_image_dimensions_from_url():
    """Test the /image-dimensions-from-url endpoint."""
    print("\n🌐 Testing /image-dimensions-from-url endpoint...")
    
    # Use a test image URL (placeholder service)
    test_url = "https://via.placeholder.com/500x300.jpg"
    expected_width, expected_height = 500, 300
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/image-dimensions-from-url",
            data={"image_url": test_url}
        )
        
        if response.status_code == 200:
            result = response.json()
            returned_width = result.get("width")
            returned_height = result.get("height")
            
            if returned_width == expected_width and returned_height == expected_height:
                print(f"✅ URL dimensions correct: {returned_width}x{returned_height}")
                return True
            else:
                print(f"❌ Wrong dimensions: expected {expected_width}x{expected_height}, got {returned_width}x{returned_height}")
                return False
        else:
            print(f"❌ Error - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_match_template_from_url_with_dimensions():
    """Test that /match-template-from-url now includes dimensions."""
    print("\n🎯 Testing /match-template-from-url with dimensions...")
    
    # Use a test image URL
    test_url = "https://via.placeholder.com/320x240.jpg"
    expected_width, expected_height = 320, 240
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/match-template-from-url",
            data={"image_url": test_url, "threshold": 5}
        )
        
        if response.status_code == 200:
            result = response.json()
            image_info = result.get("image_info", {})
            returned_width = image_info.get("width")
            returned_height = image_info.get("height")
            
            if returned_width == expected_width and returned_height == expected_height:
                print(f"✅ Match template includes dimensions: {returned_width}x{returned_height}")
                return True
            else:
                print(f"❌ Wrong dimensions in image_info: expected {expected_width}x{expected_height}, got {returned_width}x{returned_height}")
                return False
        else:
            print(f"❌ Error - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Image Dimension Extraction Functionality")
    print("=" * 60)
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("\n❌ Cannot continue tests - API is not accessible")
        print("Make sure to start the API with: cd image-hash-api && python3 main.py")
        return
    
    # Run all tests
    tests = [
        test_image_dimensions_endpoint,
        test_hash_image_with_dimensions,
        test_image_dimensions_from_url,
        test_match_template_from_url_with_dimensions
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Image dimension extraction is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 
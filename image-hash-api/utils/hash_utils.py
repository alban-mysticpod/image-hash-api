"""
Utilities for image hashing and distance calculation.
"""
import imagehash
from PIL import Image
import os
import io
import io


def generate_phash(image_path: str) -> str:
    """
    Generate perceptual hash (pHash) of an image.
    
    Args:
        image_path (str): Path to image
        
    Returns:
        str: Perceptual hash as hexadecimal string
        
    Raises:
        FileNotFoundError: If image doesn't exist
        Exception: If image cannot be processed
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image {image_path} does not exist")
    
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Generate perceptual hash
            phash = imagehash.phash(img)
            return str(phash)
    except Exception as e:
        raise Exception(f"Error processing image {image_path}: {str(e)}")


def generate_phash_from_bytes(image_bytes: bytes) -> str:
    """
    Generate perceptual hash (pHash) from image bytes.
    
    Args:
        image_bytes (bytes): Binary image data
        
    Returns:
        str: Perceptual hash as hexadecimal string
        
    Raises:
        Exception: If image cannot be processed
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Generate perceptual hash
            phash = imagehash.phash(img)
            return str(phash)
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")


def hamming_distance(hash1: str, hash2: str) -> int:
    """
    Calculate Hamming distance between two hashes.
    
    Args:
        hash1 (str): First hash
        hash2 (str): Second hash
        
    Returns:
        int: Distance de Hamming (nombre de bits différents)
        
    Raises:
        ValueError: Si les hash n'ont pas la même longueur
    """
    if len(hash1) != len(hash2):
        raise ValueError("Les hash doivent avoir la même longueur")
    
    # Convertir les hash en objets ImageHash pour utiliser la méthode intégrée
    try:
        ihash1 = imagehash.hex_to_hash(hash1)
        ihash2 = imagehash.hex_to_hash(hash2)
        # Convertir le numpy.int64 en int Python standard pour éviter les erreurs de sérialisation JSON
        return int(ihash1 - ihash2)
    except Exception:
        # Fallback: calcul manuel bit par bit
        distance = 0
        for i in range(len(hash1)):
            if hash1[i] != hash2[i]:
                distance += 1
        return distance


def is_similar_template(hash1: str, hash2: str, threshold: int = 5) -> bool:
    """
    Determine if two hashes correspond to the same template.
    
    Args:
        hash1 (str): First hash
        hash2 (str): Second hash
        threshold (int): Similarity threshold (default: 5)
        
    Returns:
        bool: True if hashes are similar, False otherwise
    """
    try:
        distance = hamming_distance(hash1, hash2)
        return distance < threshold
    except Exception:
        return False 
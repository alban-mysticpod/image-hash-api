"""
Utilitaires pour le hashing d'images et calcul de distances.
"""
import imagehash
from PIL import Image
import os
import io
import io


def generate_phash(image_path: str) -> str:
    """
    Génère un hash perceptuel (pHash) d'une image.
    
    Args:
        image_path (str): Chemin vers l'image
        
    Returns:
        str: Hash perceptuel sous forme de chaîne hexadécimale
        
    Raises:
        FileNotFoundError: Si l'image n'existe pas
        Exception: Si l'image ne peut pas être traitée
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"L'image {image_path} n'existe pas")
    
    try:
        with Image.open(image_path) as img:
            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Générer le hash perceptuel
            phash = imagehash.phash(img)
            return str(phash)
    except Exception as e:
        raise Exception(f"Erreur lors du traitement de l'image {image_path}: {str(e)}")


def generate_phash_from_bytes(image_bytes: bytes) -> str:
    """
    Génère un hash perceptuel (pHash) à partir des bytes d'une image.
    
    Args:
        image_bytes (bytes): Données binaires de l'image
        
    Returns:
        str: Hash perceptuel sous forme de chaîne hexadécimale
        
    Raises:
        Exception: Si l'image ne peut pas être traitée
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Générer le hash perceptuel
            phash = imagehash.phash(img)
            return str(phash)
    except Exception as e:
        raise Exception(f"Erreur lors du traitement de l'image: {str(e)}")


def hamming_distance(hash1: str, hash2: str) -> int:
    """
    Calcule la distance de Hamming entre deux hash.
    
    Args:
        hash1 (str): Premier hash
        hash2 (str): Deuxième hash
        
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
        return ihash1 - ihash2
    except Exception:
        # Fallback: calcul manuel bit par bit
        distance = 0
        for i in range(len(hash1)):
            if hash1[i] != hash2[i]:
                distance += 1
        return distance


def is_similar_template(hash1: str, hash2: str, threshold: int = 5) -> bool:
    """
    Détermine si deux hash correspondent au même template.
    
    Args:
        hash1 (str): Premier hash
        hash2 (str): Deuxième hash
        threshold (int): Seuil de similarité (défaut: 5)
        
    Returns:
        bool: True si les hash sont similaires, False sinon
    """
    try:
        distance = hamming_distance(hash1, hash2)
        return distance < threshold
    except Exception:
        return False 
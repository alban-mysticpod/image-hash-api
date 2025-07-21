"""
Gestionnaire des templates d'images.
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class TemplateManager:
    """Gestionnaire pour les templates d'images."""
    
    def __init__(self, templates_file: str = "data/templates.json"):
        """
        Initialise le gestionnaire de templates.
        
        Args:
            templates_file (str): Chemin vers le fichier JSON des templates
        """
        self.templates_file = templates_file
        self._ensure_templates_file_exists()
    
    def _ensure_templates_file_exists(self):
        """Assure que le fichier templates.json existe."""
        if not os.path.exists(self.templates_file):
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
            
            # Créer le fichier avec une structure vide
            initial_data = {"templates": []}
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def load_templates(self) -> List[Dict]:
        """
        Charge les templates depuis le fichier JSON.
        
        Returns:
            List[Dict]: Liste des templates avec leurs informations
        """
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("templates", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erreur lors du chargement des templates: {e}")
            return []
    
    def save_template(self, name: str, hash_value: str, reference_image_path: str, 
                     crop_x: Optional[int] = None, crop_y: Optional[int] = None, 
                     crop_w: Optional[int] = None, crop_h: Optional[int] = None,
                     image_width: Optional[int] = None, image_height: Optional[int] = None) -> Dict:
        """
        Ajoute un nouveau template au fichier JSON.
        
        Args:
            name (str): Nom du template
            hash_value (str): Hash perceptuel du template
            reference_image_path (str): Chemin vers l'image de référence
            crop_x (Optional[int]): Position X du crop
            crop_y (Optional[int]): Position Y du crop
            crop_w (Optional[int]): Largeur du crop
            crop_h (Optional[int]): Hauteur du crop
            image_width (Optional[int]): Largeur de l'image originale
            image_height (Optional[int]): Hauteur de l'image originale
            
        Returns:
            Dict: Le template créé avec son ID et les ratios de crop
            
        Raises:
            ValueError: Si un template avec le même nom existe déjà
        """
        templates = self.load_templates()
        
        # Vérifier si un template avec ce nom existe déjà
        if any(t["name"] == name for t in templates):
            raise ValueError(f"Un template avec le nom '{name}' existe déjà")
        
        # Créer le nouveau template
        new_template = {
            "id": len(templates) + 1,
            "name": name,
            "hash": hash_value,
            "reference_image_path": reference_image_path,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        # Ajouter les coordonnées de cropping si fournies
        if crop_x is not None:
            new_template["crop_x"] = crop_x
        if crop_y is not None:
            new_template["crop_y"] = crop_y
        if crop_w is not None:
            new_template["crop_w"] = crop_w
        if crop_h is not None:
            new_template["crop_h"] = crop_h
            
        # Ajouter les dimensions de l'image si fournies
        if image_width is not None:
            new_template["image_width"] = image_width
        if image_height is not None:
            new_template["image_height"] = image_height
            
        # Calculer les ratios de crop si on a les dimensions ET les coordonnées de crop
        if (image_width is not None and image_height is not None and 
            crop_x is not None and crop_y is not None and 
            crop_w is not None and crop_h is not None):
            
            # Éviter la division par zéro
            if image_width > 0 and image_height > 0:
                new_template["crop_x_ratio"] = crop_x / image_width
                new_template["crop_y_ratio"] = crop_y / image_height
                new_template["crop_w_ratio"] = crop_w / image_width
                new_template["crop_h_ratio"] = crop_h / image_height
        
        # Ajouter à la liste
        templates.append(new_template)
        
        # Sauvegarder
        data = {"templates": templates}
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return new_template
    
    def find_template_by_hash(self, hash_value: str, threshold: int = 5) -> Optional[Dict]:
        """
        Trouve un template correspondant au hash donné.
        
        Args:
            hash_value (str): Hash à rechercher
            threshold (int): Seuil de distance de Hamming acceptable
            
        Returns:
            Optional[Dict]: Template correspondant ou None si aucun trouvé
        """
        from .hash_utils import hamming_distance
        
        templates = self.load_templates()
        best_match = None
        best_distance = float('inf')
        
        for template in templates:
            try:
                distance = hamming_distance(hash_value, template["hash"])
                if distance < threshold and distance < best_distance:
                    best_match = template
                    best_distance = distance
            except Exception as e:
                print(f"Erreur lors de la comparaison avec le template {template['name']}: {e}")
                continue
        
        # Incrémenter le compteur d'usage si un template est trouvé
        if best_match:
            self._increment_usage_count(best_match["id"])
        
        return best_match
    
    def _increment_usage_count(self, template_id: int):
        """Incrémente le compteur d'usage d'un template."""
        templates = self.load_templates()
        
        for template in templates:
            if template["id"] == template_id:
                template["usage_count"] = template.get("usage_count", 0) + 1
                break
        
        # Sauvegarder les modifications
        data = {"templates": templates}
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_template_by_id(self, template_id: int) -> Optional[Dict]:
        """
        Récupère un template par son ID.
        
        Args:
            template_id (int): ID du template
            
        Returns:
            Optional[Dict]: Template trouvé ou None
        """
        templates = self.load_templates()
        return next((t for t in templates if t["id"] == template_id), None)
    
    def get_template_by_name(self, name: str) -> Optional[Dict]:
        """
        Récupère un template par son nom.
        
        Args:
            name (str): Nom du template
            
        Returns:
            Optional[Dict]: Template trouvé ou None
        """
        templates = self.load_templates()
        return next((t for t in templates if t["name"] == name), None)
    
    def list_templates(self) -> List[Dict]:
        """
        Liste tous les templates avec leurs statistiques.
        
        Returns:
            List[Dict]: Liste des templates
        """
        return self.load_templates()
    
    def delete_template(self, template_id: int) -> bool:
        """
        Supprime un template par son ID.
        
        Args:
            template_id (int): ID du template à supprimer
            
        Returns:
            bool: True si supprimé, False si non trouvé
        """
        templates = self.load_templates()
        initial_count = len(templates)
        
        templates = [t for t in templates if t["id"] != template_id]
        
        if len(templates) < initial_count:
            data = {"templates": templates}
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        
        return False


# Instance globale pour faciliter l'utilisation
template_manager = TemplateManager() 
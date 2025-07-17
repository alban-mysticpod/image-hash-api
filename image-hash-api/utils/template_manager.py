"""
Image template manager.
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class TemplateManager:
    """Manager for image templates."""
    
    def __init__(self, templates_file: str = "data/templates.json"):
        """
        Initialize template manager.
        
        Args:
            templates_file (str): Path to JSON templates file
        """
        self.templates_file = templates_file
        self._ensure_templates_file_exists()
    
    def _ensure_templates_file_exists(self):
        """Ensure templates.json file exists."""
        if not os.path.exists(self.templates_file):
            # Create parent directory if necessary
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
            
            # Create file with empty structure
            initial_data = {"templates": []}
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def load_templates(self) -> List[Dict]:
        """
        Load templates from JSON file.
        
        Returns:
            List[Dict]: List of templates with their information
        """
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("templates", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading templates: {e}")
            return []
    
    def save_template(self, name: str, hash_value: str, reference_image_path: str, 
                     crop_x: Optional[int] = None, crop_y: Optional[int] = None, 
                     crop_w: Optional[int] = None, crop_h: Optional[int] = None) -> Dict:
        """
        Ajoute un nouveau template au fichier JSON.
        
        Args:
            name (str): Nom du template
            hash_value (str): Hash perceptuel du template
            reference_image_path (str): Chemin vers l'image de référence
            
        Returns:
            Dict: Le template créé avec son ID
            
        Raises:
            ValueError: If a template with the same name already exists
        """
        templates = self.load_templates()
        
        # Check if template with this name already exists
        if any(t["name"] == name for t in templates):
            raise ValueError(f"A template with name '{name}' already exists")
        
        # Create new template
        new_template = {
            "id": len(templates) + 1,
            "name": name,
            "hash": hash_value,
            "reference_image_path": reference_image_path,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        # Add cropping coordinates if provided
        if crop_x is not None:
            new_template["crop_x"] = crop_x
        if crop_y is not None:
            new_template["crop_y"] = crop_y
        if crop_w is not None:
            new_template["crop_w"] = crop_w
        if crop_h is not None:
            new_template["crop_h"] = crop_h
            

        
        # Add to list
        templates.append(new_template)
        
        # Save
        data = {"templates": templates}
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return new_template
    
    def find_template_by_hash(self, hash_value: str, threshold: int = 5) -> Optional[Dict]:
        """
        Find template matching given hash.
        
        Args:
            hash_value (str): Hash to search for
            threshold (int): Acceptable Hamming distance threshold
            
        Returns:
            Optional[Dict]: Matching template or None if none found
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
                print(f"Error comparing with template {template['name']}: {e}")
                continue
        
        # Increment usage counter if template is found
        if best_match:
            self._increment_usage_count(best_match["id"])
        
        return best_match
    
    def _increment_usage_count(self, template_id: int):
        """Increment usage counter for a template."""
        templates = self.load_templates()
        
        for template in templates:
            if template["id"] == template_id:
                template["usage_count"] = template.get("usage_count", 0) + 1
                break
        
        # Save changes
        data = {"templates": templates}
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_template_by_id(self, template_id: int) -> Optional[Dict]:
        """
        Retrieve a template by its ID.
        
        Args:
            template_id (int): Template ID
            
        Returns:
            Optional[Dict]: Found template or None
        """
        templates = self.load_templates()
        return next((t for t in templates if t["id"] == template_id), None)
    
    def get_template_by_name(self, name: str) -> Optional[Dict]:
        """
        Retrieve a template by its name.
        
        Args:
            name (str): Template name
            
        Returns:
            Optional[Dict]: Found template or None
        """
        templates = self.load_templates()
        return next((t for t in templates if t["name"] == name), None)
    
    def list_templates(self) -> List[Dict]:
        """
        List all templates with their statistics.
        
        Returns:
            List[Dict]: List of templates
        """
        return self.load_templates()
    
    def delete_template(self, template_id: int) -> bool:
        """
        Delete a template by its ID.
        
        Args:
            template_id (int): ID of template to delete
            
        Returns:
            bool: True if deleted, False if not found
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


# Global instance for easy usage
template_manager = TemplateManager() 
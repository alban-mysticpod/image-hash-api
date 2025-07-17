"""
FastAPI API for managing hashed image templates.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
import os
import sys
import io
import requests
from datetime import datetime

# Add project directory to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.hash_utils import generate_phash_from_bytes, generate_phash, hamming_distance
from utils.template_manager import template_manager

app = FastAPI(
    title="Image Hash Template API",
    description="API for automatic image template recognition via perceptual hashing (pHash)",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Image Hash Template API",
        "version": "1.0.0",
        "endpoints": {
            "POST /hash-image": "Calculate pHash of an image",
            "POST /match-template": "Find template matching a hash",
            "POST /match-template-from-url": "Find template matching from image URL",
            "POST /add-template": "Add a new template",
            "POST /add-template-from-url": "Add a new template from image URL",
            "GET /templates": "List all templates",
            "GET /templates/{template_id}": "Get template by ID",
            "DELETE /templates/{template_id}": "Delete a template"
        }
    }


@app.post("/hash-image")
async def hash_image(file: UploadFile = File(...)):
    """
    Calculate the perceptual hash (pHash) of an uploaded image.
    
    Args:
        file: Image file to hash
        
    Returns:
        dict: Image hash and metadata
    """
    # Check file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    try:
        # Read file content
        image_data = await file.read()
        
        # Generate hash
        image_hash = generate_phash_from_bytes(image_data)
        
        return {
            "success": True,
            "hash": image_hash,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(image_data),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating hash: {str(e)}"
        )


@app.post("/match-template")
async def match_template(
    hash_value: str = Form(...),
    threshold: Optional[int] = Form(5)
):
    """
    Trouve le template correspondant le mieux à un hash donné.
    
    Args:
        hash_value: Hash à rechercher
        threshold: Seuil de distance de Hamming (défaut: 5)
        
    Returns:
        dict: Template correspondant ou message si aucun trouvé
    """
    try:
        # Utiliser la valeur par défaut si threshold est None
        threshold_value = threshold if threshold is not None else 5
        
        # Rechercher le template correspondant
        matched_template = template_manager.find_template_by_hash(hash_value, threshold_value)
        
        if matched_template:
            # Calculer la distance exacte
            distance = hamming_distance(hash_value, matched_template["hash"])
            
            return {
                "success": True,
                "match_found": True,
                "template": matched_template,
                "hamming_distance": distance,
                "similarity_score": max(0, 100 - (distance * 5))  # Score de similarité approximatif
            }
        else:
            return {
                "success": True,
                "match_found": False,
                "message": f"Aucun template trouvé avec une distance < {threshold_value}",
                "suggestions": {
                    "create_new_template": f"POST /add-template avec ce hash: {hash_value}",
                    "try_higher_threshold": "Essayez avec un seuil plus élevé"
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche de template: {str(e)}"
        )


@app.post("/match-template-from-url")
async def match_template_from_url(
    image_url: str = Form(...),
    threshold: Optional[int] = Form(5)
):
    """
    Trouve le template correspondant à une image depuis son URL.
    
    Args:
        image_url: URL publique de l'image à analyser
        threshold: Seuil de distance de Hamming (défaut: 5)
        
    Returns:
        dict: Template correspondant avec hash calculé et métadonnées
    """
    try:
        # Utiliser la valeur par défaut si threshold est None
        threshold_value = threshold if threshold is not None else 5
        
        # Télécharger l'image depuis l'URL
        print(f"📥 Téléchargement de l'image: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Vérifier le type de contenu
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"L'URL ne pointe pas vers une image valide. Type de contenu: {content_type}"
            )
        
        # Obtenir les données de l'image
        image_data = response.content
        image_size = len(image_data)
        
        # Calculer le hash de l'image
        print(f"🔢 Calcul du hash pour l'image ({image_size} bytes)")
        calculated_hash = generate_phash_from_bytes(image_data)
        
        # Rechercher le template correspondant
        print(f"🔍 Recherche de template pour hash: {calculated_hash}")
        matched_template = template_manager.find_template_by_hash(calculated_hash, threshold_value)
        
        if matched_template:
            # Calculer la distance exacte
            distance = hamming_distance(calculated_hash, matched_template["hash"])
            
            return {
                "success": True,
                "match_found": True,
                "image_info": {
                    "url": image_url,
                    "hash": calculated_hash,
                    "content_type": content_type,
                    "file_size": image_size,
                    "processed_at": datetime.now().isoformat()
                },
                "template": matched_template,
                "hamming_distance": distance,
                "similarity_score": max(0, 100 - (distance * 5)),
                "confidence": "high" if distance <= 2 else "medium" if distance <= 5 else "low"
            }
        else:
            return {
                "success": True,
                "match_found": False,
                "image_info": {
                    "url": image_url,
                    "hash": calculated_hash,
                    "content_type": content_type,
                    "file_size": image_size,
                    "processed_at": datetime.now().isoformat()
                },
                "message": f"Aucun template trouvé avec une distance < {threshold_value}",
                "suggestions": {
                    "calculated_hash": calculated_hash,
                    "create_new_template": f"POST /add-template avec ce hash: {calculated_hash}",
                    "try_higher_threshold": "Essayez avec un seuil plus élevé (ex: 10-15)",
                    "manual_check": "Vérifiez manuellement si cette image devrait correspondre à un template existant"
                }
            }
            
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail="Timeout lors du téléchargement de l'image (>30s)"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors du téléchargement de l'image: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement: {str(e)}"
        )


@app.post("/add-template")
async def add_template(
    name: str = Form(...),
    hash_value: str = Form(...),
    reference_image_path: str = Form(...),
    crop_x: Optional[str] = Form(None),
    crop_y: Optional[str] = Form(None),
    crop_w: Optional[str] = Form(None),
    crop_h: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Add a new template to the system.
    
    Args:
        name: Template name
        hash_value: Perceptual hash of the template
        reference_image_path: Path to reference image
        file: Optional - image file to automatically calculate hash
        
    Returns:
        dict: Created template with its information
    """
    try:
        # If a file is provided, calculate hash automatically
        if file:
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="File must be an image (JPEG, PNG, etc.)"
                )
            
            image_data = await file.read()
            calculated_hash = generate_phash_from_bytes(image_data)
            
            # Use calculated hash if none is provided explicitly
            if not hash_value or hash_value == "auto":
                hash_value = calculated_hash
            
            # Optional: save reference image locally
            if reference_image_path == "auto":
                upload_dir = "data/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                safe_filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                reference_image_path = os.path.join(upload_dir, safe_filename)
                
                with open(reference_image_path, "wb") as f:
                    f.write(image_data)
        
        # Convert cropping coordinates (string to int)
        crop_coords = {}
        try:
            if crop_x is not None and crop_x.strip():
                crop_coords['crop_x'] = int(crop_x)
            if crop_y is not None and crop_y.strip():
                crop_coords['crop_y'] = int(crop_y)
            if crop_w is not None and crop_w.strip():
                crop_coords['crop_w'] = int(crop_w)
            if crop_h is not None and crop_h.strip():
                crop_coords['crop_h'] = int(crop_h)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Les coordonnées de cropping doivent être des nombres entiers: {e}"
            )
        
        # Ajouter le template avec les coordonnées de cropping
        new_template = template_manager.save_template(
            name, hash_value, reference_image_path, 
            crop_x=crop_coords.get('crop_x'),
            crop_y=crop_coords.get('crop_y'),
            crop_w=crop_coords.get('crop_w'),
            crop_h=crop_coords.get('crop_h')
        )
        
        return {
            "success": True,
            "message": f"Template '{name}' ajouté avec succès",
            "template": new_template
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'ajout du template: {str(e)}"
        )


@app.post("/add-template-from-url")
async def add_template_from_url(
    image_url: str = Form(...),
    name: Optional[str] = Form(None)
):
    """
    Ajoute un nouveau template à partir d'une URL d'image.
    
    Args:
        image_url: URL publique de l'image à utiliser comme template
        name: Nom du template (optionnel, généré automatiquement si non fourni)
        
    Returns:
        dict: Template créé avec ses informations
    """
    try:
        # Télécharger l'image depuis l'URL
        print(f"📥 Téléchargement de l'image pour nouveau template: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Vérifier le type de contenu
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"L'URL ne pointe pas vers une image valide. Type de contenu: {content_type}"
            )
        
        # Obtenir les données de l'image
        image_data = response.content
        image_size = len(image_data)
        
        # Calculer le hash de l'image
        print(f"🔢 Calcul du hash pour le nouveau template ({image_size} bytes)")
        calculated_hash = generate_phash_from_bytes(image_data)
        
        # Vérifier si un template avec ce hash existe déjà
        existing_template = template_manager.find_template_by_hash(calculated_hash, threshold=2)
        if existing_template:
            return {
                "success": False,
                "error": "template_already_exists",
                "message": f"Un template similaire existe déjà: '{existing_template['name']}'",
                "existing_template": existing_template,
                "hash_distance": hamming_distance(calculated_hash, existing_template["hash"]),
                "suggestion": "Utilisez un seuil plus strict ou modifiez le template existant"
            }
        
        # Générer un nom automatique si non fourni
        if not name:
            existing_templates = template_manager.list_templates()
            template_count = len(existing_templates) + 1
            name = f"Template Auto {template_count}"
            
            # Vérifier que le nom n'existe pas déjà (au cas où)
            while any(t["name"] == name for t in existing_templates):
                template_count += 1
                name = f"Template Auto {template_count}"
        
        # Créer le répertoire de sauvegarde
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Générer un nom de fichier sécurisé
        from urllib.parse import urlparse
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(parsed_url.path) or "template_image"
        
        # Ajouter extension si manquante
        if not os.path.splitext(original_filename)[1]:
            extension = ".jpg"  # défaut
            if "png" in content_type:
                extension = ".png"
            elif "gif" in content_type:
                extension = ".gif"
            elif "webp" in content_type:
                extension = ".webp"
            original_filename += extension
        
        # Créer le chemin de fichier final
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"{safe_name}_{timestamp}_{original_filename}"
        reference_image_path = os.path.join(upload_dir, filename)
        
        # Sauvegarder l'image localement
        print(f"💾 Sauvegarde de l'image: {reference_image_path}")
        with open(reference_image_path, "wb") as f:
            f.write(image_data)
        
        # Ajouter le template
        print(f"➕ Création du template: {name}")
        new_template = template_manager.save_template(name, calculated_hash, reference_image_path)
        
        return {
            "success": True,
            "message": f"Template '{name}' créé avec succès à partir de l'URL",
            "template": new_template,
            "image_info": {
                "source_url": image_url,
                "local_path": reference_image_path,
                "hash": calculated_hash,
                "content_type": content_type,
                "file_size": image_size,
                "processed_at": datetime.now().isoformat()
            },
            "next_steps": {
                "edit_name": f"Vous pouvez modifier le nom via PUT /templates/{new_template['id']}",
                "test_matching": f"Testez avec POST /match-template-from-url",
                "view_all": "GET /templates pour voir tous les templates"
            }
        }
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail="Timeout lors du téléchargement de l'image (>30s)"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors du téléchargement de l'image: {str(e)}"
        )
    except ValueError as e:
        # Erreur du template_manager (nom déjà existant, etc.)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création du template: {str(e)}"
        )


@app.get("/templates")
async def list_templates():
    """
    Liste tous les templates disponibles.
    
    Returns:
        dict: Liste des templates avec leurs statistiques
    """
    try:
        templates = template_manager.list_templates()
        
        return {
            "success": True,
            "count": len(templates),
            "templates": templates
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des templates: {str(e)}"
        )


@app.get("/templates/{template_id}")
async def get_template(template_id: int):
    """
    Récupère un template spécifique par son ID.
    
    Args:
        template_id: ID du template
        
    Returns:
        dict: Informations du template
    """
    try:
        template = template_manager.get_template_by_id(template_id)
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template avec l'ID {template_id} non trouvé"
            )
        
        return {
            "success": True,
            "template": template
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du template: {str(e)}"
        )


@app.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    name: Optional[str] = Form(None),
    reference_image_path: Optional[str] = Form(None)
):
    """
    Met à jour les informations d'un template.
    
    Args:
        template_id: ID du template à modifier
        name: Nouveau nom du template (optionnel)
        reference_image_path: Nouveau chemin de l'image de référence (optionnel)
        
    Returns:
        dict: Template modifié
    """
    try:
        # Vérifier que le template existe
        existing_template = template_manager.get_template_by_id(template_id)
        if not existing_template:
            raise HTTPException(
                status_code=404,
                detail=f"Template avec l'ID {template_id} non trouvé"
            )
        
        # Si un nouveau nom est fourni, vérifier qu'il n'existe pas déjà
        if name and name != existing_template["name"]:
            if template_manager.get_template_by_name(name):
                raise HTTPException(
                    status_code=400,
                    detail=f"Un template avec le nom '{name}' existe déjà"
                )
        
        # Charger tous les templates pour la modification
        templates = template_manager.load_templates()
        
        # Trouver et modifier le template
        for template in templates:
            if template["id"] == template_id:
                if name:
                    template["name"] = name
                if reference_image_path:
                    template["reference_image_path"] = reference_image_path
                template["updated_at"] = datetime.now().isoformat()
                break
        
        # Sauvegarder les modifications
        data = {"templates": templates}
        with open(template_manager.templates_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Retourner le template modifié
        updated_template = template_manager.get_template_by_id(template_id)
        
        return {
            "success": True,
            "message": f"Template {template_id} mis à jour avec succès",
            "template": updated_template,
            "changes_made": {
                "name_updated": name is not None,
                "path_updated": reference_image_path is not None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour du template: {str(e)}"
        )


@app.delete("/templates/{template_id}")
async def delete_template(template_id: int):
    """
    Supprime un template par son ID.
    
    Args:
        template_id: ID du template à supprimer
        
    Returns:
        dict: Confirmation de suppression
    """
    try:
        deleted = template_manager.delete_template(template_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Template avec l'ID {template_id} non trouvé"
            )
        
        return {
            "success": True,
            "message": f"Template {template_id} supprimé avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting template: {str(e)}"
        )


@app.post("/compare-hashes")
async def compare_hashes(
    hash1: str = Form(...),
    hash2: str = Form(...)
):
    """
    Compare two hashes and return their Hamming distance.
    
    Args:
        hash1: First hash
        hash2: Second hash
        
    Returns:
        dict: Distance and similarity between hashes
    """
    try:
        distance = hamming_distance(hash1, hash2)
        similarity_score = max(0, 100 - (distance * 5))
        
        return {
            "success": True,
            "hash1": hash1,
            "hash2": hash2,
            "hamming_distance": distance,
            "similarity_score": similarity_score,
            "are_similar": distance < 5
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing hashes: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 
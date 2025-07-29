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

from utils.hash_utils import generate_phash_from_bytes, generate_phash, hamming_distance, generate_phash_with_dimensions_from_bytes, get_image_dimensions_from_bytes
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
            "POST /hash-image": "Calculate pHash of an image (includes dimensions)",
            "POST /image-dimensions": "Get dimensions of an uploaded image",
            "POST /image-dimensions-from-url": "Get dimensions of an image from URL",
            "POST /match-template": "Find template matching a hash",
            "POST /match-template-from-url": "Find template matching from image URL (includes dimensions)",
            "POST /add-template": "Add a new template",
            "POST /add-template-from-url": "Add a new template from image URL (includes dimensions)",
            "GET /templates": "List all templates",
            "GET /templates/{template_id}": "Get template by ID",
            "DELETE /templates/{template_id}": "Delete a template"
        }
    }


@app.post("/image-dimensions")
async def get_image_dimensions_endpoint(file: UploadFile = File(...)):
    """
    Get dimensions (width, height) of an uploaded image.
    
    Args:
        file: Image file to analyze
        
    Returns:
        dict: Image dimensions and metadata
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
        
        # Get dimensions
        width, height = get_image_dimensions_from_bytes(image_data)
        
        return {
            "success": True,
            "width": width,
            "height": height,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(image_data),
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting image dimensions: {str(e)}"
        )


@app.post("/image-dimensions-from-url")
async def get_image_dimensions_from_url(image_url: str = Form(...)):
    """
    Get dimensions (width, height) of an image from its URL.
    
    Args:
        image_url: Public URL of the image to analyze
        
    Returns:
        dict: Image dimensions and metadata
    """
    try:
        # Download image from URL
        print(f"📥 Downloading image for dimensions: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"URL does not point to a valid image. Content type: {content_type}"
            )
        
        # Get image data and dimensions
        image_data = response.content
        image_size = len(image_data)
        width, height = get_image_dimensions_from_bytes(image_data)
        
        return {
            "success": True,
            "width": width,
            "height": height,
            "image_info": {
                "url": image_url,
                "content_type": content_type,
                "file_size": image_size,
                "processed_at": datetime.now().isoformat()
            }
        }
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail="Timeout while downloading image (>30s)"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error downloading image: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting image dimensions: {str(e)}"
        )


@app.post("/hash-image")
async def hash_image(file: UploadFile = File(...)):
    """
    Calculate the perceptual hash (pHash) of an uploaded image and get its dimensions.
    
    Args:
        file: Image file to hash
        
    Returns:
        dict: Image hash, dimensions (width, height), and metadata
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
        
        # Generate hash and get dimensions
        hash_and_dimensions = generate_phash_with_dimensions_from_bytes(image_data)
        width, height = get_image_dimensions_from_bytes(image_data)
        
        return {
            "success": True,
            "hash": hash_and_dimensions["hash"],
            "width": hash_and_dimensions["width"],
            "height": hash_and_dimensions["height"],
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
    Find the best matching template for a given hash.
    
    Args:
        hash_value: Hash to search for
        threshold: Hamming distance threshold (default: 5)
        
    Returns:
        dict: Matching template or message if none found
    """
    try:
        # Use default value if threshold is None
        threshold_value = threshold if threshold is not None else 5
        
        # Search for matching template
        matched_template = template_manager.find_template_by_hash(hash_value, threshold_value)
        
        if matched_template:
            # Calculate exact distance
            distance = hamming_distance(hash_value, matched_template["hash"])
            
            return {
                "success": True,
                "match_found": True,
                "template": matched_template,
                "hamming_distance": distance,
                "similarity_score": max(0, 100 - (distance * 5))  # Approximate similarity score
            }
        else:
            return {
                "success": True,
                "match_found": False,
                "message": f"No template found with distance < {threshold_value}",
                "suggestions": {
                    "create_new_template": f"POST /add-template with this hash: {hash_value}",
                    "try_higher_threshold": "Try with a higher threshold"
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for template: {str(e)}"
        )


@app.post("/match-template-from-url")
async def match_template_from_url(
    image_url: str = Form(...),
    threshold: Optional[int] = Form(5)
):
    """
    Find the template matching an image from its URL.
    
    Args:
        image_url: Public URL of the image to analyze
        threshold: Hamming distance threshold (default: 5)
        
    Returns:
        dict: Matching template with calculated hash and metadata
    """
    try:
        # Use default value if threshold is None
        threshold_value = threshold if threshold is not None else 5
        
        # Download image from URL
        print(f"📥 Downloading image: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"URL does not point to a valid image. Content type: {content_type}"
            )
        
        # Get image data
        image_data = response.content
        image_size = len(image_data)
        
        # Calculate image hash and get dimensions
        print(f"🔢 Calculating hash for image ({image_size} bytes)")
        hash_and_dimensions = generate_phash_with_dimensions_from_bytes(image_data)
        calculated_hash = hash_and_dimensions["hash"]
        
        # Search for matching template
        print(f"🔍 Searching template for hash: {calculated_hash}")
        matched_template = template_manager.find_template_by_hash(calculated_hash, threshold_value)
        
        if matched_template:
            # Calculate exact distance
            distance = hamming_distance(calculated_hash, matched_template["hash"])
            
            # 🔄 SMART CROP COORDINATE CALCULATION
            current_width = hash_and_dimensions["width"]
            current_height = hash_and_dimensions["height"]
            
            # Create a copy of template to avoid modifying the original
            adjusted_template = matched_template.copy()
            
            # Check if template has ratios (new templates) or only absolute coordinates (old templates)
            has_ratios = all(key in matched_template for key in ['crop_x_ratio', 'crop_y_ratio', 'crop_w_ratio', 'crop_h_ratio'])
            has_dimensions = 'image_width' in matched_template and 'image_height' in matched_template
            has_crop_coords = all(key in matched_template for key in ['crop_x', 'crop_y', 'crop_w', 'crop_h'])
            
            print(f"🔄 Adjusting crop coordinates:")
            print(f"   Current image: {current_width}x{current_height}")
            print(f"   Template capabilities: ratios={has_ratios}, dimensions={has_dimensions}, crop_coords={has_crop_coords}")
            
            if has_ratios and has_crop_coords:
                # 🎯 NEW METHOD: Use ratios to calculate coordinates for current image dimensions
                new_crop_x = round(matched_template['crop_x_ratio'] * current_width)
                new_crop_y = round(matched_template['crop_y_ratio'] * current_height)
                new_crop_w = round(matched_template['crop_w_ratio'] * current_width)
                new_crop_h = round(matched_template['crop_h_ratio'] * current_height)
                
                print(f"   🎯 Using ratios to recalculate:")
                print(f"      Original coords: x={matched_template['crop_x']}, y={matched_template['crop_y']}, w={matched_template['crop_w']}, h={matched_template['crop_h']}")
                print(f"      Ratios: x={matched_template['crop_x_ratio']:.3f}, y={matched_template['crop_y_ratio']:.3f}, w={matched_template['crop_w_ratio']:.3f}, h={matched_template['crop_h_ratio']:.3f}")
                print(f"      Adjusted coords: x={new_crop_x}, y={new_crop_y}, w={new_crop_w}, h={new_crop_h}")
                
                # Update the template with adjusted coordinates
                adjusted_template.update({
                    'crop_x': new_crop_x,
                    'crop_y': new_crop_y,
                    'crop_w': new_crop_w,
                    'crop_h': new_crop_h,
                    'adjusted_for_dimensions': f"{current_width}x{current_height}",
                    'calculation_method': 'ratio_based'
                })
                
            elif has_crop_coords:
                # 📐 OLD METHOD: Keep original absolute coordinates (backwards compatibility)
                print(f"   📐 Using original absolute coordinates (no ratios available)")
                print(f"      Coords: x={matched_template['crop_x']}, y={matched_template['crop_y']}, w={matched_template['crop_w']}, h={matched_template['crop_h']}")
                adjusted_template['calculation_method'] = 'absolute_coordinates'
                
            else:
                # ⚠️ NO CROP DATA: Template has no crop information
                print(f"   ⚠️ Template has no crop coordinates")
                adjusted_template['calculation_method'] = 'no_crop_data'
            
            return {
                "success": True,
                "match_found": True,
                "image_info": {
                    "url": image_url,
                    "hash": calculated_hash,
                    "width": hash_and_dimensions["width"],
                    "height": hash_and_dimensions["height"],
                    "content_type": content_type,
                    "file_size": image_size,
                    "processed_at": datetime.now().isoformat()
                },
                "template": adjusted_template,
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
                    "width": hash_and_dimensions["width"],
                    "height": hash_and_dimensions["height"],
                    "content_type": content_type,
                    "file_size": image_size,
                    "processed_at": datetime.now().isoformat()
                },
                "message": f"No template found with distance < {threshold_value}",
                "suggestions": {
                    "calculated_hash": calculated_hash,
                    "create_new_template": f"POST /add-template with this hash: {calculated_hash}",
                    "try_higher_threshold": "Try with a higher threshold (ex: 10-15)",
                    "manual_check": "Manually check if this image should match an existing template"
                }
            }
            
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail="Timeout while downloading image (>30s)"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error downloading image: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during processing: {str(e)}"
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
        # Variables to store image dimensions if file is provided
        image_dimensions = None
        
        # If a file is provided, calculate hash automatically
        if file:
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="File must be an image (JPEG, PNG, etc.)"
                )
            
            image_data = await file.read()
            hash_and_dimensions = generate_phash_with_dimensions_from_bytes(image_data)
            calculated_hash = hash_and_dimensions["hash"]
            
            # Store dimensions for response
            image_dimensions = {
                "width": hash_and_dimensions["width"],
                "height": hash_and_dimensions["height"],
                "file_size": len(image_data),
                "content_type": file.content_type,
                "filename": file.filename
            }
            
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
                detail=f"Cropping coordinates must be integers: {e}"
            )
        
        # Add template with cropping coordinates and image dimensions if available
        new_template = template_manager.save_template(
            name, hash_value, reference_image_path, 
            crop_x=crop_coords.get('crop_x'),
            crop_y=crop_coords.get('crop_y'),
            crop_w=crop_coords.get('crop_w'),
            crop_h=crop_coords.get('crop_h'),
            image_width=image_dimensions["width"] if image_dimensions else None,
            image_height=image_dimensions["height"] if image_dimensions else None
        )
        
        # Prepare response with dimensions if available
        response = {
            "success": True,
            "message": f"Template '{name}' added successfully",
            "template": new_template
        }
        
        # Add image dimensions if file was processed
        if image_dimensions:
            response["image_info"] = {
                **image_dimensions,
                "processed_at": datetime.now().isoformat()
            }
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding template: {str(e)}"
        )


@app.post("/add-template-from-url")
async def add_template_from_url(
    image_url: str = Form(...),
    name: Optional[str] = Form(None)
):
    """
    Add a new template from an image URL.
    
    Args:
        image_url: Public URL of image to use as template
        name: Template name (optional, auto-generated if not provided)
        
    Returns:
        dict: Created template with its information
    """
    try:
        # Download image from URL
        print(f"📥 Downloading image for new template: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"URL does not point to a valid image. Content type: {content_type}"
            )
        
        # Get image data
        image_data = response.content
        image_size = len(image_data)
        
        # Calculate image hash and get dimensions
        print(f"🔢 Calculating hash for new template ({image_size} bytes)")
        hash_and_dimensions = generate_phash_with_dimensions_from_bytes(image_data)
        calculated_hash = hash_and_dimensions["hash"]
        
        # Check if template with this hash already exists
        existing_template = template_manager.find_template_by_hash(calculated_hash, threshold=2)
        if existing_template:
            return {
                "success": False,
                "error": "template_already_exists",
                "message": f"A similar template already exists: '{existing_template['name']}'",
                "existing_template": existing_template,
                "hash_distance": hamming_distance(calculated_hash, existing_template["hash"]),
                "suggestion": "Use a stricter threshold or modify the existing template"
            }
        
        # Generate automatic name if not provided
        if not name:
            existing_templates = template_manager.list_templates()
            template_count = len(existing_templates) + 1
            name = f"Template Auto {template_count}"
            
            # Check that name doesn't already exist (just in case)
            while any(t["name"] == name for t in existing_templates):
                template_count += 1
                name = f"Template Auto {template_count}"
        
        # Create upload directory
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate secure filename
        from urllib.parse import urlparse
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(parsed_url.path) or "template_image"
        
        # Add extension if missing
        if not os.path.splitext(original_filename)[1]:
            extension = ".jpg"  # default
            if "png" in content_type:
                extension = ".png"
            elif "gif" in content_type:
                extension = ".gif"
            elif "webp" in content_type:
                extension = ".webp"
            original_filename += extension
        
        # Create final file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"{safe_name}_{timestamp}_{original_filename}"
        reference_image_path = os.path.join(upload_dir, filename)
        
        # Save image locally
        print(f"💾 Saving image: {reference_image_path}")
        with open(reference_image_path, "wb") as f:
            f.write(image_data)
        
        # Add template with image dimensions
        print(f"➕ Creating template: {name}")
        new_template = template_manager.save_template(
            name, calculated_hash, reference_image_path,
            image_width=hash_and_dimensions["width"],
            image_height=hash_and_dimensions["height"]
        )
        
        return {
            "success": True,
            "message": f"Template '{name}' created successfully from URL",
            "template": new_template,
            "image_info": {
                "source_url": image_url,
                "local_path": reference_image_path,
                "hash": calculated_hash,
                "width": hash_and_dimensions["width"],
                "height": hash_and_dimensions["height"],
                "content_type": content_type,
                "file_size": image_size,
                "processed_at": datetime.now().isoformat()
            },
            "next_steps": {
                "edit_name": f"You can modify the name via PUT /templates/{new_template['id']}",
                "test_matching": f"Test with POST /match-template-from-url",
                "view_all": "GET /templates to see all templates"
            }
        }
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail="Timeout while downloading image (>30s)"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error downloading image: {str(e)}"
        )
    except ValueError as e:
        # Error from template_manager (name already exists, etc.)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating template: {str(e)}"
        )


@app.get("/templates")
async def list_templates():
    """
    List all available templates.
    
    Returns:
        dict: List of templates with their statistics
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
            detail=f"Error retrieving templates: {str(e)}"
        )


@app.get("/templates/{template_id}")
async def get_template(template_id: int):
    """
    Retrieve a specific template by its ID.
    
    Args:
        template_id: Template ID
        
    Returns:
        dict: Template information
    """
    try:
        template = template_manager.get_template_by_id(template_id)
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template with ID {template_id} not found"
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
            detail=f"Error retrieving template: {str(e)}"
        )


@app.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    name: Optional[str] = Form(None),
    reference_image_path: Optional[str] = Form(None)
):
    """
    Update template information.
    
    Args:
        template_id: ID of template to modify
        name: New template name (optional)
        reference_image_path: New reference image path (optional)
        
    Returns:
        dict: Modified template
    """
    try:
        # Check that template exists
        existing_template = template_manager.get_template_by_id(template_id)
        if not existing_template:
            raise HTTPException(
                status_code=404,
                detail=f"Template with ID {template_id} not found"
            )
        
        # If new name provided, check it doesn't already exist
        if name and name != existing_template["name"]:
            if template_manager.get_template_by_name(name):
                raise HTTPException(
                    status_code=400,
                    detail=f"A template with name '{name}' already exists"
                )
        
        # Load all templates for modification
        templates = template_manager.load_templates()
        
        # Find and modify template
        for template in templates:
            if template["id"] == template_id:
                if name:
                    template["name"] = name
                if reference_image_path:
                    template["reference_image_path"] = reference_image_path
                template["updated_at"] = datetime.now().isoformat()
                break
        
        # Save modifications
        data = {"templates": templates}
        with open(template_manager.templates_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Return modified template
        updated_template = template_manager.get_template_by_id(template_id)
        
        return {
            "success": True,
            "message": f"Template {template_id} updated successfully",
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
            detail=f"Error updating template: {str(e)}"
        )


@app.delete("/templates/{template_id}")
async def delete_template(template_id: int):
    """
    Delete a template by its ID.
    
    Args:
        template_id: ID of template to delete
        
    Returns:
        dict: Deletion confirmation
    """
    try:
        deleted = template_manager.delete_template(template_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Template with ID {template_id} not found"
            )
        
        return {
            "success": True,
            "message": f"Template {template_id} deleted successfully"
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
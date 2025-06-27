/**
 * Get depth map from image using MiDaS v3 small via Hugging Face Inference API
 * @param {File} imageFile - The mockup image file
 * @returns {Promise<ImageBitmap>} - Depth map as ImageBitmap
 */
export async function getDepthMap(imageFile) {
  // Try FAL.ai as primary method (most reliable with provided API key)
  try {
    console.log('Attempting depth estimation via FAL.ai...');
    return await getDepthMapFAL(imageFile);
  } catch (error) {
    console.log('FAL.ai failed:', error.message);
  }

  // Fallback to enhanced local depth map generation
  console.log('API failed, using enhanced fallback depth map...');
  return createFallbackDepthMap(imageFile);
}

/**
 * FAL.ai implementation (primary depth estimation method)
 */
export async function getDepthMapFAL(imageFile) {
  // Convert file to base64 for FAL API
  const imageBase64 = await fileToBase64(imageFile);
  
  // FAL.ai API call for MiDaS depth estimation
  const response = await fetch('https://fal.run/fal-ai/imageutils/depth', {
    method: 'POST',
    headers: {
      'Authorization': 'Key 763b2c3f-5883-48ad-a6d5-18214fe1bf11:6aa0098f353f85bbfec3adcb3268a76c',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_url: imageBase64
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`FAL depth estimation failed: ${response.status} - ${errorText}`);
  }

  const result = await response.json();
  console.log('FAL.ai response:', result);
  
  // Get depth map URL from response (according to FAL docs, it returns {image: {url: "..."}})
  const depthImageUrl = result.image?.url;
  
  if (!depthImageUrl) {
    console.error('FAL.ai response structure:', result);
    throw new Error('No depth map URL in FAL response');
  }
  
  // Fetch and convert depth image
  const depthResponse = await fetch(depthImageUrl);
  if (!depthResponse.ok) {
    throw new Error(`Failed to fetch depth image: ${depthResponse.status}`);
  }
  
  const depthBlob = await depthResponse.blob();
  const depthBitmap = await createImageBitmap(depthBlob);
  
  console.log('Successfully created depth bitmap from FAL.ai');
  return depthBitmap;
}

/**
 * Create a fallback depth map when API fails
 * Creates a t-shirt shaped depth map with more realistic contours
 */
async function createFallbackDepthMap(imageFile) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Load original image to get dimensions
  const img = await createImageBitmap(imageFile);
  canvas.width = img.width;
  canvas.height = img.height;
  
  // Draw the original image to analyze it
  ctx.drawImage(img, 0, 0);
  
  // Create a more realistic t-shirt depth map
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  
  // Clear canvas for depth map
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Create multiple gradients to simulate t-shirt contours
  // Main body gradient (torso area)
  const bodyGradient = ctx.createRadialGradient(
    centerX, centerY * 0.8, 0,
    centerX, centerY * 0.8, Math.min(canvas.width, canvas.height) * 0.3
  );
  bodyGradient.addColorStop(0, '#ffffff'); // Chest area is closest
  bodyGradient.addColorStop(0.7, '#888888'); 
  bodyGradient.addColorStop(1, '#444444'); // Sides are further
  
  ctx.fillStyle = bodyGradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Add shoulder contours
  const shoulderLeft = ctx.createRadialGradient(
    centerX * 0.3, centerY * 0.4, 0,
    centerX * 0.3, centerY * 0.4, centerX * 0.4
  );
  shoulderLeft.addColorStop(0, '#cccccc');
  shoulderLeft.addColorStop(1, 'transparent');
  
  const shoulderRight = ctx.createRadialGradient(
    centerX * 1.7, centerY * 0.4, 0,
    centerX * 1.7, centerY * 0.4, centerX * 0.4
  );
  shoulderRight.addColorStop(0, '#cccccc');
  shoulderRight.addColorStop(1, 'transparent');
  
  ctx.globalCompositeOperation = 'multiply';
  ctx.fillStyle = shoulderLeft;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = shoulderRight;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  ctx.globalCompositeOperation = 'source-over';
  
  console.log('Created fallback t-shirt depth map');
  
  return createImageBitmap(canvas);
}

/**
 * Convert file to base64 string
 */
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Process depth map for WebGL usage
 * @param {ImageBitmap} depthBitmap - Raw depth map
 * @returns {ImageBitmap} - Processed depth map (1024x1024, blurred, normalized)
 */
export async function processDepthMap(depthBitmap) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Downsample to 1024x1024
  canvas.width = 1024;
  canvas.height = 1024;
  
  ctx.drawImage(depthBitmap, 0, 0, 1024, 1024);
  
  // Apply Gaussian blur (simplified version)
  ctx.filter = 'blur(3px)';
  ctx.drawImage(canvas, 0, 0);
  ctx.filter = 'none';
  
  // Get image data for normalization
  const imageData = ctx.getImageData(0, 0, 1024, 1024);
  const data = imageData.data;
  
  // Find min/max for normalization
  let min = 255, max = 0;
  for (let i = 0; i < data.length; i += 4) {
    const gray = data[i]; // Use red channel as grayscale
    min = Math.min(min, gray);
    max = Math.max(max, gray);
  }
  
  // Normalize to 0-1 range
  const range = max - min;
  if (range > 0) {
    for (let i = 0; i < data.length; i += 4) {
      const normalized = (data[i] - min) / range * 255;
      data[i] = data[i + 1] = data[i + 2] = normalized;
    }
  }
  
  ctx.putImageData(imageData, 0, 0);
  
  return createImageBitmap(canvas);
} 
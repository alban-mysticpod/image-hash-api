/**
 * Build lighting masks (shadow and highlight) from mockup image
 * @param {ImageBitmap} mockupBitmap - The mockup image
 * @returns {Promise<{shadowMask: ImageBitmap, highlightMask: ImageBitmap}>}
 */
export async function buildLightingMasks(mockupBitmap) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  canvas.width = mockupBitmap.width;
  canvas.height = mockupBitmap.height;
  
  // Draw mockup to canvas
  ctx.drawImage(mockupBitmap, 0, 0);
  
  // Get image data
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  
  // Create shadow and highlight data arrays
  const shadowData = new Uint8ClampedArray(data.length);
  const highlightData = new Uint8ClampedArray(data.length);
  
  // Process each pixel
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const a = data[i + 3];
    
    // Convert RGB to LAB (simplified conversion)
    const lab = rgbToLab(r, g, b);
    const L = lab.L / 100; // Normalize L channel to 0-1
    
    // Calculate shadow mask: clamp(0.5 - L, 0, 1)
    const shadowValue = Math.max(0, Math.min(1, 0.5 - L)) * 255;
    
    // Calculate highlight mask: clamp(L - 0.5, 0, 1)
    const highlightValue = Math.max(0, Math.min(1, L - 0.5)) * 255;
    
    // Set shadow mask data (grayscale)
    shadowData[i] = shadowValue;
    shadowData[i + 1] = shadowValue;
    shadowData[i + 2] = shadowValue;
    shadowData[i + 3] = a;
    
    // Set highlight mask data (grayscale)
    highlightData[i] = highlightValue;
    highlightData[i + 1] = highlightValue;
    highlightData[i + 2] = highlightValue;
    highlightData[i + 3] = a;
  }
  
  // Create shadow mask bitmap
  const shadowImageData = new ImageData(shadowData, canvas.width, canvas.height);
  const shadowCanvas = document.createElement('canvas');
  const shadowCtx = shadowCanvas.getContext('2d');
  shadowCanvas.width = canvas.width;
  shadowCanvas.height = canvas.height;
  shadowCtx.putImageData(shadowImageData, 0, 0);
  const shadowMask = await createImageBitmap(shadowCanvas);
  
  // Create highlight mask bitmap
  const highlightImageData = new ImageData(highlightData, canvas.width, canvas.height);
  const highlightCanvas = document.createElement('canvas');
  const highlightCtx = highlightCanvas.getContext('2d');
  highlightCanvas.width = canvas.width;
  highlightCanvas.height = canvas.height;
  highlightCtx.putImageData(highlightImageData, 0, 0);
  const highlightMask = await createImageBitmap(highlightCanvas);
  
  return { shadowMask, highlightMask };
}

/**
 * Convert RGB to LAB color space (simplified)
 * @param {number} r - Red (0-255)
 * @param {number} g - Green (0-255) 
 * @param {number} b - Blue (0-255)
 * @returns {{L: number, A: number, B: number}} LAB values
 */
function rgbToLab(r, g, b) {
  // Normalize RGB to 0-1
  r = r / 255;
  g = g / 255;
  b = b / 255;
  
  // Convert RGB to XYZ
  r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
  g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
  b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;
  
  // Observer = 2°, Illuminant = D65
  let x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047;
  let y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.00000;
  let z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883;
  
  // XYZ to LAB
  x = x > 0.008856 ? Math.pow(x, 1/3) : (7.787 * x + 16/116);
  y = y > 0.008856 ? Math.pow(y, 1/3) : (7.787 * y + 16/116);
  z = z > 0.008856 ? Math.pow(z, 1/3) : (7.787 * z + 16/116);
  
  const L = (116 * y) - 16;
  const A = 500 * (x - y);
  const B = 200 * (y - z);
  
  return { L, A, B };
}

/**
 * Alternative simplified approach using perceived brightness
 * @param {ImageBitmap} mockupBitmap - The mockup image
 * @returns {Promise<{shadowMask: ImageBitmap, highlightMask: ImageBitmap}>}
 */
export async function buildLightingMasksSimple(mockupBitmap) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  canvas.width = mockupBitmap.width;
  canvas.height = mockupBitmap.height;
  
  // Draw mockup to canvas
  ctx.drawImage(mockupBitmap, 0, 0);
  
  // Get image data
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  
  // Create shadow and highlight data arrays
  const shadowData = new Uint8ClampedArray(data.length);
  const highlightData = new Uint8ClampedArray(data.length);
  
  // Process each pixel
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const a = data[i + 3];
    
    // Calculate perceived brightness (0-1)
    const brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    
    // Calculate shadow mask: clamp(0.5 - brightness, 0, 1)
    const shadowValue = Math.max(0, Math.min(1, 0.5 - brightness)) * 255;
    
    // Calculate highlight mask: clamp(brightness - 0.5, 0, 1)
    const highlightValue = Math.max(0, Math.min(1, brightness - 0.5)) * 255;
    
    // Set shadow mask data (grayscale)
    shadowData[i] = shadowValue;
    shadowData[i + 1] = shadowValue;
    shadowData[i + 2] = shadowValue;
    shadowData[i + 3] = a;
    
    // Set highlight mask data (grayscale)
    highlightData[i] = highlightValue;
    highlightData[i + 1] = highlightValue;
    highlightData[i + 2] = highlightValue;
    highlightData[i + 3] = a;
  }
  
  // Create shadow mask bitmap
  const shadowImageData = new ImageData(shadowData, canvas.width, canvas.height);
  const shadowCanvas = document.createElement('canvas');
  const shadowCtx = shadowCanvas.getContext('2d');
  shadowCanvas.width = canvas.width;
  shadowCanvas.height = canvas.height;
  shadowCtx.putImageData(shadowImageData, 0, 0);
  const shadowMask = await createImageBitmap(shadowCanvas);
  
  // Create highlight mask bitmap
  const highlightImageData = new ImageData(highlightData, canvas.width, canvas.height);
  const highlightCanvas = document.createElement('canvas');
  const highlightCtx = highlightCanvas.getContext('2d');
  highlightCanvas.width = canvas.width;
  highlightCanvas.height = canvas.height;
  highlightCtx.putImageData(highlightImageData, 0, 0);
  const highlightMask = await createImageBitmap(highlightCanvas);
  
  return { shadowMask, highlightMask };
} 
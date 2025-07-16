/**
 * Create a test design PNG with transparency for testing
 * @returns {Promise<File>} A PNG file with a colorful design
 */
export async function createTestDesignPNG() {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Set canvas size
  canvas.width = 400;
  canvas.height = 400;
  
  // Clear canvas with transparent background
  ctx.clearRect(0, 0, 400, 400);
  
  // Create a colorful design with transparency
  // Background circle
  ctx.fillStyle = 'rgba(255, 107, 107, 0.8)';
  ctx.beginPath();
  ctx.arc(200, 200, 150, 0, Math.PI * 2);
  ctx.fill();
  
  // Inner diamond
  ctx.fillStyle = 'rgba(78, 205, 196, 0.9)';
  ctx.beginPath();
  ctx.moveTo(200, 100); // top
  ctx.lineTo(280, 200); // right
  ctx.lineTo(200, 300); // bottom
  ctx.lineTo(120, 200); // left
  ctx.closePath();
  ctx.fill();
  
  // Center circle
  ctx.fillStyle = 'rgba(255, 230, 109, 0.9)';
  ctx.beginPath();
  ctx.arc(200, 200, 50, 0, Math.PI * 2);
  ctx.fill();
  
  // Text
  ctx.fillStyle = 'rgba(44, 62, 80, 1)';
  ctx.font = 'bold 24px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('TEST', 200, 340);
  ctx.fillText('DESIGN', 200, 370);
  
  // Convert canvas to blob and then to File
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      const file = new File([blob], 'test-design.png', { type: 'image/png' });
      resolve(file);
    }, 'image/png');
  });
}

/**
 * Create multiple test designs with different patterns
 * @returns {Promise<File[]>} Array of PNG files with different designs
 */
export async function createMultipleTestDesigns() {
  const designs = [];
  
  // Design 1: Circles
  designs.push(await createDesignWithPattern('circles', 'CIRCLES'));
  
  // Design 2: Stripes
  designs.push(await createDesignWithPattern('stripes', 'STRIPES'));
  
  // Design 3: Geometric
  designs.push(await createDesignWithPattern('geometric', 'GEO'));
  
  return designs;
}

/**
 * Create a design with a specific pattern
 */
async function createDesignWithPattern(pattern, text) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  canvas.width = 400;
  canvas.height = 400;
  ctx.clearRect(0, 0, 400, 400);
  
  switch (pattern) {
    case 'circles':
      // Multiple colorful circles
      const colors = ['rgba(255,107,107,0.7)', 'rgba(78,205,196,0.7)', 'rgba(255,230,109,0.7)'];
      for (let i = 0; i < 5; i++) {
        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.arc(150 + i * 25, 200, 40, 0, Math.PI * 2);
        ctx.fill();
      }
      break;
      
    case 'stripes':
      // Diagonal stripes
      ctx.fillStyle = 'rgba(255,107,107,0.8)';
      for (let i = 0; i < 400; i += 40) {
        ctx.fillRect(i, 0, 20, 400);
      }
      break;
      
    case 'geometric':
      // Geometric shapes
      ctx.fillStyle = 'rgba(78,205,196,0.8)';
      for (let x = 0; x < 4; x++) {
        for (let y = 0; y < 4; y++) {
          const size = 30;
          const spacing = 80;
          ctx.fillRect(50 + x * spacing, 50 + y * spacing, size, size);
        }
      }
      break;
  }
  
  // Add text
  ctx.fillStyle = 'rgba(44, 62, 80, 1)';
  ctx.font = 'bold 20px Arial';
  ctx.textAlign = 'center';
  ctx.fillText(text, 200, 350);
  
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      const file = new File([blob], `${pattern}-design.png`, { type: 'image/png' });
      resolve(file);
    }, 'image/png');
  });
} 
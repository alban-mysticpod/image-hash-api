import React from 'react';

export const DebugPanel = ({ mockupBitmap, depthBitmap, shadowMask, highlightMask, show = false }) => {
  if (!show) return null;

  const createImageUrl = async (bitmap) => {
    if (!bitmap) return null;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = bitmap.width;
    canvas.height = bitmap.height;
    ctx.drawImage(bitmap, 0, 0);
    return canvas.toDataURL();
  };

  const [images, setImages] = React.useState({});

  React.useEffect(() => {
    const loadImages = async () => {
      const newImages = {};
      if (mockupBitmap) newImages.mockup = await createImageUrl(mockupBitmap);
      if (depthBitmap) newImages.depth = await createImageUrl(depthBitmap);
      if (shadowMask) newImages.shadow = await createImageUrl(shadowMask);
      if (highlightMask) newImages.highlight = await createImageUrl(highlightMask);
      setImages(newImages);
    };
    loadImages();
  }, [mockupBitmap, depthBitmap, shadowMask, highlightMask]);

  const debugStyle = {
    position: 'fixed',
    top: '10px',
    right: '10px',
    width: '400px',
    background: 'rgba(0,0,0,0.9)',
    padding: '10px',
    borderRadius: '8px',
    color: 'white',
    fontSize: '12px',
    zIndex: 1000,
    maxHeight: '80vh',
    overflow: 'auto'
  };

  const imageStyle = {
    width: '80px',
    height: '80px',
    objectFit: 'cover',
    margin: '2px',
    border: '1px solid #666'
  };

  return (
    <div style={debugStyle}>
      <h4>Debug Panel</h4>
      <div>
        {images.mockup && (
          <div>
            <strong>Original Mockup:</strong><br/>
            <img src={images.mockup} alt="Mockup" style={imageStyle} />
          </div>
        )}
        {images.depth && (
          <div>
            <strong>Depth Map:</strong><br/>
            <img src={images.depth} alt="Depth" style={imageStyle} />
          </div>
        )}
        {images.shadow && (
          <div>
            <strong>Shadow Mask:</strong><br/>
            <img src={images.shadow} alt="Shadow" style={imageStyle} />
          </div>
        )}
        {images.highlight && (
          <div>
            <strong>Highlight Mask:</strong><br/>
            <img src={images.highlight} alt="Highlight" style={imageStyle} />
          </div>
        )}
      </div>
      <p>Press F12 to see console logs for more debugging info.</p>
    </div>
  );
}; 
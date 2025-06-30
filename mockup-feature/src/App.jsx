import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { getDepthMap, processDepthMap } from './utils/depthEstimation.js';
import { buildLightingMasksSimple } from './utils/lightingMasks.js';
import { MockupRenderer } from './utils/pixiRenderer.js';

function App() {
  // Core state
  const [mockupFile, setMockupFile] = useState(null);
  const [designFile, setDesignFile] = useState(null);
  const [mockupImage, setMockupImage] = useState(null);
  const [designImage, setDesignImage] = useState(null);
  const [designPosition, setDesignPosition] = useState({ x: 50, y: 50 });
  const [designSize, setDesignSize] = useState({ width: 200, height: 200 });
  const [depthMapUrl, setDepthMapUrl] = useState(null);
  const [depthMapMethod, setDepthMapMethod] = useState(null);
  
  // Interaction state
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  
  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [mockupRenderer, setMockupRenderer] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Refs
  const containerRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const webglCanvasRef = useRef(null);
  const animationFrameRef = useRef(null);

  // Calculate container dimensions based on mockup aspect ratio
  const containerDimensions = useMemo(() => {
    if (!mockupImage) return { width: 800, height: 600 };
    
    const maxWidth = 800;
    const maxHeight = 600;
    const aspectRatio = mockupImage.width / mockupImage.height;
    
    console.log('=== CALCULATING CONTAINER DIMENSIONS ===');
    console.log('Mockup dimensions:', mockupImage.width, 'x', mockupImage.height);
    console.log('Aspect ratio:', aspectRatio);
    console.log('Max constraints:', maxWidth, 'x', maxHeight);
    
    // Calculate container size maintaining aspect ratio
    let containerWidth = Math.min(maxWidth, mockupImage.width);
    let containerHeight = containerWidth / aspectRatio;
    
    console.log('Initial calculation - Width:', containerWidth, 'Height:', containerHeight);
    
    if (containerHeight > maxHeight) {
      containerHeight = maxHeight;
      containerWidth = containerHeight * aspectRatio;
      console.log('Constrained by height - Width:', containerWidth, 'Height:', containerHeight);
    }
    
    const result = {
      width: Math.round(containerWidth),
      height: Math.round(containerHeight)
    };
    
    console.log('Final container dimensions:', result);
    console.log('=== CONTAINER DIMENSIONS CALCULATED ===');
    
    return result;
  }, [mockupImage]);

  // Handle mockup file selection and processing
  const handleMockupChange = useCallback(async (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log('Mockup file selected:', file.name, file.type, file.size);
      setMockupFile(file);
      setIsProcessing(true);
      setProcessingStep('Loading mockup image...');
      
      try {
        const url = URL.createObjectURL(file);
        const img = new Image();
        img.onload = async () => {
          console.log('Mockup image loaded:', img.width, 'x', img.height);
          setMockupImage({ url, width: img.width, height: img.height });
          await initializeMockupProcessing(file);
        };
        img.onerror = () => {
          console.error('Failed to load mockup image');
          setIsProcessing(false);
        };
        img.src = url;
      } catch (error) {
        console.error('Error loading mockup:', error);
        setIsProcessing(false);
      }
    }
  }, []);

  // Initialize mockup processing with depth and lighting analysis
  const initializeMockupProcessing = useCallback(async (file) => {
    try {
      setProcessingStep('Analyzing depth information...');
      
      // Get depth map
      const { depthMap, method } = await getDepthMap(file);
      setDepthMapMethod(method);
      
      // Create and display depth map preview
      const depthMapCanvas = document.createElement('canvas');
      depthMapCanvas.width = depthMap.width;
      depthMapCanvas.height = depthMap.height;
      const ctx = depthMapCanvas.getContext('2d');
      ctx.drawImage(depthMap, 0, 0);
      setDepthMapUrl(depthMapCanvas.toDataURL());
      
      const processedDepthMap = await processDepthMap(depthMap);
      
      setProcessingStep('Calculating lighting masks...');
      
      // Create mockup bitmap for lighting analysis
      const mockupBitmap = await createImageBitmap(file);
      const { shadowMask, highlightMask } = await buildLightingMasksSimple(mockupBitmap);
      
      setProcessingStep('Initializing WebGL renderer...');
      
      // Set WebGL canvas size to match mockup dimensions
      if (webglCanvasRef.current) {
        webglCanvasRef.current.width = mockupBitmap.width;
        webglCanvasRef.current.height = mockupBitmap.height;
      }
      
      try {
        // Initialize PIXI renderer
        const renderer = new MockupRenderer(webglCanvasRef.current);
        await renderer.initialize(mockupBitmap, processedDepthMap, shadowMask, highlightMask);
        
        setMockupRenderer(renderer);
        setIsInitialized(true);
        setProcessingStep('Ready!');
        
        console.log('WebGL renderer initialized successfully');
        
      } catch (webglError) {
        console.warn('WebGL initialization failed, using fallback mode:', webglError);
        setProcessingStep('WebGL failed, using fallback mode...');
        
        // Set initialized to true anyway so user can still interact
        setIsInitialized(true);
      }
      
      setTimeout(() => {
        setIsProcessing(false);
      }, 500);
      
    } catch (error) {
      console.error('Error processing mockup:', error);
      setProcessingStep('Error: ' + error.message);
      setIsProcessing(false);
    }
  }, []);

  // Handle design file selection
  const handleDesignChange = useCallback(async (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log('Design file selected:', file.name, file.type, file.size);
      setDesignFile(file);
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        console.log('Design image loaded:', img.width, 'x', img.height);
        setDesignImage({ url, width: img.width, height: img.height });
        // Reset position and size when new design is loaded
        setDesignPosition({ x: 50, y: 50 });
        setDesignSize({ width: 200, height: 200 });
      };
      img.onerror = () => {
        console.error('Failed to load design image');
      };
      img.src = url;
    }
  }, []);

  // Fallback canvas rendering when WebGL fails
  const renderFallbackCanvas = useCallback(() => {
    if (!overlayCanvasRef.current || !containerRef.current || !mockupImage || !designImage) {
      console.log('Fallback render skipped - missing refs or images');
      console.log('Has overlay canvas:', !!overlayCanvasRef.current);
      console.log('Has container:', !!containerRef.current);
      console.log('Has mockup:', !!mockupImage);
      console.log('Has design:', !!designImage);
      return;
    }

    console.log('=== STARTING FALLBACK CANVAS RENDER ===');
    const overlayCanvas = overlayCanvasRef.current;
    const container = containerRef.current;
    const ctx = overlayCanvas.getContext('2d');

    // Set overlay canvas size to match container exactly
    overlayCanvas.width = container.offsetWidth;
    overlayCanvas.height = container.offsetHeight;
    
    console.log('Container dimensions:', container.offsetWidth, 'x', container.offsetHeight);
    console.log('Overlay canvas sized:', overlayCanvas.width, 'x', overlayCanvas.height);
    console.log('Mockup image dimensions:', mockupImage.width, 'x', mockupImage.height);
    console.log('Design position:', designPosition, 'Design size:', designSize);
    
    // Clear canvas
    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    
    // Draw mockup as background
    const mockupImg = new Image();
    mockupImg.onload = () => {
      console.log('Mockup image loaded for fallback, drawing...');
      
      // Calculate scaling to fit mockup properly in canvas
      const canvasAspect = overlayCanvas.width / overlayCanvas.height;
      const imageAspect = mockupImg.width / mockupImg.height;
      
      console.log('Canvas aspect ratio:', canvasAspect, 'Image aspect ratio:', imageAspect);
      
      let drawWidth, drawHeight, drawX, drawY;
      
      if (imageAspect > canvasAspect) {
        // Image is wider than canvas - fit to width
        drawWidth = overlayCanvas.width;
        drawHeight = overlayCanvas.width / imageAspect;
        drawX = 0;
        drawY = (overlayCanvas.height - drawHeight) / 2;
      } else {
        // Image is taller than canvas - fit to height
        drawHeight = overlayCanvas.height;
        drawWidth = overlayCanvas.height * imageAspect;
        drawX = (overlayCanvas.width - drawWidth) / 2;
        drawY = 0;
      }
      
      console.log('Drawing mockup at:', drawX, drawY, 'with size:', drawWidth, 'x', drawHeight);
      
      // Draw mockup scaled to fit container properly
      ctx.drawImage(mockupImg, drawX, drawY, drawWidth, drawHeight);
      
      // Draw design on top
      const designImg = new Image();
      designImg.onload = () => {
        console.log('Design image loaded for fallback, drawing at:', designPosition);
        
        // Use source-over with reduced opacity for cleaner blending
        ctx.globalCompositeOperation = 'source-over';
        ctx.globalAlpha = 0.9;
        
        // Enable image smoothing for better quality
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';
        
        console.log('Drawing design with position/size:', designPosition.x, designPosition.y, designSize.width, designSize.height);
        
        // Draw design at current position
        ctx.drawImage(designImg, 
          designPosition.x, designPosition.y, 
          designSize.width, designSize.height);
        
        // Apply a subtle multiply effect for fabric-like blending
        ctx.globalCompositeOperation = 'multiply';
        ctx.globalAlpha = 0.3;
        
        // Draw design again with multiply for depth effect
        ctx.drawImage(designImg, 
          designPosition.x, designPosition.y, 
          designSize.width, designSize.height);
        
        // Reset blend mode
        ctx.globalCompositeOperation = 'source-over';
        ctx.globalAlpha = 1.0;
        
        console.log('=== FALLBACK CANVAS RENDER COMPLETED ===');
      };
      designImg.onerror = () => {
        console.error('Failed to load design image for fallback');
      };
      designImg.src = designImage.url;
    };
    mockupImg.onerror = () => {
      console.error('Failed to load mockup image for fallback');
    };
    mockupImg.src = mockupImage.url;
  }, [mockupImage, designImage, designPosition, designSize]);

  // Update overlay canvas for live preview
  const updateOverlayCanvas = useCallback(() => {
    if (!overlayCanvasRef.current || !webglCanvasRef.current || !containerRef.current) return;

    const overlayCanvas = overlayCanvasRef.current;
    const webglCanvas = webglCanvasRef.current;
    const container = containerRef.current;
    const ctx = overlayCanvas.getContext('2d');

    // Set overlay canvas size to match container exactly
    overlayCanvas.width = container.offsetWidth;
    overlayCanvas.height = container.offsetHeight;
    
    // Clear canvas
    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    
    // Draw the WebGL result scaled to fit container with proper aspect ratio
    if (webglCanvas.width > 0 && webglCanvas.height > 0) {
      console.log('WebGL canvas size:', webglCanvas.width, 'x', webglCanvas.height);
      console.log('Overlay canvas size:', overlayCanvas.width, 'x', overlayCanvas.height);
      
      // Calculate scaling to fit WebGL result properly in overlay canvas
      const canvasAspect = overlayCanvas.width / overlayCanvas.height;
      const webglAspect = webglCanvas.width / webglCanvas.height;
      
      let drawWidth, drawHeight, drawX, drawY;
      
      if (webglAspect > canvasAspect) {
        // WebGL is wider than overlay - fit to width
        drawWidth = overlayCanvas.width;
        drawHeight = overlayCanvas.width / webglAspect;
        drawX = 0;
        drawY = (overlayCanvas.height - drawHeight) / 2;
      } else {
        // WebGL is taller than overlay - fit to height
        drawHeight = overlayCanvas.height;
        drawWidth = overlayCanvas.height * webglAspect;
        drawX = (overlayCanvas.width - drawWidth) / 2;
        drawY = 0;
      }
      
      console.log('Drawing WebGL result at:', drawX, drawY, 'with size:', drawWidth, 'x', drawHeight);
      
      ctx.drawImage(webglCanvas, drawX, drawY, drawWidth, drawHeight);
    }
    
    console.log('Overlay canvas updated:', overlayCanvas.width, 'x', overlayCanvas.height);
  }, []);

  // Real-time rendering effect
  const updateMockupRender = useCallback(async () => {
    if (!isInitialized || !designImage || !mockupImage) {
      console.log('Update render skipped:', { isInitialized, hasDesign: !!designImage, hasMockup: !!mockupImage });
      return;
    }

    console.log('=== UPDATE MOCKUP RENDER START ===');
    console.log('Mockup renderer available:', !!mockupRenderer);
    
    try {
      // Get container dimensions for scaling
      const containerRect = containerRef.current?.getBoundingClientRect();
      if (!containerRect) {
        console.log('No container rect available');
        return;
      }

      const container = containerRef.current;
      const containerWidth = container.offsetWidth;
      const containerHeight = container.offsetHeight;

      console.log('Container rect:', containerRect);
      console.log('Container offset dimensions:', containerWidth, 'x', containerHeight);
      console.log('Mockup image size:', mockupImage.width, 'x', mockupImage.height);
      
      const scaleX = mockupImage.width / containerWidth;
      const scaleY = mockupImage.height / containerHeight;

      console.log('Scale factors - X:', scaleX, 'Y:', scaleY);

      // Calculate scaled design properties
      const scaledX = designPosition.x * scaleX;
      const scaledY = designPosition.y * scaleY;
      const scaledWidth = designSize.width * scaleX;
      const scaledHeight = designSize.height * scaleY;

      console.log('Design position/size:', designPosition, designSize);
      console.log('Scaled design position/size:', { x: scaledX, y: scaledY, width: scaledWidth, height: scaledHeight });

      if (mockupRenderer) {
        console.log('Using WebGL rendering path');
        // WebGL path - advanced 3D effects
        const designCanvas = document.createElement('canvas');
        const designCtx = designCanvas.getContext('2d');
        designCanvas.width = mockupImage.width;
        designCanvas.height = mockupImage.height;

        // Load design image
        const designImg = new Image();
        designImg.onload = async () => {
          // Clear canvas
          designCtx.clearRect(0, 0, designCanvas.width, designCanvas.height);
          
          // Draw design at scaled position
          designCtx.drawImage(designImg, scaledX, scaledY, scaledWidth, scaledHeight);
          
          // Convert to bitmap and render
          const designBitmap = await createImageBitmap(designCanvas);
          await mockupRenderer.renderDesignAtPosition(designBitmap);
          
          // Force update overlay canvas
          updateOverlayCanvas();
        };
        designImg.src = designImage.url;
      } else {
        console.log('Using fallback 2D canvas rendering path');
        // Fallback path - simple 2D canvas overlay
        renderFallbackCanvas();
      }

    } catch (error) {
      console.error('Error updating mockup render:', error);
      console.log('Falling back to 2D canvas rendering');
      // Try fallback rendering
      renderFallbackCanvas();
    }
    
    console.log('=== UPDATE MOCKUP RENDER END ===');
  }, [mockupRenderer, isInitialized, designImage, mockupImage, designPosition, designSize, renderFallbackCanvas, updateOverlayCanvas]);

  // Effect to update rendering when position/size changes
  useEffect(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    animationFrameRef.current = requestAnimationFrame(() => {
      updateMockupRender();
    });

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [updateMockupRender, designPosition, designSize]);

  // Initial render when design is loaded
  useEffect(() => {
    if (isInitialized && designImage && mockupImage) {
      updateMockupRender();
    }
  }, [isInitialized, designImage, mockupImage, updateMockupRender]);

  // Handle container resize when mockup changes
  useEffect(() => {
    if (overlayCanvasRef.current && containerRef.current && mockupImage) {
      // Small delay to ensure container has updated dimensions
      const timeoutId = setTimeout(() => {
        if (designImage) {
          updateMockupRender();
        }
      }, 100);
      
      return () => clearTimeout(timeoutId);
    }
  }, [mockupImage, designImage, updateMockupRender]);

  // Mouse down handler for dragging
  const handleMouseDown = useCallback((event) => {
    event.preventDefault();
    const rect = containerRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    console.log('Mouse down at:', x, y, 'Container rect:', rect);
    console.log('Design position:', designPosition, 'Design size:', designSize);
    
    // Check if clicking on resize handle (bottom-right corner)
    const handleSize = 20;
    const resizeX = designPosition.x + designSize.width - handleSize;
    const resizeY = designPosition.y + designSize.height - handleSize;
    
    console.log('Resize handle area:', resizeX, resizeY, 'to', resizeX + handleSize, resizeY + handleSize);
    
    if (x >= resizeX && x <= resizeX + handleSize && 
        y >= resizeY && y <= resizeY + handleSize) {
      console.log('Starting resize');
      setIsResizing(true);
    } else if (x >= designPosition.x && x <= designPosition.x + designSize.width &&
               y >= designPosition.y && y <= designPosition.y + designSize.height) {
      console.log('Starting drag');
      setIsDragging(true);
      setDragOffset({
        x: x - designPosition.x,
        y: y - designPosition.y
      });
    } else {
      console.log('Click outside design area');
    }
  }, [designPosition, designSize]);

  // Mouse move handler
  const handleMouseMove = useCallback((event) => {
    if (!isDragging && !isResizing) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const container = containerRef.current;
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    if (isDragging) {
      const newX = Math.max(0, Math.min(x - dragOffset.x, container.offsetWidth - designSize.width));
      const newY = Math.max(0, Math.min(y - dragOffset.y, container.offsetHeight - designSize.height));
      console.log('Dragging to:', newX, newY, 'Container bounds:', container.offsetWidth, 'x', container.offsetHeight);
      setDesignPosition({ x: newX, y: newY });
    } else if (isResizing) {
      const newWidth = Math.max(50, x - designPosition.x);
      const newHeight = Math.max(50, y - designPosition.y);
      const constrainedWidth = Math.min(newWidth, container.offsetWidth - designPosition.x);
      const constrainedHeight = Math.min(newHeight, container.offsetHeight - designPosition.y);
      console.log('Resizing to:', constrainedWidth, constrainedHeight);
      setDesignSize({
        width: constrainedWidth,
        height: constrainedHeight
      });
    }
  }, [isDragging, isResizing, dragOffset, designPosition, designSize]);

  // Mouse up handler
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setIsResizing(false);
  }, []);

  // Generate final high-resolution result
  const handleGenerate = useCallback(async () => {
    if (!mockupRenderer || !designImage) return;

    try {
      setIsProcessing(true);
      setProcessingStep('Generating final high-resolution result...');
      
      const result = await mockupRenderer.captureFrame();
      
      // Create download link
      const link = document.createElement('a');
      link.download = 'mockup-result.png';
      link.href = result;
      link.click();
      
      setProcessingStep('Download started!');
      setTimeout(() => setIsProcessing(false), 1000);
      
    } catch (error) {
      console.error('Error generating final result:', error);
      setProcessingStep('Error generating result');
      setIsProcessing(false);
    }
  }, [mockupRenderer, designImage]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (mockupRenderer) {
        mockupRenderer.destroy();
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [mockupRenderer]);

  return (
    <div className="app">
      <h1>Smart Mock-up Designer</h1>
      <p>Upload a mockup and design, then drag and resize to see real-time 3D blending with depth and lighting effects.</p>

      {/* Processing Status */}
      {isProcessing && (
        <div className="processing-status">
          <div className="processing-spinner"></div>
          <span>{processingStep}</span>
        </div>
      )}

      {/* File Inputs */}
      <div className="file-inputs">
        <div className="file-input">
          <label htmlFor="mockup-input">
            <strong>Select Mock-up Image</strong>
          </label>
          <input
            id="mockup-input"
            type="file"
            accept="image/*"
            onChange={handleMockupChange}
            disabled={isProcessing}
          />
          {mockupFile && depthMapUrl && (
            <div className="depth-map-preview">
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '15px',
                marginTop: '10px' 
              }}>
                <img 
                  src={depthMapUrl} 
                  alt="Depth Map Preview" 
                  style={{ 
                    maxWidth: '200px', 
                    maxHeight: '200px',
                    border: '1px solid #ccc',
                    borderRadius: '4px'
                  }} 
                />
                <div style={{
                  padding: '8px 12px',
                  backgroundColor: depthMapMethod === 'ZoeDepth' ? '#e6f4ea' : '#fff3e0',
                  borderRadius: '4px',
                  fontSize: '14px',
                  color: depthMapMethod === 'ZoeDepth' ? '#1e4620' : '#b45f06',
                  border: `1px solid ${depthMapMethod === 'ZoeDepth' ? '#b7dfb9' : '#ffe0b2'}`
                }}>
                  {depthMapMethod || 'Unknown'} Depth Map
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="file-input">
          <label htmlFor="design-input">
            <strong>Select Design Image</strong>
          </label>
          <input
            id="design-input"
            type="file"
            accept="image/*"
            onChange={handleDesignChange}
            disabled={!isInitialized}
          />
          {designFile && <p>Selected: {designFile.name}</p>}
        </div>
      </div>

      {/* Interactive Design Area */}
      {mockupImage && isInitialized && (
        <div 
          ref={containerRef}
          className="design-container"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          style={{
            position: 'relative',
            width: containerDimensions.width,
            height: containerDimensions.height,
            background: designImage ? '#000' : `url(${mockupImage.url}) center/contain no-repeat`,
            border: '2px solid #646cff',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        >
          {/* Instruction bar when design is loaded */}
          {designImage && (
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                background: 'rgba(100, 108, 255, 0.9)',
                color: 'white',
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: '500',
                textAlign: 'center',
                zIndex: 10,
                borderRadius: '10px 10px 0 0'
              }}
            >
              👆 Drag to move • Drag corner handle to resize
            </div>
          )}

          {/* Live mockup preview with WebGL effects */}
          <canvas 
            ref={overlayCanvasRef}
            className="mockup-preview"
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
              zIndex: 1
            }}
          />
          
          {/* Design position indicator */}
          {designImage && (
            <div
              className="design-indicator"
              style={{
                position: 'absolute',
                left: designPosition.x,
                top: designPosition.y,
                width: designSize.width,
                height: designSize.height,
                border: '2px dashed rgba(100, 108, 255, 0.8)',
                cursor: isDragging ? 'grabbing' : 'grab',
                backgroundColor: 'rgba(100, 108, 255, 0.05)',
                zIndex: 2,
                pointerEvents: 'auto'
              }}
              onMouseDown={handleMouseDown}
            >
              {/* Resize Handle */}
              <div 
                className="resize-handle"
                style={{
                  position: 'absolute',
                  bottom: -12,
                  right: -12,
                  width: 24,
                  height: 24,
                  backgroundColor: '#fff',
                  border: '3px solid #646cff',
                  borderRadius: '50%',
                  cursor: isResizing ? 'nw-resize' : 'se-resize',
                  zIndex: 3,
                  pointerEvents: 'auto',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                }}
                onMouseDown={(e) => {
                  e.stopPropagation();
                  console.log('Resize handle clicked directly');
                  setIsResizing(true);
                }}
              />
            </div>
          )}
        </div>
      )}

      {/* Generate Button */}
      {mockupImage && designImage && isInitialized && (
        <button 
          className="generate-btn" 
          onClick={handleGenerate}
          disabled={isProcessing}
        >
          Download Final High-Resolution Result
        </button>
      )}

      {/* Hidden WebGL Canvas */}
      <canvas 
        ref={webglCanvasRef} 
        style={{ display: 'none' }} 
        width={mockupImage?.width || 512} 
        height={mockupImage?.height || 512}
      />
    </div>
  );
}

export default App; 
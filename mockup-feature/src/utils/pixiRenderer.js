import * as PIXI from 'pixi.js';

/**
 * Custom PIXI Filter for fabric wrapping effect
 */
class FabricWrapFilter extends PIXI.Filter {
  constructor() {
    const vertexShader = `
      attribute vec2 aVertexPosition;
      attribute vec2 aTextureCoord;
      
      uniform mat3 projectionMatrix;
      
      varying vec2 vTextureCoord;
      varying vec2 vUV;
      
      void main(void) {
        gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);
        vTextureCoord = aTextureCoord;
        vUV = aTextureCoord;
      }
    `;

    const fragmentShader = `
      precision mediump float;
      
      varying vec2 vTextureCoord;
      varying vec2 vUV;
      
      uniform sampler2D uSampler;     // Base mockup texture
      uniform sampler2D uDisp;        // Displacement/depth map
      uniform sampler2D uShadow;      // Shadow mask
      uniform sampler2D uHighlight;   // Highlight mask
      uniform sampler2D uDesign;      // Design texture to apply
      
      uniform float uStrength;        // Displacement strength
      uniform float uShadowPower;     // Shadow intensity
      uniform float uHighlightPower;  // Highlight intensity
      
      void main(void) {
        // Sample base texture first
        vec4 base = texture2D(uSampler, vUV);
        vec3 composite = base.rgb;
        
        // Sample displacement map and calculate warp offset
        float displacement = texture2D(uDisp, vUV).r;
        
        // Calculate warped coordinates for design sampling
        vec2 warp = vUV + (displacement - 0.5) * uStrength * 0.2;
        warp = clamp(warp, 0.0, 1.0);
        
        // Sample design texture at warped coordinates
        vec4 design = texture2D(uDesign, warp);
        
        // Blend design with base using multiply for fabric effect
        if (design.a > 0.1) {
          vec3 fabricColor = base.rgb * design.rgb;
          composite = mix(base.rgb, fabricColor, design.a * 0.8);
        }
        
        // Sample and apply lighting masks
        float shadow = texture2D(uShadow, vUV).r;
        float highlight = texture2D(uHighlight, vUV).r;
        
        // Apply lighting effects
        composite = composite * (1.0 - shadow * uShadowPower * 0.6);
        composite = composite + highlight * uHighlightPower * 0.4;
        
        // Clamp final result
        composite = clamp(composite, 0.0, 1.0);
        
        gl_FragColor = vec4(composite, 1.0);
      }
    `;

    super(vertexShader, fragmentShader, {
      uDisp: { value: null, type: 'sampler2D' },
      uShadow: { value: null, type: 'sampler2D' },
      uHighlight: { value: null, type: 'sampler2D' },
      uDesign: { value: null, type: 'sampler2D' },
      uStrength: { value: 0.1, type: '1f' },
      uShadowPower: { value: 0.3, type: '1f' },
      uHighlightPower: { value: 0.2, type: '1f' }
    });
  }

  get displacement() {
    return this.uniforms.uDisp;
  }

  set displacement(value) {
    this.uniforms.uDisp = value;
  }

  get shadow() {
    return this.uniforms.uShadow;
  }

  set shadow(value) {
    this.uniforms.uShadow = value;
  }

  get highlight() {
    return this.uniforms.uHighlight;
  }

  set highlight(value) {
    this.uniforms.uHighlight = value;
  }

  get design() {
    return this.uniforms.uDesign;
  }

  set design(value) {
    this.uniforms.uDesign = value;
  }

  get strength() {
    return this.uniforms.uStrength;
  }

  set strength(value) {
    this.uniforms.uStrength = value;
  }

  get shadowPower() {
    return this.uniforms.uShadowPower;
  }

  set shadowPower(value) {
    this.uniforms.uShadowPower = value;
  }

  get highlightPower() {
    return this.uniforms.uHighlightPower;
  }

  set highlightPower(value) {
    this.uniforms.uHighlightPower = value;
  }
}

/**
 * MockupRenderer class for handling all PIXI rendering operations
 */
export class MockupRenderer {
  constructor(canvasElement) {
    try {
      console.log('Initializing PIXI Application...');
      console.log('Canvas element:', canvasElement);
      console.log('Canvas dimensions:', canvasElement.width, 'x', canvasElement.height);
      console.log('WebGL support check:', PIXI.utils.isWebGLSupported());
      
      // Initialize PIXI Application with canvas dimensions
      this.app = new PIXI.Application({
        view: canvasElement,
        width: canvasElement.width,
        height: canvasElement.height,
        backgroundColor: 0x000000,
        antialias: true,
        preserveDrawingBuffer: true,
        forceCanvas: false, // Don't force canvas, let PIXI decide
        powerPreference: 'high-performance'
      });
      
      console.log('PIXI Application created successfully');
      console.log('PIXI App dimensions:', this.app.screen.width, 'x', this.app.screen.height);
      console.log('Renderer type:', this.app.renderer.type === PIXI.RENDERER_TYPE.WEBGL ? 'WebGL' : 'Canvas');
      console.log('WebGL version:', this.app.renderer.gl ? this.app.renderer.gl.getParameter(this.app.renderer.gl.VERSION) : 'N/A');
      
      // Check if we got WebGL
      if (this.app.renderer.type !== PIXI.RENDERER_TYPE.WEBGL) {
        throw new Error('PIXI Application fell back to Canvas renderer instead of WebGL');
      }
      
    } catch (error) {
      console.error('Failed to initialize PIXI Application:', error);
      throw new Error(`WebGL initialization failed: ${error.message}`);
    }

    // Initialize properties
    this.baseSprite = null;
    this.fabricFilter = null;
    this.baseTexture = null;
    this.dispTexture = null;
    this.shadowTexture = null;
    this.highlightTexture = null;
    this.designTextures = [];
    this.results = [];
  }

  /**
   * Initialize the renderer with base mockup and processed textures
   */
  async initialize(mockupBitmap, depthBitmap, shadowBitmap, highlightBitmap) {
    try {
      console.log('Initializing MockupRenderer with bitmaps:');
      console.log('- Mockup:', mockupBitmap.width, 'x', mockupBitmap.height);
      console.log('- Depth:', depthBitmap.width, 'x', depthBitmap.height);
      console.log('- Shadow:', shadowBitmap.width, 'x', shadowBitmap.height);
      console.log('- Highlight:', highlightBitmap.width, 'x', highlightBitmap.height);
      
      // Create PIXI textures from bitmaps
      this.baseTexture = PIXI.Texture.from(mockupBitmap);
      this.dispTexture = PIXI.Texture.from(depthBitmap);
      this.shadowTexture = PIXI.Texture.from(shadowBitmap);
      this.highlightTexture = PIXI.Texture.from(highlightBitmap);

      // Wait for all textures to be ready
      const textures = [this.baseTexture, this.dispTexture, this.shadowTexture, this.highlightTexture];
      await Promise.all(textures.map(texture => {
        if (texture.valid) return Promise.resolve();
        return new Promise(resolve => texture.baseTexture.on('loaded', resolve));
      }));

      console.log('PIXI textures created and loaded:');
      console.log('- Base valid:', this.baseTexture.valid, this.baseTexture.width, 'x', this.baseTexture.height);
      console.log('- Depth valid:', this.dispTexture.valid, this.dispTexture.width, 'x', this.dispTexture.height);
      console.log('- Shadow valid:', this.shadowTexture.valid, this.shadowTexture.width, 'x', this.shadowTexture.height);
      console.log('- Highlight valid:', this.highlightTexture.valid, this.highlightTexture.width, 'x', this.highlightTexture.height);

      // Create base sprite
      this.baseSprite = new PIXI.Sprite(this.baseTexture);
      
      // When canvas matches mockup dimensions, no scaling needed
      const canvasWidth = this.app.screen.width;
      const canvasHeight = this.app.screen.height;
      
      console.log('Canvas dimensions:', canvasWidth, 'x', canvasHeight);
      console.log('Mockup dimensions:', this.baseSprite.width, 'x', this.baseSprite.height);
      
      // If canvas matches mockup exactly, use 1:1 scaling and center
      if (canvasWidth === this.baseSprite.width && canvasHeight === this.baseSprite.height) {
        console.log('Canvas matches mockup - using 1:1 scaling');
        this.baseSprite.scale.set(1);
        this.baseSprite.anchor.set(0);
        this.baseSprite.position.set(0, 0);
      } else {
        // Scale sprite to fit canvas while maintaining aspect ratio
        const scaleX = canvasWidth / this.baseSprite.width;
        const scaleY = canvasHeight / this.baseSprite.height;
        const scale = Math.min(scaleX, scaleY);
        
        console.log('Sprite scaling:', scale, 'from', this.baseSprite.width, 'x', this.baseSprite.height, 'to fit', canvasWidth, 'x', canvasHeight);
        
        this.baseSprite.scale.set(scale);
        this.baseSprite.anchor.set(0.5);
        this.baseSprite.position.set(canvasWidth / 2, canvasHeight / 2);
      }

      // Create a default white texture for design
      const whiteCanvas = document.createElement('canvas');
      whiteCanvas.width = whiteCanvas.height = 1;
      const whiteCtx = whiteCanvas.getContext('2d');
      whiteCtx.fillStyle = 'white';
      whiteCtx.fillRect(0, 0, 1, 1);
      const defaultDesignTexture = PIXI.Texture.from(whiteCanvas);

      // Create and configure fabric wrap filter
      try {
        console.log('Creating FabricWrapFilter...');
        this.fabricFilter = new FabricWrapFilter();
        console.log('FabricWrapFilter created successfully');
      } catch (filterError) {
        console.error('Failed to create FabricWrapFilter:', filterError);
        throw new Error(`Shader compilation failed: ${filterError.message}`);
      }
      
      console.log('Setting up filter with textures...');
      this.fabricFilter.displacement = this.dispTexture;
      this.fabricFilter.shadow = this.shadowTexture;
      this.fabricFilter.highlight = this.highlightTexture;
      this.fabricFilter.design = defaultDesignTexture;
      
      // Set initial values
      this.fabricFilter.strength = 0.1;
      this.fabricFilter.shadowPower = 0.3;
      this.fabricFilter.highlightPower = 0.2;
      
      console.log('Filter configured with:');
      console.log('- Displacement texture valid:', this.fabricFilter.displacement.valid);
      console.log('- Shadow texture valid:', this.fabricFilter.shadow.valid);
      console.log('- Highlight texture valid:', this.fabricFilter.highlight.valid);
      console.log('- Design texture valid:', this.fabricFilter.design.valid);

      // Apply filter to sprite
      try {
        this.baseSprite.filters = [this.fabricFilter];
        console.log('Filter applied to sprite successfully');
        
        // Test render to ensure filter works
        this.app.render();
        console.log('Test render completed successfully');
      } catch (renderError) {
        console.error('Failed to apply filter or render:', renderError);
        throw new Error(`Filter application failed: ${renderError.message}`);
      }

      // Add sprite to stage
      this.app.stage.addChild(this.baseSprite);

      console.log('MockupRenderer initialized successfully');
      
    } catch (error) {
      console.error('Failed to initialize MockupRenderer:', error);
      throw error;
    }
  }

  /**
   * Set displacement strength
   */
  setDisplacementStrength(strength) {
    if (this.fabricFilter) {
      this.fabricFilter.strength = strength;
    }
  }

  /**
   * Render design at a specific position with real-time blending
   */
  async renderDesignAtPosition(designBitmap) {
    try {
      if (!this.fabricFilter || !designBitmap) {
        console.warn('Cannot render design: missing filter or design bitmap');
        return;
      }

      console.log('Rendering design at position:', designBitmap.width, 'x', designBitmap.height);
      
      // Create PIXI texture from bitmap
      const designTexture = PIXI.Texture.from(designBitmap);
      
      // Wait for texture to be ready
      await new Promise((resolve) => {
        if (designTexture.valid) {
          resolve();
        } else {
          designTexture.baseTexture.on('loaded', resolve);
        }
      });
      
      // Set design texture in filter
      this.fabricFilter.design = designTexture;
      
      // Force render
      this.app.render();
      
      console.log('Design rendered successfully');
      
    } catch (error) {
      console.error('Error rendering design at position:', error);
    }
  }

  /**
   * Generate results for all design textures
   */
  async generateResults(designFiles) {
    this.results = [];
    
    try {
      console.log('Starting result generation for', designFiles.length, 'designs');
      
      // First, temporarily remove the filter to capture original mockup
      const originalFilters = this.baseSprite.filters;
      this.baseSprite.filters = null;
      this.app.render();
      
      const originalImage = await this.captureFrame();
      console.log('Captured original mockup, length:', originalImage.length);
      
      this.results.push({
        name: 'Original Mockup',
        image: originalImage
      });

      // Restore filters for design processing
      this.baseSprite.filters = originalFilters;

      // Process each design file
      for (let i = 0; i < designFiles.length; i++) {
        const designFile = designFiles[i];
        console.log(`Processing design ${i + 1}:`, designFile.name, designFile.type, designFile.size, 'bytes');
        
        try {
          // Create bitmap from file with better error handling
          let designBitmap;
          
          if (designFile.type.startsWith('image/svg')) {
            // For SVG files, convert to PNG first
            designBitmap = await this.convertSvgToBitmap(designFile);
          } else {
            // For regular image files
            designBitmap = await createImageBitmap(designFile);
          }
          
          console.log('Design bitmap created:', designBitmap.width, 'x', designBitmap.height);
          
          // Create PIXI texture
          const designTexture = PIXI.Texture.from(designBitmap);
          
          // Wait for texture to be ready
          await new Promise((resolve) => {
            if (designTexture.valid) {
              resolve();
            } else {
              designTexture.baseTexture.on('loaded', resolve);
            }
          });
          
          console.log('Design texture created, valid:', designTexture.valid, designTexture.width, 'x', designTexture.height);
          
          // Set design texture in filter
          this.fabricFilter.design = designTexture;
          console.log('Design texture set in filter, checking filter state:');
          console.log('- Filter design texture valid:', this.fabricFilter.design.valid);
          console.log('- Filter strength:', this.fabricFilter.strength);
          
          // Force render
          this.app.render();
          console.log('Render forced after setting design texture');
          
          // Small delay to ensure rendering is complete
          await new Promise(resolve => setTimeout(resolve, 50));
          
          // Capture the result
          const resultImage = await this.captureFrame();
          console.log(`Captured design ${i + 1} result, length:`, resultImage.length);
          
          this.results.push({
            name: `Design ${i + 1}: ${designFile.name}`,
            image: resultImage
          });
          
        } catch (designError) {
          console.error(`Failed to process design ${i + 1}:`, designError);
          // Continue with next design instead of stopping
          this.results.push({
            name: `Design ${i + 1}: ${designFile.name} (Failed)`,
            image: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==' // 1x1 transparent PNG
          });
        }
      }

      console.log('All results generated successfully');
      return this.results;
      
    } catch (error) {
      console.error('Failed to generate results:', error);
      throw error;
    }
  }

  /**
   * Convert SVG file to ImageBitmap
   */
  async convertSvgToBitmap(svgFile) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const svgText = e.target.result;
        const img = new Image();
        img.onload = async () => {
          try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = img.width || 200;
            canvas.height = img.height || 200;
            ctx.drawImage(img, 0, 0);
            const bitmap = await createImageBitmap(canvas);
            resolve(bitmap);
          } catch (error) {
            reject(error);
          }
        };
        img.onerror = reject;
        img.src = 'data:image/svg+xml;base64,' + btoa(svgText);
      };
      reader.onerror = reject;
      reader.readAsText(svgFile);
    });
  }

  /**
   * Capture current frame as base64 image
   */
  async captureFrame() {
    try {
      // Force a render
      this.app.render();
      
      // Extract base64 image
      const base64 = this.app.renderer.extract.base64(this.app.stage);
      
      return base64;
    } catch (error) {
      console.error('Failed to capture frame:', error);
      throw error;
    }
  }

  /**
   * Fallback renderer using Canvas2D (when WebGL is not available)
   */
  static async renderWithCanvas2D(mockupBitmap, designBitmaps, strength = 0.1) {
    const results = [];
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = mockupBitmap.width;
    canvas.height = mockupBitmap.height;
    
    // Add original mockup
    ctx.drawImage(mockupBitmap, 0, 0);
    const originalDataUrl = canvas.toDataURL();
    results.push({
      name: 'Original Mockup',
      image: originalDataUrl
    });
    
    // Process each design
    for (let i = 0; i < designBitmaps.length; i++) {
      const designBitmap = designBitmaps[i];
      
      // Clear canvas and draw mockup
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(mockupBitmap, 0, 0);
      
      // Simple multiply blend for design
      ctx.globalCompositeOperation = 'multiply';
      ctx.globalAlpha = 0.7;
      ctx.drawImage(designBitmap, 0, 0, canvas.width, canvas.height);
      
      // Reset blend mode
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1.0;
      
      const resultDataUrl = canvas.toDataURL();
      results.push({
        name: `Design ${i + 1}`,
        image: resultDataUrl
      });
    }
    
    return results;
  }

  /**
   * Cleanup resources
   */
  destroy() {
    console.log('Destroying MockupRenderer...');
    
    try {
      // Clean up textures
      if (this.designTextures) {
        this.designTextures.forEach(texture => {
          if (texture && texture.destroy) texture.destroy(true);
        });
        this.designTextures = [];
      }
      
      // Clean up filter
      if (this.fabricFilter) {
        this.fabricFilter = null;
      }
      
      // Clean up sprite
      if (this.baseSprite) {
        if (this.baseSprite.parent) {
          this.baseSprite.parent.removeChild(this.baseSprite);
        }
        this.baseSprite.destroy(true);
        this.baseSprite = null;
      }
      
      // Clean up PIXI app
      if (this.app) {
        this.app.stage.removeChildren();
        this.app.destroy(true, { children: true, texture: true, baseTexture: true });
        this.app = null;
      }
      
      console.log('MockupRenderer destroyed successfully');
    } catch (error) {
      console.error('Error during MockupRenderer destruction:', error);
    }
  }
} 
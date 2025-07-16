# Vibe Coding - Mockup Feature

Ce projet est une fonctionnalité de génération de mockups 3D pour des produits personnalisés. Il utilise une combinaison de technologies frontend et backend pour créer des visualisations réalistes de produits.

## Fonctionnalités

- Génération de depth maps avec ZoeDepth (méthode principale)
- Fallback sur MiDaS via FAL.ai en cas d'échec
- Génération locale de depth maps en dernier recours
- Interface utilisateur réactive avec indicateur de méthode utilisée
- Traitement d'images optimisé pour les grands formats

## Structure du Projet

```
mockup-feature/
├── backend/              # Backend FastAPI
│   ├── app.py           # Point d'entrée de l'API
│   ├── requirements.txt # Dépendances Python
│   └── weights/         # Poids des modèles (non inclus dans git)
└── src/                 # Frontend React/Vite
    ├── components/      # Composants React
    └── utils/          # Utilitaires JS
```

## Installation

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 download_weights.py  # Télécharge les poids du modèle
python3 -m uvicorn app:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

## Utilisation

1. Démarrez le backend et le frontend
2. Accédez à http://localhost:5173
3. Téléchargez une image de produit
4. Le système générera automatiquement une depth map en utilisant la meilleure méthode disponible

## Technologies Utilisées

- Frontend : React, Vite, PixiJS
- Backend : FastAPI, PyTorch, ZoeDepth
- APIs : FAL.ai (fallback)

# Smart Mock-up Demo

A standalone web application that demonstrates realistic fabric wrapping effects on garment mock-ups using depth estimation and WebGL shaders.

## Features

- **Upload mockup images** - Load flat garment photos for processing
- **Multiple design support** - Apply up to 5 different designs simultaneously
- **Realistic wrapping** - Uses MiDaS v3 depth estimation for accurate fabric deformation
- **Preserved lighting** - Maintains original shadows and highlights from the mockup
- **Real-time adjustment** - Interactive displacement strength control
- **WebGL acceleration** - Fast rendering with Canvas2D fallback
- **Instant results** - Process multiple designs in under 200ms

## Tech Stack

- **Frontend**: React 18 + Vite
- **Rendering**: PixiJS v7 with custom WebGL shaders
- **Depth Estimation**: MiDaS v3-small via Hugging Face Inference API or FAL.ai
- **Image Processing**: Canvas2D for preprocessing and lighting mask extraction

## Quick Start

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open browser** and navigate to `http://localhost:3000`

## Usage

1. **Select a mockup image** - Choose a flat garment photo (JPG/PNG)
2. **Select design images** - Pick up to 5 design files (PNG/SVG recommended)
3. **Adjust displacement strength** - Control how much the design wraps to the fabric
4. **Click "Generate Mock-ups"** - Process and view results

## Configuration

### API Keys (Optional)

For production use, configure API keys in `src/utils/depthEstimation.js`:

**Hugging Face** (recommended):
```javascript
const response = await fetch("https://api-inference.huggingface.co/models/Intel/dpt-large", {
  headers: {
    "Authorization": "Bearer YOUR_HF_TOKEN_HERE",
    // ...
  }
});
```

**FAL.ai** (alternative):
```javascript
const response = await fetch('https://fal.run/models/midas-v3-small', {
  headers: {
    'Authorization': 'Key YOUR_FAL_KEY_HERE',
    // ...
  }
});
```

### Fallback Mode

Without API keys, the application uses a radial gradient as a fallback depth map. This still provides basic wrapping effects but with reduced realism.

## Architecture

### Core Components

1. **Depth Estimation** (`src/utils/depthEstimation.js`)
   - Calls MiDaS v3-small model via API
   - Processes depth maps for WebGL usage
   - Provides fallback depth generation

2. **Lighting Masks** (`src/utils/lightingMasks.js`)
   - Extracts shadow and highlight information
   - Converts RGB to LAB color space
   - Creates grayscale masks for shader use

3. **PixiJS Renderer** (`src/utils/pixiRenderer.js`)
   - Custom WebGL fragment shader
   - Real-time texture compositing
   - Frame capture for result generation

4. **React App** (`src/App.jsx`)
   - File upload handling
   - State management
   - UI controls and result display

### Shader Pipeline

The custom WebGL fragment shader performs these operations per pixel:

1. **Displacement Sampling**: Read depth map and calculate warp offset
2. **Texture Warping**: Sample design texture at warped coordinates
3. **Composition**: Blend design onto base mockup
4. **Shadow Application**: Darken based on shadow mask
5. **Highlight Application**: Brighten based on highlight mask

## Performance

- **Preprocessing**: ~100ms for depth estimation (API dependent)
- **Rendering**: <20ms per design on mid-range hardware
- **Total Processing**: <200ms for 5 designs
- **Memory**: Efficient texture reuse and cleanup

## Browser Compatibility

- **WebGL 2.0**: Modern browsers (Chrome 56+, Firefox 51+, Safari 15+)
- **Canvas2D Fallback**: All modern browsers
- **File API**: All modern browsers

## Development

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Project Structure

```
src/
├── App.jsx                 # Main React component
├── main.jsx               # React entry point
├── index.css              # Global styles
└── utils/
    ├── depthEstimation.js # Depth map generation
    ├── lightingMasks.js   # Shadow/highlight extraction
    └── pixiRenderer.js    # WebGL rendering engine
```

## Customization

### Shader Parameters

Modify shader uniforms in `pixiRenderer.js`:

```javascript
uStrength: { value: 0.1, type: '1f' },        // Displacement strength
uShadowPower: { value: 0.3, type: '1f' },     // Shadow intensity
uHighlightPower: { value: 0.2, type: '1f' }   // Highlight intensity
```

### Processing Pipeline

Extend the processing pipeline by modifying:

- `buildLightingMasks()` for custom lighting extraction
- `processDepthMap()` for depth map enhancement
- `FabricWrapFilter` for additional shader effects

## Troubleshooting

### Common Issues

1. **WebGL not available**: Application falls back to Canvas2D rendering
2. **API rate limits**: Depth estimation uses fallback gradient
3. **Large image files**: Consider resizing images before upload
4. **Performance issues**: Reduce displacement strength or image size

### Error Messages

- `"Depth estimation failed"`: Check API keys or network connection
- `"WebGL not available"`: Browser doesn't support WebGL 2.0
- `"Processing failed"`: File format or memory issues

## License

This project is for demonstration purposes. Commercial use requires proper API key configuration and licensing.

## Credits

- **Depth Estimation**: Intel MiDaS v3-small model
- **Rendering**: PixiJS WebGL framework
- **UI Framework**: React + Vite

---

For support or questions, please check the browser console for detailed error messages. 
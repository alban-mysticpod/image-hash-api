# Contribution Guide

Thank you for your interest in contributing to this project! Here are some guidelines to help you get started.

## Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/vibe-coding.git
cd vibe-coding/mockup-feature
```

2. Setup the backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python download_weights.py
```

3. Setup the frontend:
```bash
cd ..
npm install
```

4. Create a `.env` file based on `.env.example` and add your API keys.

## Starting the Project

1. Start the backend:
```bash
cd backend
source venv/bin/activate
python -m uvicorn app:app --reload
```

2. In another terminal, start the frontend:
```bash
npm run dev
```

## Project Structure

- `backend/` : FastAPI API with ZoeDepth
- `src/` : React/Vite frontend
- `weights/` : Model weights (downloaded automatically)

## Contribution Process

1. Create a branch for your feature:
```bash
git checkout -b feature/feature-name
```

2. Make your changes and test them.

3. Commit your changes:
```bash
git add .
git commit -m "Clear description of changes"
```

4. Push your branch:
```bash
git push origin feature/feature-name
```

5. Open a Pull Request on GitHub.

## Code Standards

- Use descriptive variable and function names
- Comment your code when necessary
- Follow PEP 8 conventions for Python
- Use ESLint for JavaScript/TypeScript

## Testing

- Test your changes locally before submitting a PR
- Make sure all existing tests pass
- Add tests for new features

## Questions?

If you have questions, feel free to open an issue on GitHub. 
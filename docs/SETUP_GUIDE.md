# Setup Guide

This guide will walk you through setting up the Fashion Labs project from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**
- **Git** (optional, for cloning)

### Verify Installation

```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check npm version
npm --version
```

---

## Project Structure

After setup, your project should look like this:

```
Fashion Labs/
├── FRSCA/                      # Backend
│   ├── api/
│   │   └── main.py
│   ├── scripts/
│   │   ├── generate_outfit.py
│   │   ├── slot_alternatives.py
│   │   ├── rules.py
│   │   ├── slots.py
│   │   ├── extract_embeddings.py
│   │   └── build_metadata.py
│   ├── processed/              # Generated data
│   │   ├── embeddings.npy
│   │   ├── image_names.npy
│   │   └── metadata.json
│   ├── train_images/           # Fashion item images
│   └── test_images/
│
└── frsca-frontend/             # Frontend
    ├── src/
    │   ├── App.js
    │   ├── index.css
    │   └── index.js
    ├── public/
    └── package.json
```

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd "Fashion Labs/FRSCA"
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install fastapi uvicorn numpy scikit-learn pydantic python-multipart
```

**Or use requirements.txt if available:**
```bash
pip install -r requirements.txt
```

### Step 4: Verify Data Files

Ensure the following files exist in the `processed/` directory:

- `embeddings.npy` - Pre-computed image embeddings
- `image_names.npy` - Corresponding image filenames
- `metadata.json` - Item metadata

**If these files don't exist**, you'll need to generate them:

#### Generate Embeddings (if needed)

1. Ensure you have images in `train_images/`
2. Run the embedding extraction script:
   ```bash
   cd scripts
   python extract_embeddings.py
   ```

#### Generate Metadata (if needed)

```bash
cd scripts
python build_metadata.py
```

### Step 5: Start the Backend Server

```bash
cd api
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Test the Backend

Open your browser and navigate to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: Try accessing an image: http://localhost:8000/images/[any-image-name].jpg

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

Open a **new terminal** (keep the backend running) and navigate to:

```bash
cd "Fashion Labs/frsca-frontend"
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install all dependencies listed in `package.json`:
- React
- React DOM
- React Scripts
- Testing libraries

**Expected output:**
```
added XXX packages in XXs
```

### Step 3: Configure API Base URL (if needed)

By default, the frontend connects to `http://localhost:8000`. If your backend runs on a different port, update `src/App.js`:

```javascript
const API_BASE = "http://localhost:8000";  // Change if needed
```

### Step 4: Start the Development Server

```bash
npm start
```

The app will automatically open in your browser at:
```
http://localhost:3000
```

**Expected output:**
```
Compiled successfully!

You can now view frsca-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

---

## Verification

### Test the Complete Flow

1. **Open the app** at http://localhost:3000
2. **Select preferences**:
   - Gender: Men or Women
   - Season: Winter or Summer
   - Occasion: Casual or Formal
3. **Click "Generate Outfit"**
4. **Verify**:
   - Outfit images load correctly
   - You can click "Change" to see alternatives
   - You can save outfits to "My Closet"

### Common Issues

#### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
pip install fastapi uvicorn
```

**Problem**: `FileNotFoundError: [Errno 2] No such file or directory: 'processed/embeddings.npy'`
```bash
# Solution: Generate embeddings
cd scripts
python extract_embeddings.py
```

**Problem**: Port 8000 already in use
```bash
# Solution: Use a different port
uvicorn main:app --reload --port 8001

# Then update frontend API_BASE to http://localhost:8001
```

#### Frontend Issues

**Problem**: `npm: command not found`
```bash
# Solution: Install Node.js from https://nodejs.org/
```

**Problem**: CORS errors in browser console
```bash
# Solution: Ensure backend CORS is configured correctly
# Check api/main.py for CORSMiddleware settings
```

**Problem**: Images not loading
```bash
# Solution: 
# 1. Verify backend is running
# 2. Check that train_images/ directory exists
# 3. Verify image paths in metadata
```

**Problem**: Port 3000 already in use
```bash
# Solution: The app will prompt you to use a different port
# Press 'y' to accept
```

---

## Development Workflow

### Running Both Servers

You'll need **two terminal windows**:

**Terminal 1 - Backend:**
```bash
cd "Fashion Labs/FRSCA/api"
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd "Fashion Labs/frsca-frontend"
npm start
```

### Making Changes

**Backend Changes:**
- Edit Python files in `FRSCA/scripts/` or `FRSCA/api/`
- Server auto-reloads with `--reload` flag
- Check terminal for errors

**Frontend Changes:**
- Edit files in `frsca-frontend/src/`
- Browser auto-refreshes
- Check browser console for errors

---

## Production Build

### Backend Production

```bash
cd "Fashion Labs/FRSCA/api"
uvicorn main:app --host 0.0.0.0 --port 8000
```

**For production deployment:**
- Use a process manager (PM2, systemd)
- Set up reverse proxy (nginx)
- Enable HTTPS
- Configure proper CORS

### Frontend Production

```bash
cd "Fashion Labs/frsca-frontend"
npm run build
```

This creates an optimized production build in the `build/` folder.

**Serve the build:**
```bash
npm install -g serve
serve -s build -p 3000
```

---

## Environment Variables (Optional)

Create a `.env` file for configuration:

**Backend (.env):**
```
API_HOST=0.0.0.0
API_PORT=8000
IMAGES_DIR=../train_images
PROCESSED_DIR=../processed
```

**Frontend (.env):**
```
REACT_APP_API_BASE=http://localhost:8000
```

---

## Database Setup (Future)

Currently, the app uses:
- **LocalStorage** for frontend data persistence
- **In-memory** data for backend

For production, consider:
- PostgreSQL for user data
- Redis for caching
- S3/CDN for images
- Vector database for embeddings (Pinecone, Weaviate)

---

## Next Steps

After successful setup:

1. **Explore the code** - Read through `App.js` and `main.py`
2. **Test features** - Generate outfits, save to closet, try alternatives
3. **Read documentation** - Check `API_DOCUMENTATION.md` and `ARCHITECTURE.md`
4. **Make modifications** - Try adding new features
5. **Run tests** - Set up testing framework

---

## Getting Help

If you encounter issues:

1. **Check the logs** - Look at terminal output for errors
2. **Verify prerequisites** - Ensure all dependencies are installed
3. **Check file paths** - Ensure all data files exist
4. **Review documentation** - Read README.md and API docs
5. **Check browser console** - Look for JavaScript errors

---

## Uninstallation

### Remove Backend Environment

```bash
cd "Fashion Labs/FRSCA"
deactivate  # If virtual environment is active
rm -rf venv/  # Remove virtual environment
```

### Remove Frontend Dependencies

```bash
cd "Fashion Labs/frsca-frontend"
rm -rf node_modules/
rm package-lock.json
```

---

**You're all set! Happy coding! 🚀**

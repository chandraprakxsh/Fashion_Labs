# Fashion Labs 👔

**Fashion Labs** is an AI-powered outfit recommendation system that generates personalized fashion outfits based on user preferences including gender, season, and occasion. The system uses deep learning embeddings to create cohesive outfit combinations and provides a digital closet for saving favorite looks.

![Fashion Labs](https://img.shields.io/badge/React-19.2.3-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green) ![Python](https://img.shields.io/badge/Python-3.8+-yellow)

## 🌟 Features

### Frontend (React)
- **Outfit Generation**: Generate complete outfits based on gender, season, and occasion
- **Interactive Customization**: Swap individual clothing items with AI-recommended alternatives
- **Digital Closet**: Save and manage your favorite outfit combinations
- **Outfit Naming**: Organize saved outfits with custom names
- **Responsive Design**: Modern, animated UI with glassmorphism effects
- **Real-time Preview**: View outfit images with instant updates

### Backend (Python + FastAPI)
- **Deep Learning Embeddings**: Uses pre-trained vision models for fashion item similarity
- **Rule-Based Engine**: Enforces season, occasion, and style constraints
- **Slot-Based System**: Organizes outfits by TOP, BOTTOM, and OUTERWEAR slots
- **Smart Recommendations**: Cosine similarity-based item matching
- **RESTful API**: Clean, documented API endpoints

## 🏗️ Architecture

```
Fashion Labs/
├── FRSCA/                    # Backend (Python)
│   ├── api/
│   │   └── main.py          # FastAPI server
│   ├── scripts/
│   │   ├── generate_outfit.py    # Core outfit generation logic
│   │   ├── slot_alternatives.py  # Alternative item recommendations
│   │   ├── rules.py              # Season/occasion constraints
│   │   ├── slots.py              # Slot mapping utilities
│   │   ├── extract_embeddings.py # Feature extraction
│   │   └── build_metadata.py     # Data preprocessing
│   ├── processed/           # Processed data (embeddings, metadata)
│   ├── train_images/        # Fashion item images
│   └── test_images/         # Test dataset
│
└── frsca-frontend/          # Frontend (React)
    ├── src/
    │   ├── App.js          # Main application component
    │   ├── index.css       # Styles and animations
    │   └── index.js        # React entry point
    └── public/             # Static assets
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **npm** or **yarn**

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd "Fashion Labs/FRSCA"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn numpy scikit-learn pydantic
   ```

3. **Ensure processed data exists:**
   - `processed/embeddings.npy` - Pre-computed image embeddings
   - `processed/image_names.npy` - Corresponding image filenames
   - `processed/metadata.json` - Item metadata (category, gender, season, etc.)

4. **Start the FastAPI server:**
   ```bash
   cd api
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd "Fashion Labs/frsca-frontend"
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

## 📖 Usage

### Generating an Outfit

1. Select your preferences:
   - **Gender**: Men or Women
   - **Season**: Winter or Summer
   - **Occasion**: Casual or Formal

2. Click **"Generate Outfit"** to create a complete outfit

3. View the generated outfit with images for each slot (TOP, BOTTOM, OUTERWEAR)

### Customizing Items

1. Click **"Change"** on any clothing item
2. Browse AI-recommended alternatives with similarity scores
3. Click an alternative to swap it into your outfit

### Saving to Digital Closet

1. Click **"Save to Closet"** on a generated outfit
2. Optionally name your outfit
3. Access saved outfits from **"My Closet"** in the header
4. Click on outfit names to rename them
5. Delete outfits you no longer want

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Generate Outfit
**POST** `/generate-outfit`

Generate a complete outfit based on user preferences.

**Request Body:**
```json
{
  "gender": "men",
  "season": "winter",
  "occasion": "casual",
  "style": null
}
```

**Response:**
```json
{
  "outfit": {
    "TOP": {
      "image": "12345.jpg",
      "category": "top",
      "gender": "men"
    },
    "BOTTOM": {
      "image": "67890.jpg",
      "category": "bottom",
      "gender": "men"
    },
    "OUTERWEAR": {
      "image": "11223.jpg",
      "category": "outerwear",
      "gender": "men"
    }
  }
}
```

#### 2. Get Slot Alternatives
**POST** `/slot-alternatives`

Get alternative items for a specific outfit slot.

**Request Body:**
```json
{
  "current_outfit": {
    "TOP": { "image": "12345.jpg", "category": "top", "gender": "men" },
    "BOTTOM": { "image": "67890.jpg", "category": "bottom", "gender": "men" }
  },
  "slot": "TOP",
  "gender": "men",
  "season": "winter",
  "occasion": "casual",
  "top_k": 5
}
```

**Response:**
```json
{
  "slot": "TOP",
  "alternatives": [
    {
      "image": "54321.jpg",
      "category": "top",
      "gender": "men",
      "score": 0.923
    },
    ...
  ]
}
```

#### 3. Static Images
**GET** `/images/{filename}`

Serve fashion item images.

**Example:**
```
http://localhost:8000/images/12345.jpg
```

## 🧠 How It Works

### 1. **Feature Extraction**
- Fashion item images are processed using a pre-trained vision model
- Each item is converted to a high-dimensional embedding vector
- Embeddings capture visual features like color, pattern, and style

### 2. **Rule-Based Filtering**
The system enforces constraints based on:

**Season Rules:**
- **Summer**: No outerwear, allows short and long coverage
- **Winter**: Requires outerwear, only long coverage

**Occasion Rules:**
- **Casual**: Excludes blazers
- **Formal**: Only items tagged with "formal" usage

### 3. **Outfit Generation Algorithm**
1. Filter items by gender, season, and occasion
2. Select TOP as anchor using centroid similarity
3. For each remaining slot (BOTTOM, OUTERWEAR):
   - Calculate similarity to existing outfit items
   - Select the most compatible item

### 4. **Alternative Recommendations**
- When swapping an item, the system finds similar alternatives
- Uses cosine similarity between embeddings
- Filters by the same rules (gender, season, occasion)
- Returns top-k most similar items with scores

## 🎨 Frontend Features

### Modern UI/UX
- **Dot Matrix Background**: Interactive animated background
- **Glassmorphism Cards**: Modern frosted glass effect
- **Loading States**: Visual feedback during API calls
- **Smooth Animations**: Hover effects and transitions
- **Responsive Layout**: Grid-based outfit display

### State Management
- React hooks for local state
- LocalStorage persistence for saved outfits
- Real-time UI updates

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **NumPy**: Numerical computing for embeddings
- **scikit-learn**: Cosine similarity calculations
- **Pydantic**: Data validation and serialization

### Frontend
- **React 19**: UI library with hooks
- **CSS3**: Modern styling with animations
- **Fetch API**: HTTP requests to backend

## 📁 Data Structure

### Metadata Format
Each fashion item in `metadata.json` contains:
```json
{
  "category": "top",
  "subcategory": "t-shirt",
  "gender": "men",
  "coverage": "short",
  "usage": ["casual", "formal"],
  "fit": "regular"
}
```

### Processed Files
- **embeddings.npy**: NumPy array of shape `(N, D)` where N is number of items and D is embedding dimension
- **image_names.npy**: Array of image filenames corresponding to embeddings
- **metadata.json**: List of metadata dictionaries for each item

## 🔧 Configuration

### API Base URL
Update in `frsca-frontend/src/App.js`:
```javascript
const API_BASE = "http://localhost:8000";
```

### CORS Settings
Configured in `FRSCA/api/main.py` for development (allows all origins)

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError` when starting API
- **Solution**: Ensure all dependencies are installed and you're in the correct directory

**Problem**: `FileNotFoundError` for processed data
- **Solution**: Run preprocessing scripts to generate embeddings and metadata

### Frontend Issues

**Problem**: CORS errors in browser console
- **Solution**: Ensure backend is running and CORS is properly configured

**Problem**: Images not loading
- **Solution**: Verify backend is serving static files and image paths are correct

## 📝 Future Enhancements

- [ ] Add more seasons (Spring, Fall, Monsoon)
- [ ] Implement style preferences (Minimal, Street, Formal)
- [ ] Add footwear and accessories slots
- [ ] User authentication and cloud storage
- [ ] Social sharing of outfits
- [ ] AI-powered outfit ratings and feedback
- [ ] Mobile app version

## 📄 License

This project is for educational and personal use.

## 👥 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Built with ❤️ using React and FastAPI**

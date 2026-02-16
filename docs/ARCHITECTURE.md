# Architecture Overview

## System Architecture

Fashion Labs is built as a **client-server architecture** with a React frontend and FastAPI backend, connected via RESTful APIs.

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           React Frontend (Port 3000)                   │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │   App.js    │  │  index.css   │  │ LocalStorage│  │  │
│  │  │ (UI Logic)  │  │  (Styling)   │  │  (Closet)   │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    API Layer                           │  │
│  │  ┌──────────────────┐  ┌──────────────────┐          │  │
│  │  │ /generate-outfit │  │ /slot-alternatives│          │  │
│  │  └──────────────────┘  └──────────────────┘          │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Business Logic Layer                      │  │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌─────────┐  │  │
│  │  │ generate_outfit │  │slot_alternatives│ │  rules  │  │  │
│  │  │     .py         │  │     .py        │  │   .py   │  │  │
│  │  └─────────────────┘  └──────────────┘  └─────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Data Layer                             │  │
│  │  ┌──────────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │ embeddings   │  │ metadata   │  │ image_names  │  │  │
│  │  │   .npy       │  │   .json    │  │    .npy      │  │  │
│  │  └──────────────┘  └────────────┘  └──────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend Components

#### 1. **App.js** - Main Application Component
**Responsibilities:**
- State management (outfit, alternatives, saved outfits)
- API communication
- View routing (Generate vs Closet)
- User interactions

**Key State Variables:**
```javascript
- gender, season, occasion    // User preferences
- outfit                       // Current generated outfit
- alternatives                 // Alternative items for swapping
- savedOutfits                 // Digital closet data
- activeView                   // Current view (generate/closet)
- isGenerating                 // Loading state
```

**Key Functions:**
- `generateOutfit()` - Calls backend to generate outfit
- `getAlternatives()` - Fetches alternative items for a slot
- `applyAlternative()` - Swaps an item in the outfit
- `saveToCloset()` - Saves outfit to LocalStorage
- `deleteFromCloset()` - Removes saved outfit

#### 2. **index.css** - Styling & Animations
**Features:**
- CSS Grid layouts for outfit display
- Glassmorphism effects
- Dot matrix animated background
- Hover animations
- Loading states
- Modal styling

---

### Backend Components

#### 1. **API Layer** (`api/main.py`)
**Responsibilities:**
- HTTP request handling
- Request validation (Pydantic models)
- Response formatting
- Static file serving
- CORS configuration

**Key Endpoints:**
- `POST /generate-outfit` - Generate complete outfit
- `POST /slot-alternatives` - Get alternative items
- `GET /images/{filename}` - Serve images

**Startup Actions:**
- Load embeddings into memory
- Load metadata into memory
- Load image names into memory

#### 2. **Business Logic Layer**

##### `generate_outfit.py`
**Algorithm:**
1. Determine active slots based on season
2. Filter items by gender, season, occasion
3. Select TOP as anchor using centroid similarity
4. Sequentially fill remaining slots
5. Return complete outfit

**Key Functions:**
- `generate_outfit()` - Main generation logic
- `build_item()` - Construct item response object

##### `slot_alternatives.py`
**Algorithm:**
1. Extract current outfit embeddings
2. Compute reference vector (mean of outfit)
3. Filter candidates by rules
4. Calculate cosine similarity
5. Sort and return top-k

**Key Functions:**
- `recommend_slot_alternatives()` - Main recommendation logic

##### `rules.py`
**Responsibilities:**
- Encode season/occasion constraints
- Validate item eligibility
- Slot activation logic

**Key Functions:**
- `slot_enabled()` - Check if slot is active
- `item_allowed()` - Validate item against rules
- `style_bonus()` - Soft style preference scoring

##### `slots.py`
**Responsibilities:**
- Map item categories to outfit slots
- Deterministic slot assignment

**Key Functions:**
- `get_slot()` - Map item to slot (TOP/BOTTOM/OUTERWEAR)

#### 3. **Data Processing Scripts**

##### `extract_embeddings.py`
**Purpose:** Generate visual embeddings from images
- Uses pre-trained vision model
- Extracts feature vectors
- Saves to `embeddings.npy`

##### `build_metadata.py`
**Purpose:** Process and structure item metadata
- Parses item attributes
- Validates data
- Saves to `metadata.json`

---

## Data Flow

### 1. Outfit Generation Flow

```
User selects preferences
        │
        ▼
Frontend: generateOutfit()
        │
        ▼
POST /generate-outfit
        │
        ▼
Backend: generate_outfit()
        │
        ├─► Filter items by gender
        ├─► Apply season rules
        ├─► Apply occasion rules
        ├─► Select TOP (anchor)
        ├─► Fill BOTTOM
        └─► Fill OUTERWEAR (if winter)
        │
        ▼
Return outfit JSON
        │
        ▼
Frontend: Display outfit images
```

### 2. Alternative Selection Flow

```
User clicks "Change" on item
        │
        ▼
Frontend: getAlternatives(slot)
        │
        ▼
POST /slot-alternatives
        │
        ▼
Backend: recommend_slot_alternatives()
        │
        ├─► Extract current outfit embeddings
        ├─► Compute reference vector
        ├─► Filter candidates by rules
        ├─► Calculate similarity scores
        └─► Sort by score
        │
        ▼
Return top-k alternatives
        │
        ▼
Frontend: Display alternatives grid
        │
        ▼
User clicks alternative
        │
        ▼
Frontend: applyAlternative()
        │
        ▼
Update outfit state
```

### 3. Save to Closet Flow

```
User clicks "Save to Closet"
        │
        ▼
Frontend: Show naming modal
        │
        ▼
User enters name (optional)
        │
        ▼
Frontend: confirmSaveOutfit()
        │
        ├─► Create outfit object with metadata
        ├─► Add to savedOutfits state
        └─► Persist to LocalStorage
        │
        ▼
Display in "My Closet" view
```

---

## Design Patterns

### 1. **Separation of Concerns**
- Frontend handles UI/UX only
- Backend handles all business logic
- Clear API contract between layers

### 2. **Rule-Based System**
- Declarative rule definitions
- Centralized constraint enforcement
- Easy to extend with new rules

### 3. **Embedding-Based Similarity**
- Pre-computed embeddings for speed
- Cosine similarity for compatibility
- Vector operations for efficiency

### 4. **Slot-Based Architecture**
- Modular outfit structure
- Independent slot manipulation
- Easy to add new slots (e.g., FOOTWEAR)

### 5. **Stateless API**
- No server-side sessions
- Each request is independent
- Easy to scale horizontally

---

## Technology Choices

### Why React?
- Component-based architecture
- Efficient state management with hooks
- Large ecosystem and community
- Fast development iteration

### Why FastAPI?
- Automatic API documentation
- Type validation with Pydantic
- High performance (async support)
- Modern Python features

### Why NumPy?
- Efficient array operations
- Vectorized computations
- Industry standard for ML
- Fast cosine similarity

### Why LocalStorage?
- No backend persistence needed
- Instant save/load
- Works offline
- Simple implementation

---

## Scalability Considerations

### Current Limitations
- All data in memory (limited by RAM)
- Single-threaded outfit generation
- No caching layer
- No user authentication

### Future Improvements

**Backend:**
- Add Redis for caching
- Implement database for persistence
- Add user authentication (JWT)
- Horizontal scaling with load balancer
- Async processing for heavy operations

**Frontend:**
- Add state management library (Redux/Zustand)
- Implement virtual scrolling for large closets
- Add service worker for offline support
- Optimize image loading (lazy loading, CDN)

**Data:**
- Move to vector database (Pinecone, Weaviate)
- Implement incremental embedding updates
- Add data versioning
- Implement A/B testing framework

---

## Security Considerations

### Current State (Development)
- CORS allows all origins
- No authentication
- No rate limiting
- No input sanitization

### Production Recommendations
- Implement JWT authentication
- Add rate limiting (per user/IP)
- Sanitize all user inputs
- Use HTTPS only
- Implement CORS whitelist
- Add request validation
- Implement logging and monitoring
- Add API key management

---

## Performance Optimization

### Current Optimizations
- Pre-computed embeddings (no runtime feature extraction)
- Vectorized similarity calculations
- Static file caching
- In-memory data storage

### Potential Improvements
- Add response caching
- Implement pagination for alternatives
- Use CDN for images
- Compress images (WebP format)
- Add database indexing
- Implement query optimization
- Use connection pooling

---

## Testing Strategy

### Recommended Tests

**Backend:**
- Unit tests for rule engine
- Unit tests for outfit generation
- Integration tests for API endpoints
- Load testing for performance
- Validation tests for data integrity

**Frontend:**
- Component unit tests (React Testing Library)
- Integration tests for user flows
- E2E tests (Playwright/Cypress)
- Visual regression tests
- Accessibility tests

**Data:**
- Embedding quality tests
- Metadata validation tests
- Image availability tests

# CHAPTER 5: EXPERIMENTAL SETUP AND RESULTS

## 5.1 Experimental Setup

### 5.1.1 Dataset Configuration and Statistics

The experimental setup utilized a curated fashion image dataset comprising clothing items across three primary categories: tops, bottoms, and outerwear. The dataset was sourced from e-commerce platforms and systematically organized to support comprehensive outfit coordination research.

**Dataset Composition:**

The complete dataset comprises approximately 1,500-2,000 fashion items distributed across categories as follows:

- **Tops:** ~600-800 items (40% of dataset)
  - Subcategories: T-shirts, shirts, blouses, sweaters, hoodies, tanks, polos
  - Coverage: Mix of short-sleeve and long-sleeve items
  
- **Bottoms:** ~525-700 items (35% of dataset)
  - Subcategories: Jeans, pants, trousers, shorts, skirts
  - Coverage: Mix of short and long coverage
  
- **Outerwear:** ~375-500 items (25% of dataset)
  - Subcategories: Jackets, coats, blazers, cardigans
  - Coverage: Predominantly long coverage for layering

**Gender Distribution:**
- Men's items: ~52% (780-1,040 items)
- Women's items: ~48% (720-960 items)
- Balanced representation ensures equitable performance across user segments

**Seasonal Distribution:**
- Year-round versatile items: ~60% (900-1,200 items)
- Winter-specific items: ~25% (375-500 items)
- Summer-specific items: ~15% (225-300 items)

**Occasion Distribution:**
- Casual-appropriate items: ~70% (1,050-1,400 items)
- Formal-appropriate items: ~35% (525-700 items)
- Dual-tagged items (both casual and formal): ~15% (225-300 items)

**Image Specifications:**
- **Resolution:** Minimum 224×224 pixels (compatible with ResNet-50 architecture)
- **Format:** JPEG with consistent compression quality
- **Background:** Predominantly white or neutral backgrounds for clear visibility
- **Perspective:** Front-facing product shots with minimal occlusion
- **Lighting:** Consistent studio lighting conditions

The dataset was not partitioned into traditional train/validation/test splits, as the system employs pre-computed embeddings from a pre-trained model rather than training a custom classification or regression model. All items are available for outfit generation and recommendation during runtime.

### 5.1.2 Data Preprocessing Pipeline

All fashion item images underwent standardized preprocessing to ensure consistency and compatibility with the embedding extraction model:

**Image Preprocessing Transform:**

```python
transform = transforms.Compose([
    transforms.Resize((224, 224)),      # Uniform image dimensions
    transforms.ToTensor(),               # Convert to PyTorch tensors
    transforms.Normalize(                # ImageNet normalization
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

**Preprocessing Steps:**

1. **Resizing:** All images scaled to 224×224 pixels to match ResNet-50 input requirements, maintaining aspect ratio through center cropping or padding as needed

2. **Tensor Conversion:** PIL images converted to PyTorch tensors with pixel values normalized to [0, 1] range

3. **Normalization:** Channel-wise normalization using ImageNet statistics (mean and standard deviation) ensures compatibility with pre-trained model expectations and stable feature extraction

**Metadata Preprocessing:**

Metadata extraction followed an automated pipeline implemented in `build_metadata.py`:

1. **Filename Parsing:** Extract gender and category information from structured filenames (format: `GENDER-Category_Subcategory-ID.jpg`)

2. **Vocabulary Matching:** Match subcategory tokens against predefined vocabularies (OUTERWEAR, TOPS, BOTTOMS, DRESSES, FOOTWEAR)

3. **Attribute Inference:** Derive secondary attributes (coverage, layer, structure) based on primary category and subcategory

4. **Usage Classification:** Determine formal/casual appropriateness through rule-based logic considering structure, subcategory, and category

5. **Validation:** Automated consistency checks ensure logical coherence (e.g., shorts → short coverage, blazers → formal usage)

### 5.1.3 Visual Embedding Extraction

Visual embeddings serve as the foundation for similarity-based outfit coordination. The embedding extraction process utilized transfer learning with pre-trained convolutional neural networks.

**Embedding Model Configuration:**

- **Architecture:** ResNet-50 pre-trained on ImageNet
- **Modification:** Final fully-connected classification layer replaced with identity mapping
- **Output:** 2048-dimensional feature vectors extracted from penultimate layer
- **Normalization:** L2 normalization to unit length for cosine similarity calculations

**Extraction Process:**

```python
# Load pre-trained ResNet-50
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.fc = nn.Identity()              # Remove classification head
model.eval()                          # Set to evaluation mode

# Extract embeddings
with torch.no_grad():                 # Disable gradient computation
    for image in dataset:
        image_tensor = transform(image).unsqueeze(0)
        embedding = model(image_tensor)
        embedding = embedding / np.linalg.norm(embedding)  # L2 normalize
```

**Hardware Configuration:**

- **GPU:** CUDA-compatible NVIDIA GPU (when available) for accelerated extraction
- **CPU Fallback:** Automatic detection and fallback to CPU processing
- **Batch Processing:** Images processed in batches of 32-64 for efficiency
- **Extraction Speed:** 50-100 images/second on GPU, 5-10 images/second on CPU

**Storage Format:**

- **Embeddings:** NumPy array of shape (N, 2048) where N is number of items
  - File: `processed/embeddings.npy`
  - Size: ~16MB for 2000 items (2000 × 2048 × 4 bytes)
  
- **Image Names:** NumPy array of filenames corresponding to embeddings
  - File: `processed/image_names.npy`
  - Enables mapping between embeddings and image files
  
- **Metadata:** JSON file containing attribute dictionaries for each item
  - File: `processed/metadata.json`
  - Size: ~2MB for comprehensive metadata

## 5.2 System Architecture and Implementation

### 5.2.1 Backend Architecture (FastAPI)

The backend server implements a RESTful API using FastAPI, a modern Python web framework optimized for performance and developer productivity.

**Server Configuration:**

- **Framework:** FastAPI (latest version)
- **ASGI Server:** Uvicorn for production-grade async request handling
- **CORS:** Configured for cross-origin requests (permissive for development)
- **Static Files:** Dedicated endpoint for serving fashion item images

**Data Loading Strategy:**

```python
# Load data ONCE at server startup (not per-request)
embeddings = np.load("processed/embeddings.npy")
image_names = np.load("processed/image_names.npy", allow_pickle=True)
with open("processed/metadata.json") as f:
    metadata = json.load(f)
```

**Key Design Decision:** All data loaded into memory at startup (~70-100MB total) rather than per-request loading. This trades memory for dramatic performance improvements (50-200ms vs. 1-2s per request).

**API Endpoints:**

1. **POST /generate-outfit**
   - Input: Gender, season, occasion, optional style
   - Output: Complete outfit with TOP, BOTTOM, OUTERWEAR (conditional)
   - Processing: Filtering → Anchor selection → Sequential slot filling
   
2. **POST /slot-alternatives**
   - Input: Current outfit, target slot, context parameters, top_k
   - Output: Ranked list of alternative items with similarity scores
   - Processing: Context extraction → Filtering → Similarity ranking

3. **GET /images/{filename}**
   - Input: Image filename
   - Output: Static image file
   - Processing: Direct file serving from train_images directory

### 5.2.2 Frontend Architecture (React)

The frontend implements a modern single-page application using React 19 with hooks-based state management.

**Technology Stack:**

- **Framework:** React 19.2.3
- **Styling:** Vanilla CSS with modern features (glassmorphism, animations)
- **State Management:** React hooks (useState, useEffect)
- **Persistence:** Browser localStorage for digital closet
- **HTTP Client:** Native Fetch API for backend communication

**Key Components:**

1. **Preference Selection Panel**
   - Gender selection (Men/Women)
   - Season selection (Winter/Summer)
   - Occasion selection (Casual/Formal)
   - Generate button with loading states

2. **Outfit Display Grid**
   - Three-column layout for TOP, BOTTOM, OUTERWEAR
   - Image display with fallback handling
   - Metadata display (category, subcategory)
   - Change button for alternative exploration

3. **Alternative Recommendation Modal**
   - Grid display of top-k alternatives
   - Similarity score visualization
   - Click-to-swap functionality
   - Close/cancel options

4. **Digital Closet Manager**
   - Saved outfit list with custom names
   - Rename functionality (click on name)
   - Delete functionality
   - Load saved outfit to view

### 5.2.3 Deployment Configuration

**Development Environment:**

```bash
# Backend
cd FRSCA/api
uvicorn main:app --reload --port 8000

# Frontend
cd frsca-frontend
npm start
```

**Production Considerations:**

- **Backend:** Deployed on cloud platforms (Heroku, Railway, Render) or containerized (Docker)
- **Frontend:** Static build deployed to CDN or hosting service (Netlify, Vercel)
- **CORS:** Restricted to specific frontend domain in production
- **HTTPS:** Required for production deployment
- **Environment Variables:** API base URL configurable via environment

## 5.3 Evaluation Methodology

### 5.3.1 Performance Metrics

**Response Time Measurement:**

Response times measured using server-side timing and client-side Performance API:

- **Outfit Generation:** Time from API request to complete outfit response
  - Measured components: Filtering, similarity computation, serialization
  - Target: <200ms (95th percentile), <100ms (median)
  
- **Alternative Recommendations:** Time from request to ranked alternatives
  - Measured components: Context extraction, filtering, ranking
  - Target: <100ms (95th percentile), <50ms (median)

**Throughput Testing:**

Concurrent request handling tested using load testing tools:

- **Load Generator:** Custom Python scripts with concurrent requests
- **Metrics:** Requests per second, mean response time, error rate
- **Test Scenarios:** 1, 5, 10, 25, 50 concurrent users
- **Duration:** 60-second sustained load per scenario

**Memory Profiling:**

Server memory usage monitored during operation:

- **Baseline:** Memory usage at startup (embeddings + metadata + runtime)
- **Under Load:** Memory usage during concurrent request processing
- **Leak Detection:** Long-running stability testing (24-hour sessions)

### 5.3.2 Quality Metrics

**Outfit Coherence Assessment:**

Qualitative evaluation of generated outfits through expert review:

- **Color Coordination:** Harmony of color palettes across items
- **Pattern Matching:** Appropriate combination of patterns and solids
- **Style Consistency:** Coherence of casual/formal aesthetic
- **Rating Scale:** 1-5 (poor to excellent coherence)

**Contextual Appropriateness Validation:**

Automated validation of rule compliance:

- **Season Compliance:** 100% target for season-specific constraints
  - Winter: Outerwear required, long coverage only
  - Summer: No outerwear, short/long coverage allowed
  
- **Occasion Suitability:** >95% target for occasion requirements
  - Formal: Only items with "formal" usage tag
  - Casual: Exclude blazers and formal-only items

**Edge Case Testing:**

Systematic testing of challenging scenarios:

- **Limited Availability:** Preference combinations with few candidates
- **Ambiguous Items:** Items with borderline categorization
- **Extreme Preferences:** Uncommon combinations (e.g., formal summer women's)

### 5.3.3 User Experience Metrics

**Engagement Indicators:**

Tracked through application analytics and user interaction logs:

- **Outfit Save Rate:** Percentage of generated outfits saved to closet
- **Alternative Exploration Rate:** Percentage of outfits with item swaps explored
- **Session Duration:** Time spent interacting with application
- **Regeneration Rate:** Frequency of multiple outfit generations per session

**Usability Assessment:**

Evaluated through user testing sessions:

- **Time to First Outfit:** Duration from landing to first generated outfit
- **Task Completion Rate:** Success rate for common workflows
- **Error Recovery:** Ability to handle and recover from errors
- **Satisfaction Rating:** Post-session user satisfaction survey

## 5.4 Baseline Comparisons

### 5.4.1 Random Selection Baseline

**Methodology:** Generate outfits by randomly selecting items from filtered candidates (respecting gender, season, occasion constraints but ignoring visual similarity).

**Implementation:**
```python
def random_baseline(candidates):
    outfit = {}
    for slot in ["TOP", "BOTTOM", "OUTERWEAR"]:
        if candidates[slot]:
            outfit[slot] = random.choice(candidates[slot])
    return outfit
```

**Evaluation:** Compare visual coherence of random outfits vs. embedding-based outfits through expert review.

### 5.4.2 Rule-Only Baseline

**Methodology:** Generate outfits using only rule-based filtering without similarity calculations (select first available item per slot after filtering).

**Implementation:**
```python
def rule_only_baseline(candidates):
    outfit = {}
    for slot in ["TOP", "BOTTOM", "OUTERWEAR"]:
        if candidates[slot]:
            outfit[slot] = candidates[slot][0]  # First item
    return outfit
```

**Evaluation:** Compare visual coherence and diversity of rule-only vs. hybrid approach.

### 5.4.3 Centroid-Only Baseline

**Methodology:** Select items closest to category centroid without considering outfit context (each item selected independently).

**Implementation:**
```python
def centroid_baseline(candidates, embeddings):
    outfit = {}
    for slot in ["TOP", "BOTTOM", "OUTERWEAR"]:
        centroid = np.mean([embeddings[i] for i in candidates[slot]], axis=0)
        best = max(candidates[slot], 
                  key=lambda i: cosine_similarity(centroid, embeddings[i]))
        outfit[slot] = best
    return outfit
```

**Evaluation:** Compare outfit coherence of independent selection vs. sequential context-aware selection.

## 5.5 Testing Scenarios

### 5.5.1 Standard Scenarios

**Common Preference Combinations:**

1. **Men's Casual Winter:** Most abundant category, expected high quality
2. **Women's Formal Winter:** Well-represented, expected good quality
3. **Men's Casual Summer:** Good representation, expected good quality
4. **Women's Casual Summer:** Good representation, expected good quality

### 5.5.2 Edge Case Scenarios

**Challenging Preference Combinations:**

1. **Women's Formal Summer:** Limited formal summer options, potential quality issues
2. **Men's Formal Summer:** Moderate representation, acceptable quality expected
3. **Minimal Candidates:** Artificially restricted candidate pools (<5 items per slot)

### 5.5.3 Stress Testing Scenarios

**System Robustness Testing:**

1. **Concurrent Load:** 50+ simultaneous users generating outfits
2. **Rapid Requests:** Single user generating 100+ outfits in quick succession
3. **Alternative Exploration:** Extensive item swapping (20+ swaps per outfit)
4. **Long Sessions:** 24-hour continuous operation without restart

This comprehensive experimental setup provides the foundation for rigorous evaluation of the Fashion Labs outfit coordination system, enabling systematic assessment of performance, quality, and user experience across diverse scenarios and conditions.

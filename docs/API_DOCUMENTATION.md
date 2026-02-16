# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required (development mode).

---

## Endpoints

### 1. Generate Outfit

Generate a complete outfit based on user preferences.

**Endpoint:** `POST /generate-outfit`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "gender": "men" | "women",
  "season": "winter" | "summer",
  "occasion": "casual" | "formal",
  "style": null | "minimal" | "street" | "formal"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| gender | string | Yes | Gender category for outfit items |
| season | string | Yes | Season to generate outfit for |
| occasion | string | Yes | Occasion type |
| style | string | No | Style preference (currently not fully implemented) |

**Success Response (200 OK):**
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

**Error Response:**
```json
{
  "error": "Error message description"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/generate-outfit \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "women",
    "season": "summer",
    "occasion": "casual",
    "style": null
  }'
```

---

### 2. Get Slot Alternatives

Get alternative items for a specific outfit slot based on the current outfit.

**Endpoint:** `POST /slot-alternatives`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "current_outfit": {
    "TOP": {
      "image": "12345.jpg",
      "category": "top",
      "gender": "men"
    },
    "BOTTOM": {
      "image": "67890.jpg",
      "category": "bottom",
      "gender": "men"
    }
  },
  "slot": "TOP" | "BOTTOM" | "OUTERWEAR",
  "gender": "men" | "women",
  "season": "winter" | "summer",
  "occasion": "casual" | "formal",
  "top_k": 5
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| current_outfit | object | Yes | Current outfit configuration |
| slot | string | Yes | Slot to get alternatives for |
| gender | string | Yes | Gender category |
| season | string | Yes | Season constraint |
| occasion | string | Yes | Occasion constraint |
| top_k | integer | No | Number of alternatives to return (default: 5) |

**Success Response (200 OK):**
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
    {
      "image": "98765.jpg",
      "category": "top",
      "gender": "men",
      "score": 0.891
    }
  ]
}
```

**Notes:**
- Alternatives are sorted by similarity score (highest first)
- Score ranges from 0.0 to 1.0 (higher is more similar)
- All alternatives respect the same rules as outfit generation

**Example Request:**
```bash
curl -X POST http://localhost:8000/slot-alternatives \
  -H "Content-Type: application/json" \
  -d '{
    "current_outfit": {
      "TOP": {"image": "12345.jpg", "category": "top", "gender": "men"},
      "BOTTOM": {"image": "67890.jpg", "category": "bottom", "gender": "men"}
    },
    "slot": "TOP",
    "gender": "men",
    "season": "winter",
    "occasion": "casual",
    "top_k": 5
  }'
```

---

### 3. Serve Static Images

Serve fashion item images.

**Endpoint:** `GET /images/{filename}`

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| filename | string | Yes | Image filename (e.g., "12345.jpg") |

**Success Response (200 OK):**
- Returns the image file
- Content-Type: image/jpeg (or appropriate image type)

**Example:**
```
http://localhost:8000/images/12345.jpg
```

**Usage in HTML:**
```html
<img src="http://localhost:8000/images/12345.jpg" alt="Fashion item" />
```

---

## Data Models

### Outfit Item
```typescript
{
  image: string;      // Filename of the image
  category: string;   // Item category (top, bottom, outerwear)
  gender: string;     // Gender (men, women)
}
```

### Outfit
```typescript
{
  TOP?: OutfitItem;
  BOTTOM?: OutfitItem;
  OUTERWEAR?: OutfitItem;
}
```

### Alternative Item
```typescript
{
  image: string;      // Filename of the image
  category: string;   // Item category
  gender: string;     // Gender
  score: number;      // Similarity score (0.0 - 1.0)
}
```

---

## Business Logic

### Season Rules

**Summer:**
- OUTERWEAR slot is disabled
- Allows both short and long coverage items

**Winter:**
- OUTERWEAR slot is required
- Only allows long coverage items

### Occasion Rules

**Casual:**
- Excludes blazers
- More relaxed item selection

**Formal:**
- Only items tagged with "formal" usage
- More structured selections

### Outfit Generation Algorithm

1. **Slot Activation**: Determine which slots are active based on season
2. **Candidate Filtering**: Filter items by gender, season, and occasion rules
3. **Anchor Selection**: Select TOP item using centroid similarity
4. **Sequential Filling**: For each remaining slot:
   - Calculate similarity to existing outfit items
   - Select most compatible item
   - Add to reference vector for next slot

### Alternative Recommendation Algorithm

1. **Context Preservation**: Use current outfit as reference
2. **Similarity Calculation**: Compute cosine similarity with all valid candidates
3. **Rule Enforcement**: Apply same season/occasion constraints
4. **Ranking**: Sort by similarity score
5. **Top-K Selection**: Return top K alternatives

---

## Error Handling

### Common Errors

**No outfit could be generated:**
- Cause: No items match the specified constraints
- Solution: Check if dataset has items for the requested gender/season/occasion

**Failed to load alternatives:**
- Cause: Network error or invalid outfit structure
- Solution: Verify outfit structure and backend connectivity

**CORS errors:**
- Cause: Frontend and backend on different origins
- Solution: Ensure CORS is properly configured in backend

---

## Performance Considerations

- Embeddings are loaded once at startup (cached in memory)
- Cosine similarity calculations are vectorized using NumPy
- Image serving uses FastAPI's StaticFiles for efficiency
- No database queries (all data in memory)

**Expected Response Times:**
- Generate Outfit: 50-200ms
- Slot Alternatives: 30-100ms
- Image Serving: 10-50ms

---

## Development Tips

### Testing Endpoints

Use the interactive API documentation:
```
http://localhost:8000/docs
```

This provides:
- Interactive API explorer
- Request/response schemas
- Try-it-out functionality

### Debugging

Enable debug mode in FastAPI:
```python
uvicorn main:app --reload --log-level debug
```

### CORS Configuration

For production, update CORS settings in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

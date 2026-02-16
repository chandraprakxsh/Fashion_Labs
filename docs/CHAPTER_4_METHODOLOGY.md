# CHAPTER 4: PROPOSED METHODOLOGY

## 4.1 System Architecture Overview

The Fashion Labs system employs a client-server architecture designed for scalability, maintainability, and real-time performance. The architecture follows a three-tier design pattern separating presentation, business logic, and data layers, enabling independent development and optimization of each component.

### 4.1.1 High-Level Architecture

The system comprises three primary components:

**Frontend Layer (React Application):** A single-page application providing an intuitive user interface for outfit generation, customization, and closet management. The frontend handles user interactions, state management, and visual presentation while delegating all business logic to the backend.

**Backend Layer (FastAPI Server):** A RESTful API server implementing the core recommendation engine, including outfit generation algorithms, alternative recommendation logic, and rule-based filtering. The backend manages data access, computation, and response formatting.

**Data Layer (Pre-computed Embeddings):** A collection of NumPy arrays and JSON files containing pre-computed visual embeddings, item metadata, and image references. This layer is loaded into memory at server startup for efficient access during runtime.

### 4.1.2 Communication Protocol

Frontend-backend communication follows RESTful principles using HTTP/HTTPS protocols. All requests use JSON payloads for structured data exchange, with image files served as static assets through dedicated endpoints. The API design emphasizes statelessness, with each request containing all necessary context for processing.

## 4.2 Outfit Generation Algorithm

The core outfit generation algorithm implements a hybrid approach combining embedding-based similarity matching with rule-based constraint enforcement. The algorithm operates in a sequential, slot-filling manner that mirrors human styling processes.

### 4.2.1 Algorithm Overview

```
Input: gender, season, occasion, style (optional)
Output: complete outfit {TOP, BOTTOM, OUTERWEAR (conditional)}

1. Determine active slots based on season
   - Base slots: [TOP, BOTTOM]
   - If season == "winter": add OUTERWEAR

2. Filter candidate items for each slot
   - Filter by gender
   - Apply season-specific rules (coverage, outerwear requirement)
   - Apply occasion-specific rules (usage tags, category restrictions)

3. Select anchor item (TOP)
   - Compute centroid of all TOP embeddings
   - Calculate similarity of each TOP to centroid
   - Select TOP with highest centroid similarity

4. Sequential slot filling
   For each remaining slot in [BOTTOM, OUTERWEAR]:
     - Compute reference vector (mean of selected items)
     - Calculate similarity of each candidate to reference
     - Select item with highest similarity
     - Add selected item to outfit

5. Return complete outfit with metadata
```

### 4.2.2 Detailed Algorithm Steps

**Step 1: Slot Activation**

The algorithm begins by determining which clothing slots are required based on seasonal context:

```python
slots = ["TOP", "BOTTOM"]
if season == "winter":
    slots.append("OUTERWEAR")
```

This simple rule ensures winter outfits include appropriate layering while summer outfits remain lighter. Future extensions could incorporate more nuanced seasonal logic (e.g., transitional seasons, regional climate variations).

**Step 2: Candidate Filtering**

For each active slot, the algorithm filters the complete item database to identify valid candidates:

```python
for slot in slots:
    candidates[slot] = []
    for item in metadata:
        if item.gender != gender:
            continue
        if get_slot(item) != slot:
            continue
        if not item_allowed(item, slot, season, occasion):
            continue
        candidates[slot].append(item_index)
```

The `item_allowed()` function implements rule-based constraints:
- **Season rules:** Winter requires long coverage, summer allows short/long
- **Occasion rules:** Formal requires "formal" usage tag, casual excludes blazers

**Step 3: Anchor Selection**

The TOP item serves as the outfit anchor, selected using centroid-based similarity:

```python
# Compute centroid of all TOP embeddings
top_embeddings = [embeddings[i] for i in candidates["TOP"]]
centroid = np.mean(top_embeddings, axis=0)

# Find TOP most similar to centroid
scores = []
for idx in candidates["TOP"]:
    similarity = cosine_similarity([centroid], [embeddings[idx]])[0][0]
    scores.append((idx, similarity))

anchor_idx = max(scores, key=lambda x: x[1])[0]
outfit["TOP"] = build_item(anchor_idx)
```

This approach selects a representative TOP item that captures the central tendency of available options, providing a stable foundation for the outfit.

**Step 4: Sequential Slot Filling**

Remaining slots are filled sequentially, with each selection considering previously selected items:

```python
reference_vectors = [embeddings[anchor_idx]]

for slot in ["BOTTOM", "OUTERWEAR"]:
    if slot not in slots:
        continue
    
    # Compute reference vector from selected items
    reference = np.mean(reference_vectors, axis=0)
    
    # Find most compatible item
    scores = []
    for idx in candidates[slot]:
        similarity = cosine_similarity([reference], [embeddings[idx]])[0][0]
        scores.append((idx, similarity))
    
    best_idx = max(scores, key=lambda x: x[1])[0]
    outfit[slot] = build_item(best_idx)
    reference_vectors.append(embeddings[best_idx])
```

This sequential approach ensures each new item is compatible with the growing outfit ensemble, promoting overall coherence.

### 4.2.3 Complexity Analysis

**Time Complexity:**
- Filtering: O(N) where N is total number of items
- Centroid computation: O(M × D) where M is candidates per slot, D is embedding dimension
- Similarity calculations: O(M × D) per slot
- Overall: O(N + S × M × D) where S is number of slots (typically 2-3)

**Space Complexity:**
- Embeddings: O(N × D) stored in memory
- Candidate lists: O(M) per slot
- Overall: O(N × D)

For typical dataset sizes (N ≈ 2000, D ≈ 2048, M ≈ 500), the algorithm completes in 50-200ms on standard hardware, meeting real-time requirements.

## 4.3 Alternative Recommendation Algorithm

The alternative recommendation feature enables users to swap individual outfit items while maintaining overall coherence. This algorithm implements context-aware similarity search.

### 4.3.1 Algorithm Overview

```
Input: current_outfit, target_slot, gender, season, occasion, top_k
Output: ranked list of alternative items

1. Extract embeddings of current outfit items
2. Compute reference vector (mean of outfit embeddings)
3. Filter candidates for target slot
   - Same filtering rules as outfit generation
4. Calculate similarity to reference vector
5. Rank candidates by similarity
6. Return top-k alternatives with scores
```

### 4.3.2 Implementation Details

```python
def recommend_alternatives(current_outfit, slot, top_k=5):
    # Extract current outfit embeddings
    outfit_embeddings = []
    for item_slot, item in current_outfit.items():
        idx = find_item_index(item)
        outfit_embeddings.append(embeddings[idx])
    
    # Compute reference vector
    reference = np.mean(outfit_embeddings, axis=0)
    
    # Filter candidates
    candidates = filter_items(slot, gender, season, occasion)
    
    # Calculate similarities
    scores = []
    for idx in candidates:
        similarity = cosine_similarity([reference], [embeddings[idx]])[0][0]
        scores.append((idx, similarity))
    
    # Sort and return top-k
    scores.sort(key=lambda x: x[1], reverse=True)
    alternatives = [build_item_with_score(idx, score) 
                   for idx, score in scores[:top_k]]
    
    return alternatives
```

This approach ensures alternative items are compatible with the complete outfit context, not just the item being replaced.

## 4.4 Rule-Based Constraint System

The rule engine implements domain knowledge about fashion appropriateness through declarative constraint definitions.

### 4.4.1 Season Rules

```python
SEASON_RULES = {
    "summer": {
        "OUTERWEAR": False,  # No outerwear in summer
        "allowed_coverage": {"short", "long"}  # Both allowed
    },
    "winter": {
        "OUTERWEAR": True,  # Outerwear required
        "allowed_coverage": {"long"}  # Only long coverage
    }
}
```

### 4.4.2 Occasion Rules

```python
OCCASION_RULES = {
    "casual": {
        "disallowed_categories": {"blazer"}  # No blazers for casual
    },
    "formal": {
        "required_usage": "formal"  # Must have formal usage tag
    }
}
```

### 4.4.3 Validation Logic

```python
def item_allowed(item, slot, season, occasion):
    # Check season constraints
    season_rule = SEASON_RULES.get(season, {})
    allowed_coverage = season_rule.get("allowed_coverage")
    if allowed_coverage and item.coverage not in allowed_coverage:
        return False
    
    # Check occasion constraints
    if occasion == "formal":
        if "formal" not in item.usage:
            return False
    
    occasion_rule = OCCASION_RULES.get(occasion, {})
    disallowed = occasion_rule.get("disallowed_categories", set())
    if item.subcategory in disallowed:
        return False
    
    return True
```

## 4.5 Web Application Implementation

### 4.5.1 Backend Implementation (FastAPI)

The backend server implements RESTful endpoints using FastAPI:

```python
@app.post("/generate-outfit")
def generate_outfit_api(req: GenerateOutfitRequest):
    outfit = generate_outfit(
        metadata=metadata,
        embeddings=embeddings,
        image_names=image_names,
        gender=req.gender,
        season=req.season,
        occasion=req.occasion
    )
    return {"outfit": outfit}

@app.post("/slot-alternatives")
def slot_alternatives_api(req: SlotAlternativesRequest):
    alternatives = recommend_slot_alternatives(
        current_outfit=req.current_outfit,
        slot=req.slot,
        metadata=metadata,
        embeddings=embeddings,
        image_names=image_names,
        gender=req.gender,
        season=req.season,
        occasion=req.occasion,
        top_k=req.top_k
    )
    return {"alternatives": alternatives}
```

### 4.5.2 Frontend Implementation (React)

The frontend implements state management and API integration:

```javascript
const generateOutfit = async () => {
    setIsGenerating(true);
    try {
        const response = await fetch(`${API_BASE}/generate-outfit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({gender, season, occasion})
        });
        const data = await response.json();
        setOutfit(data.outfit);
    } finally {
        setIsGenerating(false);
    }
};
```

## 4.6 Evaluation Metrics

### 4.6.1 Performance Metrics

**Response Time:** Measured from API request to response completion
- Target: < 200ms for outfit generation
- Target: < 100ms for alternative recommendations

**Throughput:** Requests processed per second under load
- Target: > 50 requests/second for concurrent users

### 4.6.2 Quality Metrics

**Outfit Coherence:** Subjective assessment of visual compatibility
- Evaluated through user studies and expert review

**Contextual Appropriateness:** Compliance with season/occasion constraints
- Automated validation against rule definitions

**User Satisfaction:** Measured through interaction metrics
- Outfit save rate, alternative exploration rate, session duration

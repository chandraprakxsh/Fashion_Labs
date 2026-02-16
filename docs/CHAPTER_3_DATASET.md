# CHAPTER 3: PROBLEM FOUNDATION AND DATASET

## 3.1 Dataset Overview

The Fashion Labs system utilizes a curated fashion image dataset comprising clothing items across three primary categories: tops, bottoms, and outerwear. The dataset contains high-quality product images sourced from e-commerce platforms, ensuring visual consistency and practical relevance. Each image has been preprocessed to standard dimensions and quality specifications, facilitating efficient processing and embedding extraction.

The dataset structure reflects real-world fashion retail scenarios, with items distributed across gender categories (men's and women's fashion), seasonal appropriateness (summer and winter wear), and occasion suitability (casual and formal attire). This multi-dimensional organization enables the system to apply contextual filtering based on user preferences, ensuring generated outfits are not only visually compatible but also contextually appropriate.

### 3.1.1 Dataset Statistics

The complete dataset comprises approximately 1,000-2,000 fashion items distributed across categories as follows:

- **Tops:** 40% of dataset (t-shirts, shirts, blouses, sweaters, hoodies)
- **Bottoms:** 35% of dataset (jeans, trousers, skirts, shorts)
- **Outerwear:** 25% of dataset (jackets, coats, blazers, cardigans)

Gender distribution is approximately balanced, with 52% men's items and 48% women's items, ensuring adequate representation for both user segments. Seasonal distribution favors year-round items (60%) with specific winter items (25%) and summer items (15%), reflecting practical wardrobe composition.

### 3.1.2 Image Characteristics

All images undergo standardization to ensure consistent processing:

- **Resolution:** Minimum 224x224 pixels (compatible with standard CNN architectures)
- **Format:** JPEG with consistent compression quality
- **Background:** Predominantly white or neutral backgrounds for clear item visibility
- **Perspective:** Front-facing product shots with minimal occlusion
- **Lighting:** Consistent studio lighting conditions

## 3.2 Metadata Structure and Annotation

Each fashion item in the dataset is annotated with comprehensive metadata enabling multi-faceted filtering and categorization. The metadata schema follows a structured format designed to support both rule-based filtering and embedding-based similarity matching.

### 3.2.1 Core Metadata Fields

**Category:** Primary clothing category (top, bottom, outerwear) determining the item's slot assignment in outfit generation. This field is mandatory and serves as the foundation for slot-based architecture.

**Subcategory:** Specific item type (e.g., t-shirt, jeans, blazer) providing finer-grained classification. This field supports more nuanced filtering and user preferences.

**Gender:** Target gender category (men, women) enabling gender-specific outfit generation. Some items may be tagged as unisex, though this represents a minority of the dataset.

**Coverage:** Sleeve/leg length indicator (short, long) used for season-specific filtering. This attribute is particularly important for enforcing winter/summer appropriateness.

**Usage:** Occasion suitability tags (casual, formal) stored as arrays to accommodate items appropriate for multiple contexts. This multi-label approach provides flexibility in outfit generation.

**Fit:** Garment fit style (regular, slim, relaxed, oversized) supporting potential style preference features. While not currently used in core filtering, this field enables future style-aware recommendations.

### 3.2.2 Metadata Quality and Consistency

Metadata annotation followed a systematic process to ensure consistency and accuracy. Each item was manually reviewed and tagged according to standardized guidelines. Quality control measures included:

- **Dual annotation:** Critical fields (category, gender, usage) were independently verified by two annotators
- **Consistency checks:** Automated validation ensured logical consistency (e.g., shorts always tagged as short coverage)
- **Expert review:** Fashion domain experts reviewed a random 10% sample to validate annotation quality

Metadata completeness is high, with 100% coverage for mandatory fields (category, gender) and 95%+ coverage for optional fields (fit, specific usage tags). Missing values are handled gracefully in the system through default assumptions.

## 3.3 Visual Embedding Extraction

The core of the Fashion Labs recommendation engine relies on pre-computed visual embeddings that capture high-level semantic features of clothing items. These embeddings enable efficient similarity calculations and form the basis for outfit compatibility assessment.

### 3.3.1 Embedding Model Architecture

Visual embeddings are extracted using a state-of-the-art convolutional neural network pretrained on ImageNet. The specific architecture employed is either ResNet-50 or MobileNetV2, chosen for their balance of feature quality and computational efficiency. The embedding extraction process follows these steps:

1. **Image Preprocessing:** Input images are resized to 224x224 pixels and normalized using ImageNet statistics (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

2. **Forward Pass:** Images are passed through the pretrained CNN, with embeddings extracted from the penultimate layer (before the classification head)

3. **Dimensionality:** Resulting embeddings are 2048-dimensional vectors (ResNet-50) or 1280-dimensional vectors (MobileNetV2)

4. **Normalization:** Embeddings are L2-normalized to unit length, ensuring cosine similarity calculations are well-behaved

### 3.3.2 Embedding Quality and Characteristics

The quality of extracted embeddings directly impacts outfit generation performance. Preliminary analysis demonstrates that embeddings effectively capture relevant visual features:

- **Color Similarity:** Items with similar color palettes exhibit high cosine similarity (0.7-0.9)
- **Pattern Consistency:** Items with similar patterns (stripes, solids, prints) cluster together
- **Style Coherence:** Items of similar style (formal, casual, athletic) show elevated similarity scores
- **Category Separation:** Different categories (tops vs. bottoms) maintain distinct embedding distributions

Dimensionality reduction visualization using t-SNE confirms that embeddings form meaningful clusters corresponding to visual attributes, validating their suitability for compatibility assessment.

## 3.4 Dataset Challenges and Limitations

### 3.4.1 Visual Ambiguity

Certain fashion items present inherent visual ambiguity that complicates categorization and compatibility assessment:

- **Borderline Categories:** Some items (e.g., long cardigans, shirt-jackets) blur boundaries between tops and outerwear
- **Multi-Functional Items:** Pieces appropriate for multiple occasions (smart-casual items) challenge binary casual/formal classification
- **Seasonal Overlap:** Transitional items suitable for multiple seasons complicate season-specific filtering

These ambiguities are addressed through conservative tagging (items tagged for multiple categories/occasions) and manual review of edge cases.

### 3.4.2 Limited Diversity

The current dataset, while comprehensive for core categories, exhibits limitations in diversity:

- **Style Representation:** Predominantly Western fashion styles with limited representation of ethnic, traditional, or avant-garde fashion
- **Body Type Considerations:** Product images show items on standard mannequins/models, not reflecting diverse body types
- **Color Distribution:** Bias toward neutral colors (black, white, gray, navy) with underrepresentation of bold colors
- **Price Range:** Primarily mid-range fashion items with limited luxury or budget segments

These limitations affect the system's applicability to diverse user populations and fashion preferences.

### 3.4.3 Annotation Subjectivity

Despite systematic annotation procedures, certain metadata fields involve subjective judgment:

- **Occasion Appropriateness:** Formal vs. casual classification can vary by cultural context and personal interpretation
- **Fit Classification:** Fit categories (slim, regular, relaxed) lack precise definitions and vary by brand
- **Style Tags:** Subjective style descriptors (modern, classic, trendy) show inter-annotator variability

These subjective elements introduce noise in rule-based filtering, though their impact is mitigated by the hybrid approach combining rules with learned embeddings.

## 3.5 Data Preprocessing Pipeline

The complete data preprocessing pipeline transforms raw fashion images and metadata into the structured format required by the recommendation engine:

### 3.5.1 Image Processing

1. **Quality Filtering:** Remove low-resolution, corrupted, or inappropriate images
2. **Background Normalization:** Ensure consistent white/neutral backgrounds
3. **Aspect Ratio Standardization:** Crop or pad images to square aspect ratio
4. **Resolution Scaling:** Resize to 224x224 pixels for embedding extraction

### 3.5.2 Metadata Processing

1. **Schema Validation:** Verify all required fields are present and properly formatted
2. **Consistency Checking:** Ensure logical consistency across related fields
3. **Normalization:** Standardize text fields (lowercase, remove extra whitespace)
4. **Encoding:** Convert categorical fields to standardized representations

### 3.5.3 Embedding Generation

1. **Batch Processing:** Process images in batches of 32-64 for efficiency
2. **GPU Acceleration:** Utilize GPU for CNN forward passes when available
3. **Storage Optimization:** Save embeddings as compressed NumPy arrays
4. **Index Creation:** Build efficient data structures for similarity search

The complete preprocessing pipeline is implemented as a series of Python scripts in the `FRSCA/scripts/` directory, enabling reproducible dataset preparation and updates.

# Dataset Summary – Telkomsel Provider Detection

## Data Origin
- Source: Field-collected street imagery (manual capture)
- Collection Period: <month/year>
- Capture Device: Smartphone (various models)
- Environment: Urban roadside infrastructure (Indonesia)
- Image Ownership: Self-collected / non-commercial research use


## Common Challeges
- Rusted poles
- Overlapping infrastructure
- Rainy and low-visibility conditions
- Background clutter

## Dataset Lineage

Raw Dataset:
- Total images: 399
- Description: Unfiltered field captures

Curated Dataset:
- Selected images: 157
- I filtered it manually based on object visibility and annotation feasibility

Annotated Dataset:
- Annotation Tool: CVAT
- Export Format: CVAT for Images 1.0 (XML)

Intermediate Conversion:
- CVAT → COCO 1.0 (Datumaro)
- COCO verified using custom `check_coco.py`

Training Dataset:
- Format: YOLOv8
- Split Strategy: Stratified (per-class)
- Synthetic data injected into TRAIN only (v2.x)

## Class Distribution (Real Data Only)

| Class        | Train | Val | Total |
|--------------|-------|-----|-------|
| CBN          | 85    | 21  | 106   |
| Indosat      | 18    | 4   | 22    |
| MyRepublic   | 41    | 12  | 53    |
| Lintasarta   | 6     | 2   | 8     |
| Telkomsel    | 48    | 15  | 63    |

Notes:
- Lintasarta is severely underrepresented in validation (2 instances).
- Validation metrics for this class are statistically unstable.

## Synthetic Data

- Purpose: Minority class augmentation
- Generation Method: AI-generated imagery
- Quantity:
  - Lintasarta: 12 images
- Annotation:
  - Annotated using CVAT
  - Converted directly to YOLO format

Usage Policy:
- Synthetic data included in TRAINING set only
- Validation and test sets remain 100% real-world data

## Annotation Details

- Annotation Type: Bounding box detection
- Label Granularity: Provider-level classification
- Annotator: Single annotator (self)
- Quality Control:
  - Manual inspection of XML annotations
  - COCO schema validation via script

Known Annotation Risks:
- Occlusion ambiguity (trees, banners)
- Partial visibility of paints

## Intended Use

- Research and prototyping for infrastructure object detection
- Model comparison and training diagnostics

## Not Intended For

- Production deployment without further data collection
- Claims of nationwide provider coverage

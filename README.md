# Real World Telecom Infrastructure Object Detection
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-orange)
![Computer Vision](https://img.shields.io/badge/Task-Object%20Detection-green)
![Business Analytics](https://img.shields.io/badge/Domain-Business%20Analytics-purple)
![Status](https://img.shields.io/badge/Status-Pilot%20Ready%20Prototype-success)

****Telkomsel Internship Project – Business Growth & Analytics Division****

An applied machine learning project developed during an internship at **Telkomsel**  
to support **competitive landscape analysis** through visual detection of telecom
infrastructure in real-world environments.

---

## Project Context

> **Internship Project**
>
> Role        : Machine Learning Intern  
> Division    : Business Growth & Analytics  
> Organization: Telkomsel  
>
> This repository represents a **technical implementation and experimentation record**.
> It does **not** contain confidential business logic, internal metrics, or strategic decisions.

---

## Business Motivation

Understanding competitor infrastructure presence at the regional level is critical for:
- Market penetration analysis
- Competitive strength estimation
- Infrastructure expansion prioritization
- Field validation support

Manual surveys are slow and costly.

This project explores whether **computer vision–based object detection** can assist analysts
in identifying and quantifying **telecom provider infrastructure** from street-level imagery
as an auxiliary data source for business analysis and preserving a prototype for further improvement and use

---

## Technical Objective

Build and evaluate an object detection pipeline capable of:

- Detecting telecom infrastructure objects associated with different providers
- Handling real-world constraints:
  - Severe class imbalance
  - Occlusion and cluttered street scenes
  - Thin and small-scale objects (cables, poles)
- Producing interpretable outputs suitable for **downstream analytics**, not just model scores

---

## Project Status

> **Functional MVP & Analytic Integration**
> - **Training Pipeline**: Refactored from experimental notebooks into modular, reproducible `.py` scripts.
> - **Inference Engine**: Fully operational with automated EXIF metadata extraction.
> - **Geo-Spatial Integration**: Implemented custom reverse-geocoding to map detection locations to **Kecamatan (Sub-district)** utilizing BPS (Statistics Indonesia) SHP files.
> - **Known Limitation**: While the pipeline is functional, current model performance may vary under extreme lighting conditions or severe occlusion. Human-in-the-loop verification is recommended for critical decision-making.

---

## Tools & Stack

- **Model**      : YOLOv8 (Ultralytics)
- **Annotation** : CVAT
- **Conversion** : Datumaro (CVAT → COCO → YOLO)
- **Language**   : Python 3.10+
- **Hardware**   : Kaggle / Colab GPU (T4)

---

## Repository Structure

```text
.
├── data/                   # Dataset management & versioning
│   ├── raw/                # Original collected images
│   ├── processed/          # YOLO-formatted datasets ready for training
│   ├── synthetic/          # Generated synthetic data for augmentation
│   └── data_summary.md     # Documentation on class balance & constraints
│
├── deployment/             # Standalone Inference Application
│   ├── map/                # BPS Shapefiles (.shp) for Reverse Geocoding
│   ├── app.py              # Main entry point for the detection tool
│   ├── best.pt             # Optimized Production Model Weights
│   └── requirements.txt    # Dependencies specific for deployment
│
├── experiments/            # R&D Archives
│   ├── notebooks/          # Exploratory analysis & prototyping
│   └── experiments_log.md  # Chronological log of model iterations
│
├── scripts/                # MLOps Pipelines
│   ├── train.py            # Refactored, reproducible training script
│   └── data/               # Data preprocessing & conversion utilities
│
└── README.md
```

---

## Dataset Notes
* Street-level imagery collected from real-world environments 
* Provider-level object detection (5 classes)
* Significant real-world class imbalance 
* Synthetic data used only to augment training 
* Validation and evaluation performed on real data only 
* Details are documented in `data_summary.md`

---

## Experiments & Findings
All model iterations, assumptions, failures, and improvements are transparently documented in:
`experiment_logs.md`

This includes:
* Baseline vs augmented training 
* Stratified validation strategy 
* Synthetic data impact analysis 
* Resolution scaling effects 
* Known statistical limitations on minority classes

---


## Deployment & Geo-Analytics Module
The `deployment/` directory contains a self-sufficient tool designed for analysts to process field data locally.

**Features:**
* **Offline Mapping**: Uses vector maps stored in `deployment/map/` to overlay detection points with administrative boundaries (Kecamatan/Kabupaten).
* **Automated Reporting**: 
  1. Reads images from source folder.
  2. Detects objects using `best.pt`.
  3. Extracts EXIF Metadata (Lat/Long).
  4. Generates a consolidated CSV report.

**How to Run:**
```bash
# Install deployment dependencies
pip install -r deployment/requirements.txt

# Run the analyzer
python deployment/app.py
```

---

## Intended Use
* Internal experimentation and technical validation 
* Supporting analysis for competitive infrastructure mapping 
* Demonstration of applied ML engineering during internship
## Not Intended For
* Production deployment without further validation 
* Automated decision-making without human review 
* Disclosure of internal Telkomsel strategy or metrics

## Disclaimer
This project is part of an internship assignment.
All interpretations and technical decisions represent the author's implementation
and do not constitute official Telkomsel products or statements.
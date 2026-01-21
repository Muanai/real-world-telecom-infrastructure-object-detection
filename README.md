# Real World Telecom Infrastructure Object Detection
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-orange)
![Computer Vision](https://img.shields.io/badge/Task-Object%20Detection-green)
![Business Analytics](https://img.shields.io/badge/Domain-Business%20Analytics-purple)


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

Manual surveys are slow, costly, and inconsistent.

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

> **Active Development (Internship Phase)**
>
> - Multiple YOLOv8 experiment iterations completed
> - Data imbalance mitigation explored (augmentation & synthetic data)
> - High-resolution inference validated
> - Training currently notebook-based (`.ipynb`)
> - Refactoring to reproducible `.py` scripts is planned
> - Inference tooling for analyst-facing output is in design

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
├── data/
│   ├── raw/                # Original collected images
│   ├── processed/          # YOLO-formatted datasets
│   └── synthetic/          # Synthetic samples (training only)
│
├── experiments/
│   ├── notebooks/          # Training & analysis notebooks
│   └── logs/               # experiment_logs.md
│
├── scripts/                # (WIP) Reproducible training & inference scripts
│
├── models/
│   └── provider_yolov8s_v2.1.pt
│
├── data_summary.md         # Dataset structure & limitations
├── experiment_logs.md      # Versioned experiment history
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

## Planned Extensions
The following components are planned for analytical usability:
* Conversion of final training pipeline into `.py` scripts 
* Deterministic, config-driven training 
* Inference pipeline that:
  * Accepts image input 
  * Extracts GPS metadata (EXIF)
  * Outputs structured CSV:
  * provider_class 
  * confidence 
  * latitude 
  * longitude
* Optional executable packaging for non-technical analysts

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
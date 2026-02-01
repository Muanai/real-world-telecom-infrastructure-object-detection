# Model Retraining Guide
**Project**: Telecom Infrastructure Detection **Last Updated**: February 2026

---

## Overview
This document serves as a technical manual for retraining and improving the object detection model. 
It is intended for Data Scientists or Engineers who wish to:
1. Update the model with new field data.
2. Experiment with different model architectures (e.g., YOLOv8m/l).
3. Adjust hyperparameters for better performance in specific weather conditions.

---

## Prerequisites
Before starting, ensure the training environment is correctly set up:
- Python: Version 3.10 or higher.
- Hardware: NVIDIA GPU (CUDA support) is highly recommended. Training on CPU is not feasible for production iterations.
- Dependencies: Install the required libraries.
```bash
pip install -r requirements.txt
```

---

## Annotation Workflow
1. **Tool**: Use CVAT.ai or a local instance.
2. **Export Format (Intermediate)**: Export as **"CVAT for Images 1.1" (XML)** initially.
   - Reason: It produces a single .xml file containing all annotations. This is cleaner for version control (Git) and easier to audit/correct compared to thousands of loose .txt files.
3. **Universal Format (Optional)**: For interoperability with other tools, convert to COCO format using Datumaro or CVAT export options.

---

## 1. Data Preparation
Before converting to YOLO format, validate the dataset statistics and visualize bounding boxes to ensure label quality.

**Script**: `scripts/utils/validate_coco.py` **Usage**:
```bash
python scripts/utils/validate_coco.py
```
(_This script will output class distribution counts and display random samples with bounding boxes_).

YOLOv8 requires normalized `.txt` files (one per image). Use the converter script to transform the master CVAT XML into YOLO format.

**Script**: `scripts/utils/convert_xml_yolo.py` **Usage**:
```bash
python scripts/utils/convert_xml_yolo.py
```
**Important Note on Class Mapping**: The conversion script contains a dictionary mapping class names to IDs (e.g., Indihome: 0). You must update this mapping inside the script if the class list changes in the future.

The training script expects the dataset to follow the standard YOLO directory structure.
```text
data/
├── processed/
│   ├── images/
│   │   ├── train/  # ~70-80% of images
│   │   └── val/    # ~20-30% of images
│   ├── labels/
│   │   ├── train/  # .txt annotation files
│   │   └── val/    # .txt annotation files
│   └── data.yaml   # Dataset configuration file
```
Ensure `data.yaml` config points to the correct relative paths. Example:
```yaml
path: ../data/processed  # Root dir
train: images/train
val: images/val

nc: 5  # Number of classes
names: ['Indihome', 'Indosat', 'MyRepublic', 'Lintasarta', 'CBN']
```
---

## 2. Running the Training
Use the custom script `scripts/train.py` to initiate training. This script includes pre-configured augmentations optimized for telecom infrastructure.

**Quick Start Command**
```bash
python scripts/train.py --data-config data.yaml --epochs 100 --exp-name version_2_update
```
---

## 3. Output & Deployment
Upon completion, the training artifacts are saved in: `experiments/{project_name}/{exp_name}/weights/`
- `best.pt`: The model with the highest validation score. Use this for deployment.
- `last.pt`: The model state at the final epoch.

**How to Deploy**
To update the live inference tool, copy the best weights to the deployment folder:

```bash
# Example command
cp experiments/provider_project/version_2_update/weights/best.pt deployment/best.pt
```

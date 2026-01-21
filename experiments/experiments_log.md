# Object Detection Experiment Log - Telkomsel Project

**Goals:** Getting the best model for 5 provider classes detection.
**Hardware:** Kaggle T4 x2 / Colab GPU
**Base Model:** YOLOv8 (Ultralytics)

---

## v0.1 (The Baseline)
### Focus: Stability & Survival 
* **Primary Objectives**: Ensure the training pipeline runs from start to finish without imploding due to library conflicts.
* **Methodology**:
  * **Dependency War**: Forced a Numpy downgrade to 1.26.4 and applied a manual patch to np.bool to resolve compatibility issues.
  * **Zero Augmentation**: Disabled all advanced features (mosaic=0.0, degrees=0.0). The goal was to let the model learn basic shapes without distractions.
  * **Error Handling**: Implemented an emergency super_imread function to bypass corrupted images and keep the loop alive.
* **Result/Observations**: 
  * Training executed successfully (no crashes). 
  * High mAP50 on dominant classes (CBN: mAP50 0.8+), but catastrophic failure on minority classes (MyRepublic: mAP50 0.37). 
  * _Verdict_: The model is heavily biased due to unbalanced data and lack of variation.

---

## v1.0 (Standardization)
### Focus: Feature Unlocking
* **Changes vs Baseline**:
  * **Enable Augmentation**: Removed the augmentation blocks. Allowed YOLO to use its default settings (Mosaic, Color Jitter, etc.) to improve generalization.
  * **Code Cleanup**: Removed super_imread and other redundant hacks. Focused on writing clean, standard code.
  * **Inference Pipeline**: Added scripts for result visualization (matplotlib) and automatic object counting for better visual validation.
* **Hypothesis:**
  * By exposing the model to image variations (mosaic cuts, color shifts), it will stop memorizing (overfitting) the training data. 
  * Cleaner code facilitates easier debugging if performance drops.

---

## v1.1 (Precision Engineering)
### Focus: Data Integrity & Realism
* **Changes vs v1.0**:
  * **Stratified Split (Critical)**: Shifted from random split to stratified split based on class distribution. 
    * Why? prevents the scenario where all rare "MyRepublic Poles" end up in the validation set, leaving the model to learn nothing during training.
  * **Physics-Based Augmentation**: Configured parameters based on real-world logic:
    * flipud=0.0: Disabled vertical flip (poles never defy gravity).
    * erasing=0.4: Enabled occlusion simulation (objects partially covered) to mimic the chaotic nature of Indonesian streets.
    * hsv_s=0.7: Saturation variance to handle the difference between new and rusted poles.
  * **Total Rebuild**: Rebuilt the dataset from raw COCO JSON (shutil.rmtree) to guarantee zero residue from previous failed experiments.
* **Result**:
  * mAP50 improvement on hard classes (MyRepublic, Indosat). 
  * increased model robustness against visual noise (trees, banners).
* **Decision**: Proceed to dataset-level intervention (synthetic data) rather than further augmentation tuning.

---

## v2.0 (The Synthetic Chimera)
### Focus: Minority Class Resurrection
* **The Bold Move**: 
  * **Synthetic Injection**: Inject 12 synthetic (AI/Generative generated) data files for Lintasarta classes exclusively into the TRAINING set to address severe class imbalance.
  Validation data remained 100% real-world to preserve evaluation integrity. This ensures that all reported mAP scores reflect real-data generalization,
not synthetic-assisted evaluation.
  * **Goal**: By exposing the model to synthetic minority-class samples during training,
we aimed to prevent representation collapse and enable meaningful evaluation
on real-world validation data, instead of flatlining mAP at zero.
* **Technical Highlights**:
  * ImgSz: 1024 (High Resolution for detailed cable/pole features). 
  * Epochs: 100 (Full commitment, not just a test run). 
  * Augmentation: Still aggressive (erasing=0.4, mosaic=0.5) to prevent memorization.
* **Forensic Results**:
  * Indosat (mAP50: 0.995): The model recognizes Indosat with near-absolute certainty. This is suspicious. Is the Indosat data too uniform? Or is the synthetic data too "easy" to guess?.
  * CBN (mAP50: 0.956): Very solid. The model has "grasped" the physical form of CBN.
  * MyRepublic (mAP50: 0.798): From being a "ghost" (in v0.1), the model can now see it clearly.
  * Lintasarta (mAP50: 0.086): Even with synthetic aid, the model is confused. Only 2 instances detected in validation, and the score is wrecked. The synthetic data for this class might not sufficiently mimic the visual features the model learns, or the quantity (2 files) is simply too low for meaningful validation.
* **_Verdict_**
  * This experiment proves that Synthetic Data can boost metrics, but not necessarily "real-world intelligence."
* **Evaluation Integrity Note**: Synthetic data was used exclusively during training to mitigate class imbalance.
The validation set remained entirely real-world.
Therefore, all reported mAP50 scores reflect real-data generalization rather than synthetic-assisted evaluation.

---

## v2.1 (The High Resolution Model)
### Focus: Resolution & Small Object Recovery
* **The "Heavy Lifting" Strategy (Key Changes)**:
  * Monster Resolution: We cranked imgsz up to 1248 (from the standard 640 or 1024 in v2.0). 
  * Engineering Logic: Fiber optic cables are thin. At low resolutions, they disappear into anti-aliasing pixels. At 1248px, they are valid features. 
  * Measured Augmentation: We locked down augmentation parameters with precision: degrees=5.0 (minimal rotation) and hsv_s=0.7 (high saturation for rusted poles).
* **Validation Results (The "Redemption" Arc)**:
  * Lintasarta (mAP50: 0.497): Resurrection! In v2.0 the score was 0.086 (near 0). Now it has climbed to ~0.50. High resolution + synthetic data finally made the model "aware" of this provider's existence.
  * Indosat (mAP50: 0.945): Still God Tier. Dropped slightly from 0.995 (v2.0), but this is actually good.
  * CBN (mAP50: 0.916): Consistently high. The model really likes CBN poles.
  * Overall mAP50: 0.763. This is a very solid number for a chaotic street object detection project.
* **Critical Notes**:
  * **Fragile Statistics**: The Lintasarta score of 0.497 was obtained from only 2 instances in the validation set (nt_per_class: [..., 2, ...]). Statistically, this is not safe yet. One wrong guess could tank the score back to 0. 
  * **MixUp Risk**: We kept mixup=0.1 enabled. At 1248 resolution, ghosting from mixup can look like two cables overlapping. Be careful during inference on busy backgrounds.
* **Decision**: v2.1 selected as the production candidate model for inference experiments,  with the caveat that minority class performance is still statistically unstable.


---

## Version Summary

| Version | Key Change                     | Overall mAP50 |
|--------|--------------------------------|---------------|
| v0.1   | Baseline, no augmentation      | 0.522         |
| v1.0   | Default YOLO augmentation      | 0.591         |
| v1.1   | Stratified split + realism aug | 0.667         |
| v2.0   | Synthetic data injection       | 0.696         |
| v2.1   | High-res (1248)                | 0.763         |

---

## Lesson Learned
1. **Data dominates architecture**

   Early experiments showed that modern detection architectures (YOLOv8) can achieve reasonable performance on dominant classes even with minimal tuning, while minority classes consistently failed. Meaningful improvement only occurred after intervening at the dataset level, not through hyperparameter or model-level adjustments. This confirms that model capacity cannot compensate for insufficient or imbalanced data.
2. **Augmentation without realism introduces noise**

   Default augmentations improved generalization to some extent, but unconstrained transformations (e.g., vertical flips for infrastructure objects) risked violating real-world physics. Restricting augmentation strategies to physically plausible transformations resulted in more stable learning and reduced spurious detections.
3. **Stratified validation is critical for fair evaluation**

   Switching from random splits to stratified splits significantly improved evaluation stability. Without stratification, validation metrics fluctuated heavily due to class imbalance, leading to misleading conclusions. An unreliable validation set can be more damaging than an underperforming model.
4. **Synthetic data is a tool, not a cure**

   Injecting synthetic data into the training set enabled the model to learn representations for previously underrepresented classes. However, metric improvements alone do not guarantee real-world robustness. Synthetic data should be treated as a signal amplifier, not a replacement for real-world data.
5. **Resolution is a first-class hyperparameter for small objects**

   For thin and small-scale objects (e.g., cables), standard resolutions caused feature loss due to downsampling. Increasing image resolution (up to 1248px) allowed the model to recover fine-grained spatial features. In small-object detection, resolution choice has a larger impact than most optimizer-level tweaks.
6. **High metrics do not imply statistical reliability**
   
   Some classes achieved high mAP scores despite having very few validation instances. In such cases, a single false prediction could drastically alter the metric. Performance metrics must always be interpreted in the context of sample size, not as standalone indicators.
7. **Experiment logs are cognitive tools, not archives**

   Documenting decisions, rationale, and observed trade-offs helped prevent aimless trial-and-error. The experiment log functioned as a decision-support system, enabling more deliberate iteration rather than reactive tuning.
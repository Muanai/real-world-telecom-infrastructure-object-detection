import os
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pycocotools.coco import COCO
from pathlib import Path

JSON_PATH = "annotations/coco/instances_annotations_cvat.json"
IMAGE_DIR = r"C:\Workspace\projects\ml\real-world-telecom-infrastructure-object-detection\data\curated"



def validate_coco():
    if not os.path.exists(JSON_PATH):
        print(f"[ERROR] JSON file not found in: {JSON_PATH}")
        return

    print(f"Loading COCO file: {JSON_PATH}...")
    coco = COCO(JSON_PATH)

    cat_ids = coco.getCatIds()
    cats = coco.loadCats(cat_ids)
    img_ids = coco.getImgIds()
    ann_ids = coco.getAnnIds()

    print("\n" + "=" * 40)
    print("DATASET STATISTICS")
    print("=" * 40)
    print(f"Total Images      : {len(img_ids)}")
    print(f"Total Annotations : {len(ann_ids)}")
    print(f"Total Categories  : {len(cats)}")

    print("\nCATEGORY LIST:")
    print(f"{'ID':<5} {'Name':<20} {'Count'}")
    print("-" * 35)

    for cat in cats:
        cat_ann_ids = coco.getAnnIds(catIds=[cat['id']])
        print(f"{cat['id']:<5} {cat['name']:<20} {len(cat_ann_ids)}")

    print("\n" + "=" * 40)
    print("VISUALIZATIONS (Close window to continue)")
    print("=" * 40)

    sample_img_ids = random.sample(img_ids, min(len(img_ids), 3))

    for i, img_id in enumerate(sample_img_ids):
        img_info = coco.loadImgs(img_id)[0]
        img_filename = img_info['file_name']

        img_path = Path(IMAGE_DIR) / Path(img_filename).name

        if not img_path.exists():
            img_path = Path(IMAGE_DIR).parent / Path(img_filename).name

        if not img_path.exists():
            print(f"[WARNING] Image not found: {img_path}")
            continue

        try:
            image = Image.open(img_path)
            plt.figure(figsize=(10, 8))
            plt.imshow(image)
            plt.axis('off')
            plt.title(f"Image ID: {img_id} | File: {img_filename}")

            ann_ids_img = coco.getAnnIds(imgIds=img_id)
            anns = coco.loadAnns(ann_ids_img)

            ax = plt.gca()
            for ann in anns:
                bbox = ann['bbox']
                cat_name = [c['name'] for c in cats if c['id'] == ann['category_id']][0]

                rect = patches.Rectangle(
                    (bbox[0], bbox[1]), bbox[2], bbox[3],
                    linewidth=2, edgecolor='r', facecolor='none'
                )
                ax.add_patch(rect)

                plt.text(
                    bbox[0], bbox[1] - 5,
                    cat_name,
                    color='white', fontsize=10, backgroundcolor='red'
                )

            print(f"Displaying images {i + 1}/3: {img_filename} ({len(anns)} objects)...")
            plt.show()

        except Exception as e:
            print(f"[ERROR] Failed to process image {img_filename}: {e}")


if __name__ == "__main__":
    validate_coco()
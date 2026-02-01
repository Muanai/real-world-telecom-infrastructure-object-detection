import argparse
import sys
import yaml
from pathlib import Path
from ultralytics import YOLO, settings

# PATH SETUP
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


def train(args):
    """
    The main training function adopts the logic from provider-detection-v2-1.ipynb
    """
    print(f" [Start] Training Project: {args.project_name}")
    print(f" Early Model: {args.model}")
    print(f"️ Image Size: {args.imgsz} | Batch: {args.batch}")

    settings.update({'raytune': False})

    # Setup Path Data
    data_path = ROOT / 'data' / 'processed' / args.data_config
    if not data_path.exists():
        print(f"Warning: Config not found in {data_path}")
        print("Searching in the data folder/...")
        potential_paths = list(ROOT.glob(f"data/**/{args.data_config}"))
        if potential_paths:
            data_path = potential_paths[0]
            print(f" Config found in: {data_path}")
        else:
            raise FileNotFoundError(f" Data config '{args.data_config}' lost!")

    # Load Model
    model = YOLO(args.model)

    # Output Directory
    project_dir = ROOT / 'experiments'

    print("\n Training Start with Specific Augmentations...")

    # TRAINING
    results = model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,

        # Output Management
        project=str(project_dir),
        name=args.exp_name,
        exist_ok=True,
        patience=args.patience,

        # AUGMENTATION SETTINGS
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=5.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=args.mosaic,
        mixup=0.1,
        copy_paste=0.1,
        erasing=0.4,

        # System
        optimizer='auto',
        verbose=True,
        seed=42
    )

    print(f"Training completed. Output saved to: {project_dir / args.exp_name}")

    # VALIDATION
    print("\n Running Validation on the Best Model...")
    metrics = model.val(
        data=str(data_path),
        augment=False
    )

    print(f"\n Validation Result:")
    print(f"   mAP50:    {metrics.box.map50:.4f}")
    print(f"   mAP50-95: {metrics.box.map:.4f}")


def parse_opt():
    parser = argparse.ArgumentParser(description='Telkomsel Infrastructure Detection Training Script')

    # Default values
    parser.add_argument('--model', type=str, default='yolov8s.pt', help='Early model')
    parser.add_argument('--data-config', type=str, default='data.yaml', help='Config data file name')
    parser.add_argument('--epochs', type=int, default=100, help='Total epoch')
    parser.add_argument('--batch', type=int, default=16, help='Batch size (Reduce if OOM)')
    parser.add_argument('--imgsz', type=int, default=1240, help='Image size (NB: 1240 is quite large, be careful with VRAM)')
    parser.add_argument('--patience', type=int, default=100, help='Early stopping patience')

    # Eksperimen Management
    parser.add_argument('--project-name', type=str, default='provider_project', help='Main Project Name')
    parser.add_argument('--exp-name', type=str, default='aug_run_v1', help='Experiment Name (output folder)')
    parser.add_argument('--device', type=str, default='0', help='Device (0, 1, or cpu)')
    parser.add_argument('--mosaic', type=float, default=0.5, help='Mosaic Augmentation Probability')

    return parser.parse_args()


if __name__ == "__main__":
    opt = parse_opt()
    train(opt)
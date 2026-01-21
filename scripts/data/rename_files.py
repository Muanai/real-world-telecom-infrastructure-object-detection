import argparse
import os
import re
from pathlib import Path


def natural_key(filename: str):
    match = re.search(r"\d+", filename)
    return int(match.group()) if match else float("inf")


def rename_files(
    directory: Path,
    prefix: str,
    padding: int,
    extension: str,
    dry_run: bool,
):
    files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() == extension.lower()
    ]

    files.sort(key=lambda f: natural_key(f.name))

    print(f"Found {len(files)} files")

    for idx, file in enumerate(files, start=1):
        new_name = f"{prefix}_{str(idx).zfill(padding)}{extension}"
        new_path = directory / new_name

        if file.name == new_name:
            continue  # already correct

        if dry_run:
            print(f"[DRY-RUN] {file.name} -> {new_name}")
        else:
            if new_path.exists():
                raise FileExistsError(f"Target file already exists: {new_name}")
            file.rename(new_path)
            print(f"Renamed: {file.name} -> {new_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename image files with prefix and zero padding (safe & deterministic)."
    )
    parser.add_argument(
        "--dir", type=str, default=".",
        help="Directory containing image files"
    )
    parser.add_argument(
        "--prefix", type=str, default="images",
        help="Filename prefix (default: images)"
    )
    parser.add_argument(
        "--pad", type=int, default=4,
        help="Zero padding length (default: 4 -> 0001)"
    )
    parser.add_argument(
        "--ext", type=str, default=".jpg",
        help="File extension to rename (default: .jpg)"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Apply changes (without this flag, script runs in dry-run mode)"
    )

    args = parser.parse_args()

    rename_files(
        directory=Path(args.dir),
        prefix=args.prefix,
        padding=args.pad,
        extension=args.ext,
        dry_run=not args.apply,
    )

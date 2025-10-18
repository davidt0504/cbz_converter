#!/usr/bin/env python3
"""
RAR to CBZ Converter
Converts RAR archives containing nested directories of images into individual CBZ files.
Handles Unicode (including Japanese) filenames safely.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from typing import List
import rarfile

rarfile.UNRAR_TOOL = "unrar"  # or "unar" if preferred/installed

def find_rar_files(directory: Path) -> List[Path]:
    """Find all .rar files in the specified directory."""
    return sorted(directory.glob("*.rar"))

def extract_rar(rar_path: Path, extract_to: Path) -> Path:
    """Extract a RAR archive to a temporary directory and return its top-level folder."""
    print(f"📦 Extracting: {rar_path.name}")
    with rarfile.RarFile(rar_path) as rf:
        rf.extractall(extract_to)
    items = [p for p in extract_to.iterdir() if not p.name.startswith(".")]
    return items[0] if len(items) == 1 and items[0].is_dir() else extract_to

def create_cbz(source_dir: Path, output_path: Path):
    """Create a CBZ file (ZIP with .cbz extension) from image files."""
    print(f"  📚 Creating: {output_path.name}")
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_STORED) as zbz:
        for root, _, files in os.walk(source_dir):
            for file in sorted(files):
                if file.startswith("."):
                    continue
                file_path = Path(root) / file
                zbz.write(file_path, file_path.relative_to(source_dir))
    print(f"  ✅ Created: {output_path.name}")

def process_rar_file(rar_path: Path, output_dir: Path, temp_dir: Path):
    """Extract one RAR and create CBZ files for each subfolder."""
    basename = rar_path.stem
    extract_path = temp_dir / f"extract_{basename}"
    extract_path.mkdir(parents=True, exist_ok=True)
    try:
        parent_dir = extract_rar(rar_path, extract_path)
        child_dirs = [d for d in parent_dir.iterdir() if d.is_dir()]
        if not child_dirs:
            print(f"  ⚠️  No subdirectories found in {rar_path.name}")
            return
        for child_dir in sorted(child_dirs):
            images = list(child_dir.glob("*.[jJ][pP][gG]")) + \
                        list(child_dir.glob("*.[pP][nN][gG]"))
            if not images:
                print(f"  ⚠️  Skipping {child_dir.name} (no images found)")
                continue
            safe_name = "".join(c if c not in r'\/:*?"<>|' else "_" for c in child_dir.name)
            cbz_path = output_dir / f"{basename}_{safe_name}.cbz"
            create_cbz(child_dir, cbz_path)
    except rarfile.BadRarFile:
        print(f"❌ Invalid RAR file: {rar_path.name}")
    except Exception as e:
        print(f"❌ Error processing {rar_path.name}: {e}")
    finally:
        shutil.rmtree(extract_path, ignore_errors=True)

def main():
    print("=" * 60)
    print("RAR → CBZ Converter")
    print("=" * 60)

    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    output_dir = input_dir / "cbz_output"
    temp_dir = input_dir / "temp_extract"
    output_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)

    print(f"📁 Input:  {input_dir}")
    print(f"📁 Output: {output_dir}\n")

    rar_files = find_rar_files(input_dir)
    if not rar_files:
        print("❌ No .rar files found.")
        return

    for i, rar_path in enumerate(rar_files, 1):
        print(f"[{i}/{len(rar_files)}] {rar_path.name}")
        process_rar_file(rar_path, output_dir, temp_dir)

    shutil.rmtree(temp_dir, ignore_errors=True)
    print("\n✅ All conversions complete!")
    print(f"📚 CBZ files saved to: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()

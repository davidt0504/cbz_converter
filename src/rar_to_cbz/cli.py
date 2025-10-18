"""Command-line interface for archive to CBZ converter."""

import sys
import shutil
from pathlib import Path

from .converter import ARCHIVE_EXTENSIONS, process_archive


def main():
    """Main CLI entry point."""
    print("=" * 60)
    print("Archive → CBZ Converter")
    print("=" * 60)

    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    output_dir = input_dir / "cbz_output"
    temp_dir = input_dir / "temp_extract"
    output_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)

    print(f"📁 Input:  {input_dir}")
    print(f"📁 Output: {output_dir}\n")

    archives = sorted([f for f in input_dir.iterdir() 
                      if f.is_file() and f.suffix.lower() in ARCHIVE_EXTENSIONS])
    if not archives:
        print("❌ No supported archive files found.")
        print(f"   Supported formats: {', '.join(sorted(ARCHIVE_EXTENSIONS))}")
        return

    for i, archive_path in enumerate(archives, 1):
        print(f"[{i}/{len(archives)}] {archive_path.name}")
        process_archive(archive_path, output_dir, temp_dir)

    shutil.rmtree(temp_dir, ignore_errors=True)
    print("\n✅ All conversions complete!")
    print(f"📚 CBZ files saved to: {output_dir}")
    print("=" * 60)

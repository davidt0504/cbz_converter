"""Core conversion logic for archive to CBZ conversion."""

import os
import shutil
import tarfile
import zipfile
from pathlib import Path

import py7zr
import rarfile

rarfile.UNRAR_TOOL = "unrar"

# Supported archive formats
ARCHIVE_EXTENSIONS = {'.rar', '.zip', '.7z', '.tar', '.gz', '.bz2', '.xz'}

# Supported image formats for comic archives
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


def sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in filenames across platforms."""
    return "".join(c if c not in r'\/:*?"<>|' else "_" for c in name)


def extract_archive(archive_path: Path, extract_to: Path) -> Path:
    """Extract an archive to a temporary directory and return its top-level folder.
    
    Supports: RAR, ZIP, 7z, TAR (including .tar.gz, .tar.bz2, .tar.xz)
    """
    print(f"📦 Extracting: {archive_path.name}")
    suffix = archive_path.suffix.lower()
    
    # Extract based on archive type
    if suffix == '.rar':
        with rarfile.RarFile(archive_path) as rf:
            rf.extractall(extract_to)
    elif suffix == '.zip':
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(extract_to)
    elif suffix == '.7z':
        with py7zr.SevenZipFile(archive_path) as sz:
            sz.extractall(extract_to)
    elif suffix in {'.tar', '.gz', '.bz2', '.xz'}:
        # tarfile.open() auto-detects compression (gzip, bzip2, xz)
        with tarfile.open(archive_path) as tf:
            tf.extractall(extract_to)
    else:
        raise ValueError(f"Unsupported archive format: {suffix}")
    
    # If archive contains a single directory, unwrap it
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


def process_archive(archive_path: Path, output_dir: Path, temp_dir: Path):
    """Extract an archive and create CBZ files for each subfolder."""
    basename = archive_path.stem
    extract_path = temp_dir / f"extract_{basename}"
    extract_path.mkdir(parents=True, exist_ok=True)
    
    try:
        parent_dir = extract_archive(archive_path, extract_path)
        child_dirs = [d for d in parent_dir.iterdir() if d.is_dir()]
        
        if not child_dirs:
            print(f"  ⚠️  No subdirectories found in {archive_path.name}")
            return
        
        for child_dir in sorted(child_dirs):
            images = [f for f in child_dir.iterdir() 
                     if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
            
            if not images:
                print(f"  ⚠️  Skipping {child_dir.name} (no images found)")
                continue
            
            safe_name = sanitize_filename(child_dir.name)
            cbz_path = output_dir / f"{basename}_{safe_name}.cbz"
            create_cbz(child_dir, cbz_path)
    
    except (rarfile.BadRarFile, zipfile.BadZipFile, tarfile.ReadError, py7zr.Bad7zFile):
        print(f"❌ Invalid or corrupt archive: {archive_path.name}")
    except Exception as e:
        print(f"❌ Error processing {archive_path.name}: {e}")
    finally:
        shutil.rmtree(extract_path, ignore_errors=True)

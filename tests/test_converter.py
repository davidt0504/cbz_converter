"""Tests for archive conversion functionality."""

import zipfile
import tarfile
from pathlib import Path

import pytest

from rar_to_cbz.converter import (
    ARCHIVE_EXTENSIONS,
    IMAGE_EXTENSIONS,
    sanitize_filename,
    extract_archive,
    create_cbz,
)


class TestFilenameSanitization:
    """Test sanitize_filename function."""

    def test_removes_invalid_characters(self):
        """Test that invalid filename characters are replaced with underscores."""
        assert sanitize_filename('file:name') == 'file_name'
        assert sanitize_filename('file\\path') == 'file_path'
        assert sanitize_filename('file/path') == 'file_path'
        assert sanitize_filename('file*name') == 'file_name'
        assert sanitize_filename('file?name') == 'file_name'
        assert sanitize_filename('file"name') == 'file_name'
        assert sanitize_filename('file<name>') == 'file_name_'
        assert sanitize_filename('file|name') == 'file_name'

    def test_preserves_valid_characters(self):
        """Test that valid characters are preserved."""
        assert sanitize_filename('Dragon Ball v01') == 'Dragon Ball v01'
        assert sanitize_filename('Volume.01') == 'Volume.01'
        assert sanitize_filename('Chapter-05') == 'Chapter-05'
        assert sanitize_filename('漫画_01') == '漫画_01'  # Japanese characters

    def test_handles_multiple_invalid_characters(self):
        """Test handling of multiple invalid characters."""
        assert sanitize_filename('a:b\\c/d*e?f') == 'a_b_c_d_e_f'


class TestConstants:
    """Test module-level constants."""

    def test_archive_extensions(self):
        """Verify supported archive formats."""
        expected = {'.rar', '.zip', '.7z', '.tar', '.gz', '.bz2', '.xz'}
        assert ARCHIVE_EXTENSIONS == expected

    def test_image_extensions(self):
        """Verify supported image formats."""
        expected = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        assert IMAGE_EXTENSIONS == expected


class TestArchiveExtraction:
    """Test archive extraction functionality."""

    def test_extract_zip_single_folder(self, tmp_path):
        """Test ZIP extraction with single nested folder."""
        # Create a test ZIP with nested structure
        archive_path = tmp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("Volume 01/page01.jpg", b"fake image data")
            zf.writestr("Volume 01/page02.jpg", b"fake image data")
        
        extract_to = tmp_path / "extract"
        extract_to.mkdir()
        
        result = extract_archive(archive_path, extract_to)
        
        # Should unwrap the single folder
        assert result.name == "Volume 01"
        assert (result / "page01.jpg").exists()
        assert (result / "page02.jpg").exists()

    def test_extract_zip_multiple_folders(self, tmp_path):
        """Test ZIP extraction with multiple top-level folders."""
        archive_path = tmp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("Volume 01/page01.jpg", b"fake image")
            zf.writestr("Volume 02/page01.jpg", b"fake image")
        
        extract_to = tmp_path / "extract"
        extract_to.mkdir()
        
        result = extract_archive(archive_path, extract_to)
        
        # Should NOT unwrap (multiple folders)
        assert result == extract_to
        assert (result / "Volume 01").is_dir()
        assert (result / "Volume 02").is_dir()

    def test_extract_tar(self, tmp_path):
        """Test TAR extraction."""
        archive_path = tmp_path / "test.tar"
        with tarfile.open(archive_path, 'w') as tf:
            # Create in-memory file
            file_data = b"fake image"
            from io import BytesIO
            import tarfile as tf_module
            
            info = tf_module.TarInfo(name="Volume 01/page01.jpg")
            info.size = len(file_data)
            tf.addfile(info, BytesIO(file_data))
        
        extract_to = tmp_path / "extract"
        extract_to.mkdir()
        
        result = extract_archive(archive_path, extract_to)
        
        assert result.name == "Volume 01"
        assert (result / "page01.jpg").exists()

    def test_extract_tar_gz(self, tmp_path):
        """Test compressed TAR extraction."""
        archive_path = tmp_path / "test.tar.gz"
        with tarfile.open(archive_path, 'w:gz') as tf:
            from io import BytesIO
            import tarfile as tf_module
            
            info = tf_module.TarInfo(name="test/file.txt")
            info.size = 4
            tf.addfile(info, BytesIO(b"test"))
        
        extract_to = tmp_path / "extract"
        extract_to.mkdir()
        
        result = extract_archive(archive_path, extract_to)
        
        assert (result / "file.txt").exists()

    def test_extract_ignores_hidden_files(self, tmp_path):
        """Test that hidden files are ignored during unwrap detection."""
        archive_path = tmp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("Volume 01/page01.jpg", b"fake")
            zf.writestr(".DS_Store", b"hidden")
        
        extract_to = tmp_path / "extract"
        extract_to.mkdir()
        
        result = extract_archive(archive_path, extract_to)
        
        # Should still unwrap because .DS_Store is ignored
        assert result.name == "Volume 01"

    def test_unsupported_format_raises_error(self, tmp_path):
        """Test that unsupported formats raise ValueError."""
        fake_archive = tmp_path / "test.unknown"
        fake_archive.write_text("not an archive")
        
        extract_to = tmp_path / "extract"
        extract_to.mkdir()
        
        with pytest.raises(ValueError, match="Unsupported archive format"):
            extract_archive(fake_archive, extract_to)


class TestCBZCreation:
    """Test CBZ file creation."""

    def test_create_cbz_from_directory(self, tmp_path):
        """Test creating CBZ from a directory with images."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create fake image files
        (source_dir / "page01.jpg").write_bytes(b"fake jpg")
        (source_dir / "page02.png").write_bytes(b"fake png")
        (source_dir / ".hidden").write_bytes(b"hidden file")
        
        output_path = tmp_path / "output.cbz"
        
        create_cbz(source_dir, output_path)
        
        # Verify CBZ is a valid ZIP
        assert output_path.exists()
        with zipfile.ZipFile(output_path, 'r') as zf:
            names = zf.namelist()
            assert "page01.jpg" in names
            assert "page02.png" in names
            assert ".hidden" not in names  # Hidden files excluded

    def test_create_cbz_preserves_order(self, tmp_path):
        """Test that files are sorted in CBZ."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create files in non-alphabetical order
        (source_dir / "page10.jpg").write_bytes(b"10")
        (source_dir / "page02.jpg").write_bytes(b"02")
        (source_dir / "page01.jpg").write_bytes(b"01")
        
        output_path = tmp_path / "output.cbz"
        create_cbz(source_dir, output_path)
        
        with zipfile.ZipFile(output_path, 'r') as zf:
            names = zf.namelist()
            # Files should be in sorted order
            assert names == ["page01.jpg", "page02.jpg", "page10.jpg"]

    def test_create_cbz_with_subdirectories(self, tmp_path):
        """Test CBZ creation with nested directory structure."""
        source_dir = tmp_path / "source"
        subdir = source_dir / "chapter1"
        subdir.mkdir(parents=True)
        
        (subdir / "page01.jpg").write_bytes(b"page")
        
        output_path = tmp_path / "output.cbz"
        create_cbz(source_dir, output_path)
        
        with zipfile.ZipFile(output_path, 'r') as zf:
            names = zf.namelist()
            assert "chapter1/page01.jpg" in names


class TestImageDetection:
    """Test image file detection logic."""

    def test_supported_image_formats(self, tmp_path):
        """Test that all supported image formats are detected."""
        test_dir = tmp_path / "images"
        test_dir.mkdir()
        
        # Create files with different extensions
        formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        for ext in formats:
            (test_dir / f"image{ext}").write_bytes(b"fake")
        
        # Simulate our image detection logic
        images = [f for f in test_dir.iterdir() 
                 if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
        
        assert len(images) == len(formats)

    def test_case_insensitive_detection(self, tmp_path):
        """Test that image detection is case-insensitive."""
        test_dir = tmp_path / "images"
        test_dir.mkdir()
        
        (test_dir / "image.JPG").write_bytes(b"fake")
        (test_dir / "image.Png").write_bytes(b"fake")
        
        images = [f for f in test_dir.iterdir() 
                 if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
        
        assert len(images) == 2

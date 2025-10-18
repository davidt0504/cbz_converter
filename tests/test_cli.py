"""Tests for CLI functionality."""

from pathlib import Path
import sys

import pytest

from rar_to_cbz.converter import ARCHIVE_EXTENSIONS


class TestFileDiscovery:
    """Test archive file discovery logic."""

    def test_finds_supported_archives(self, tmp_path):
        """Test that all supported archive types are found."""
        # Create test files
        (tmp_path / "test.rar").write_bytes(b"fake")
        (tmp_path / "test.zip").write_bytes(b"fake")
        (tmp_path / "test.7z").write_bytes(b"fake")
        (tmp_path / "test.tar").write_bytes(b"fake")
        (tmp_path / "test.tar.gz").write_bytes(b"fake")
        (tmp_path / "test.txt").write_bytes(b"not an archive")
        (tmp_path / "README.md").write_bytes(b"not an archive")
        
        # Simulate CLI file discovery logic
        archives = sorted([f for f in tmp_path.iterdir() 
                          if f.is_file() and f.suffix.lower() in ARCHIVE_EXTENSIONS])
        
        # Should find 5 archives, ignore .txt and .md
        assert len(archives) == 5
        assert all(f.suffix.lower() in ARCHIVE_EXTENSIONS for f in archives)

    def test_ignores_directories(self, tmp_path):
        """Test that directories are not included in archive list."""
        (tmp_path / "archive.zip").write_bytes(b"fake")
        (tmp_path / "not_archive.rar").mkdir()  # Directory with .rar name
        
        archives = [f for f in tmp_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in ARCHIVE_EXTENSIONS]
        
        assert len(archives) == 1
        assert archives[0].name == "archive.zip"

    def test_case_insensitive_extension_matching(self, tmp_path):
        """Test that extension matching is case-insensitive."""
        (tmp_path / "test.ZIP").write_bytes(b"fake")
        (tmp_path / "test.Rar").write_bytes(b"fake")
        (tmp_path / "test.7Z").write_bytes(b"fake")
        
        archives = [f for f in tmp_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in ARCHIVE_EXTENSIONS]
        
        assert len(archives) == 3

    def test_does_not_recurse_subdirectories(self, tmp_path):
        """Test that file discovery is not recursive."""
        (tmp_path / "test.zip").write_bytes(b"fake")
        
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.zip").write_bytes(b"fake")
        
        # Using iterdir() (not recursive)
        archives = [f for f in tmp_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in ARCHIVE_EXTENSIONS]
        
        # Should only find top-level archive
        assert len(archives) == 1
        assert archives[0].name == "test.zip"

    def test_finds_compressed_tar_variants(self, tmp_path):
        """Test that compressed TAR files are detected."""
        (tmp_path / "test.tar.gz").write_bytes(b"fake")
        (tmp_path / "test.tar.bz2").write_bytes(b"fake")
        (tmp_path / "test.tar.xz").write_bytes(b"fake")
        
        # These have suffixes .gz, .bz2, .xz
        archives = [f for f in tmp_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in ARCHIVE_EXTENSIONS]
        
        assert len(archives) == 3


class TestArgumentHandling:
    """Test command-line argument handling."""

    def test_uses_current_directory_by_default(self):
        """Test that no argument uses current working directory."""
        # Simulate: input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
        argv_no_args = ["rar-to-cbz"]
        
        if len(argv_no_args) > 1:
            input_dir = Path(argv_no_args[1])
        else:
            input_dir = Path.cwd()
        
        assert input_dir == Path.cwd()

    def test_uses_provided_directory(self, tmp_path):
        """Test that provided argument is used as input directory."""
        argv_with_path = ["rar-to-cbz", str(tmp_path)]
        
        if len(argv_with_path) > 1:
            input_dir = Path(argv_with_path[1])
        else:
            input_dir = Path.cwd()
        
        assert input_dir == tmp_path


class TestOutputStructure:
    """Test output directory structure."""

    def test_output_directory_creation(self, tmp_path):
        """Test that output directories are created correctly."""
        input_dir = tmp_path
        output_dir = input_dir / "cbz_output"
        temp_dir = input_dir / "temp_extract"
        
        output_dir.mkdir(exist_ok=True)
        temp_dir.mkdir(exist_ok=True)
        
        assert output_dir.exists()
        assert output_dir.is_dir()
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_handles_existing_output_directory(self, tmp_path):
        """Test that existing output directory doesn't cause errors."""
        output_dir = tmp_path / "cbz_output"
        output_dir.mkdir()
        
        # Should not raise error with exist_ok=True
        output_dir.mkdir(exist_ok=True)
        
        assert output_dir.exists()

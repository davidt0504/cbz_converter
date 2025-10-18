# Archive to CBZ Converter

A command-line tool to convert comic/manga archives (RAR, ZIP, 7z, TAR) into CBZ format for use with e-readers and comic book readers like Kindle Comic Converter.

## Features

- **Multi-format support**: RAR, ZIP, 7z, TAR (including .tar.gz, .tar.bz2, .tar.xz)
- **Batch processing**: Convert multiple archives at once
- **Smart extraction**: Automatically handles nested folder structures
- **Unicode support**: Handles Japanese and other non-ASCII filenames
- **Progress display**: Real-time feedback during conversion

## Installation

### Requirements

- Python 3.8 or higher
- `unrar` command-line tool (for RAR support)

Install `unrar`:

```bash
# Ubuntu/Debian
sudo apt install unrar

# macOS
brew install unrar

# Arch Linux
sudo pacman -S unrar
```

### Install from PyPI (coming soon)

```bash
pip install rar-to-cbz
```

### Install from source

```bash
git clone https://github.com/yourusername/cbz_converter.git
cd cbz_converter
pip install .
```

## Usage

### Basic usage

Convert all archives in the current directory:

```bash
rar-to-cbz
```

Convert archives in a specific directory:

```bash
rar-to-cbz /path/to/comics
```

### What it does

1. Finds all supported archive files in the directory
2. Extracts each archive to a temporary folder
3. Creates individual CBZ files for each volume/chapter found inside
4. Saves output to `cbz_output/` subdirectory
5. Cleans up temporary files

### Example

```
comics/
├── Dragon Ball v01-05.rar
├── Dragon Ball v06-10.zip
└── Dragon Ball v11-15.7z

$ rar-to-cbz comics/

Output:
comics/cbz_output/
├── Dragon Ball v01-05_Dragon Ball - Volume.01.cbz
├── Dragon Ball v01-05_Dragon Ball - Volume.02.cbz
├── ...
```

## Supported Formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| RAR | `.rar` | Requires `unrar` tool |
| ZIP | `.zip` | Built-in support |
| 7-Zip | `.7z` | Built-in support |
| TAR | `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz` | Built-in support |

## Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- WebP (`.webp`)
- BMP (`.bmp`)

## Contributing

Contributions are welcome! To get started:

```bash
# Clone and install
git clone https://github.com/yourusername/cbz_converter.git
cd cbz_converter
pip install -e ".[dev]"

# Run tests
pytest

# Test locally
rar-to-cbz /path/to/test/files
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [rarfile](https://github.com/markokr/rarfile), [py7zr](https://github.com/miurahr/py7zr), and Python's standard library
- Inspired by the need to prepare manga collections for Kindle Comic Converter

## Troubleshooting

**No archives found?** Ensure files have correct extensions (`.rar`, `.zip`, `.7z`, `.tar`).

**Extraction fails?** Install `unrar` for RAR support: `sudo apt install unrar`

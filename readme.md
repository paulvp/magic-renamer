**Setup:**
```bash
git clone https://github.com/paulvp/magic-renamer
cd magicrenamer
chmod +x magic-renamer.sh magicrenamer_web.py

uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Usage

### Web

```bash
# Run the web interface
uv run magicrenamer_web.py
```

Features: Select specific images, visual directory browser, real-time progress, optional prefix naming, **AI-powered smart cropping** for training datasets.

### CLI Mode (You need to be brave to open the console!)

```bash
./magicrenamer.sh -i
```

**Options:**
- `-p <path>` - Specify directory
- `-n <prefix>` - Set naming prefix (e.g., `anna-1.png`)
- `-i` - Interactive mode
- `-y` - Skip confirmations
- `-h` - Show help

## 🎯 Complete Workflow Example

Let's say you have a folder with mixed images for training a LoRA model of a character named "anna":

```
/home/user/anna_training/
├── IMG_3847.jpg
├── downloaded_pic.webp
├── photo_2024_01_15.png
├── screenshot_001.jpg
└── ... (196 more files)
```

**Run MagicRenamer:**
```bash
cd /home/user/anna_training
./magicrenamer.sh -i
```

**Interactive prompts:**
```
Found 200 image(s) to process

Sample files in directory:
IMG_3847.jpg
downloaded_pic.webp
photo_2024_01_15.png
screenshot_001.jpg
... and 196 more

Do you want to add a naming prefix?
Prefix: anna

Naming convention: anna-1.png, anna-2.png, anna-3.png, ...

This will:
  1. Convert all images to PNG format
  2. Delete all original files
  3. Rename images sequentially

Do you want to continue? (yes/no): yes
```

**Result:**
```
/home/user/anna_training/
├── anna-1.png
├── anna-2.png
├── anna-3.png
├── anna-4.png
└── ... (196 more files)
```

### Supported Formats
**Input formats:**
- JPG/JPEG
- PNG
- WebP
- GIF
- BMP
- TIFF/TIF

**Output format:**
- PNG (always)

### Performance
- Processing 200 images typically takes **30-60 seconds**
- Depends on image sizes and system performance
- No quality loss (PNG is lossless)

## 🛠️echnical Details

### What the Script Does

1. **Conversion Phase**: 
   - Scans for all supported image formats
   - Converts each to PNG with temporary naming (`temp_0001.png`)
   - Uses ImageMagick for high-quality conversion

2. **Cleanup Phase**:
   - Removes all original files
   - Only temp files remain

3. **Renaming Phase**:
   - Renames temp files sequentially
   - Applies prefix if specified
   - Final format: `prefix-N.png` or `N.png`

### Why PNG?
- **Lossless compression**: No quality degradation
- **Wide compatibility**: Supported by all ML frameworks
- **Consistent format**: Eliminates format-related training issues
- **Alpha channel support**: Handles transparency properly

MIT License

---

<p align="center">
  Made with ☕️
</p>

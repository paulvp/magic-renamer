# MagicRenamer

[🇷🇺 Русский](readme_ru.md) | [🇮🇳 हिन्दी](readme_hi.md)

![](assets/demo.mp4)

## Why I Created It?

When training LoRA models, I sometimes have hundreds of images of a single character or subject. The typical workflow looks like this:

1. Collect 100-200+ images from various sources
2. Each image has a different format (JPG, PNG, WebP, etc.)
3. Each image has a cryptic filename like `IMG_20231015_143522.jpg`
4. You need to manually edit and rename each one... **one by one** 😱

I was spending hours just organizing files instead of actually training my models, so I created a bash script first and then also a web UI for more comfort.

### The Problem I Had
- ❌ Manually renaming +100 images
- ❌ Inconsistent file formats causing training issues
- ❌ Repetitive, soul-crushing work

### The Solution I Created
**MagicRenamer** automates the entire process:
- ✅ Batch convert to PNG (the standard for training):
- ✅ Sequential naming with optional prefixes: **Automated**
- ✅ Process 100+ images: **Under a minute**
- ✅ Clean, organized dataset ready for training

## ✨ Features

- 🔄 **Batch Conversion**: Convert all images to PNG format
- 📝 **Sequential Renaming**: Rename files as 1.png, 2.png, 3.png...
- 🏷️ **Custom Prefixes**: Add prefixes like `anna-1.png`, `anna-2.png`
- 🎨 **Interactive UI**: Beautiful colored terminal interface
- 💬 **Interactive Mode**: Guided prompts for easy use
- ⚡ **Multiple Format Support**: JPG, PNG, WebP, GIF, BMP, TIFF
- 🛡️ **Safety Features**: Confirmation prompts before destructive operations
- 📊 **Progress Tracking**: Real-time feedback with success/failure counts
- 🎯 **Smart Crop**: AI-powered attention detection to keep important features when resizing
- 📐 **Training Presets**: Quick resize to 512x512, 768x768, 1024x1024, 2048x2048

## 📋 Use Cases

### Perfect for:
- 🤖 **AI/ML Training Datasets**: Organize images for LoRA, Stable Diffusion, or custom model training
- 📸 **Photography Collections**: Batch process and organize photo shoots
- 🎮 **Game Assets**: Prepare sprite sheets or texture collections
- 📚 **Digital Archives**: Standardize image libraries
- 🎨 **Art Projects**: Organize reference images or artwork collections

**Setup:**
```bash
git clone https://github.com/paulvp/magic-renamer
cd magicrenamer
chmod +x magic-renamer.sh magicrenamer_web.py

# For web interface with smart crop
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## 📖 Usage

### Web (Easiest way!)

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

## 🛠️ Technical Details

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

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions
- [ ] Add support for custom output formats (keep as JPG option)
- [ ] Implement dry-run mode to preview changes
- [ ] Add image quality/compression options
- [ ] Create undo functionality (backup system)
- [ ] Add image filtering (by size, dimensions, etc.)
- [ ] Progress bar for large batches
- [ ] Resize images (already renamed for AI Training supported formats (512x512, 768x768, 1024x1024, 2048x2048) (by center of image or manually for each image))

## 📝 License

MIT License

---

<p align="center">
  Made with ☕️ and 🌃
</p>

<p align="center">
  <sub>add ⭐</sub>
</p>
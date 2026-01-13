#!/bin/bash

# ImageMagick Image Renamer Script
# A tool for batch converting and renaming images with sequential numbering
# Perfect for organizing training datasets for AI/ML models

VERSION="2.1.0"

# Color codes for better UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Function to display usage
usage() {
    echo -e "${BOLD}ImageMagick Image Renamer v${VERSION}${NC}"
    echo ""
    echo -e "${CYAN}Usage:${NC} $0 [-p path] [-n prefix] [-r size] [-c center|manual] [-i] [-y]"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo "  -p path    Specify the path to the image folder"
    echo "  -n prefix  Set naming prefix (e.g., 'anna' for anna-1.png, anna-2.png)"
    echo "  -r size    Resize images (512, 768, 1024, 2048)"
    echo "  -c mode    Crop mode: 'center' (default) or 'manual' for each image"
    echo "  -i         Interactive mode (ask for prefix and confirmation)"
    echo "  -y         Skip all confirmations (use with caution!)"
    echo "  -h         Show this help message"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 -i                                    # Interactive mode"
    echo "  $0 -p /path/to/images -i                 # Interactive mode for specific directory"
    echo "  $0 -n anna -r 1024 -p /path/to/images    # Use 'anna' prefix and resize to 1024x1024"
    echo "  $0 -n character_001 -r 512 -c manual     # Manual crop for each image"
    echo ""
    exit 1
}

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_step() {
    echo -e "${MAGENTA}${BOLD}$1${NC}"
}

# Function to display progress bar
progress_bar() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    printf "\r  ["
    printf "%${completed}s" | tr ' ' '='
    printf "%${remaining}s" | tr ' ' '-'
    printf "] %3d%% (%d/%d)" $percentage $current $total
}

# Function to get image dimensions
get_dimensions() {
    local file="$1"
    identify -format "%wx%h" "$file" 2>/dev/null
}

# Function to resize and crop image (center crop)
resize_center_crop() {
    local input="$1"
    local output="$2"
    local target_size="$3"
    
    # Get original dimensions
    local dims=$(get_dimensions "$input")
    local width=$(echo "$dims" | cut -d'x' -f1)
    local height=$(echo "$dims" | cut -d'x' -f2)
    
    if [ -z "$width" ] || [ -z "$height" ]; then
        return 1
    fi
    
    # Calculate aspect ratios
    local orig_ratio=$(awk "BEGIN {print $width / $height}")
    local target_ratio=1.0
    
    # Determine crop dimensions
    if (( $(awk "BEGIN {print ($orig_ratio > $target_ratio)}") )); then
        # Image is wider - crop width
        local new_width=$(awk "BEGIN {print int($height * $target_ratio)}")
        local offset_x=$(awk "BEGIN {print int(($width - $new_width) / 2)}")
        magick "$input" -crop "${new_width}x${height}+${offset_x}+0" -resize "${target_size}x${target_size}" "$output" 2>/dev/null
    else
        # Image is taller - crop height
        local new_height=$(awk "BEGIN {print int($width / $target_ratio)}")
        local offset_y=$(awk "BEGIN {print int(($height - $new_height) / 2)}")
        magick "$input" -crop "${width}x${new_height}+0+${offset_y}" -resize "${target_size}x${target_size}" "$output" 2>/dev/null
    fi
    
    return $?
}

# Function to manually crop image
manual_crop() {
    local input="$1"
    local output="$2"
    local target_size="$3"
    
    local dims=$(get_dimensions "$input")
    echo ""
    print_info "Original dimensions: ${BOLD}${dims}${NC}"
    echo ""
    echo "Enter crop coordinates (x, y, width, height):"
    echo "Example: 100 50 800 800"
    echo -n "Coordinates: "
    read -r crop_x crop_y crop_w crop_h
    
    if [ -z "$crop_x" ] || [ -z "$crop_y" ] || [ -z "$crop_w" ] || [ -z "$crop_h" ]; then
        print_warning "Invalid coordinates, using center crop"
        resize_center_crop "$input" "$output" "$target_size"
        return $?
    fi
    
    magick "$input" -crop "${crop_w}x${crop_h}+${crop_x}+${crop_y}" -resize "${target_size}x${target_size}" "$output" 2>/dev/null
    return $?
}

# Check if ImageMagick is installed
if ! command -v magick &> /dev/null; then
    print_error "ImageMagick is not installed or 'magick' command not found"
    echo "Please install ImageMagick first:"
    echo "  Ubuntu/Debian: sudo apt-get install imagemagick"
    echo "  macOS: brew install imagemagick"
    echo "  Fedora: sudo dnf install ImageMagick"
    exit 1
fi

# Default values
IMAGE_DIR="."
PREFIX=""
RESIZE_SIZE=""
CROP_MODE="center"
INTERACTIVE=false
SKIP_CONFIRM=false

# Parse command line arguments
while getopts "p:n:r:c:iyh" opt; do
    case $opt in
        p)
            IMAGE_DIR="$OPTARG"
            ;;
        n)
            PREFIX="$OPTARG"
            ;;
        r)
            RESIZE_SIZE="$OPTARG"
            if [[ ! "$RESIZE_SIZE" =~ ^(512|768|1024|2048)$ ]]; then
                print_error "Invalid resize size. Must be 512, 768, 1024, or 2048"
                exit 1
            fi
            ;;
        c)
            CROP_MODE="$OPTARG"
            if [[ ! "$CROP_MODE" =~ ^(center|manual)$ ]]; then
                print_error "Invalid crop mode. Must be 'center' or 'manual'"
                exit 1
            fi
            ;;
        i)
            INTERACTIVE=true
            ;;
        y)
            SKIP_CONFIRM=true
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            ;;
    esac
done

# Change to the image directory
cd "$IMAGE_DIR" || { print_error "Cannot access directory $IMAGE_DIR"; exit 1; }

# Display banner
echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   ImageMagick Image Renamer v${VERSION}          ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""

print_info "Working directory: ${BOLD}$(pwd)${NC}"
echo ""

# Count images before processing
image_count=$(find . -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.tif" \) | wc -l)

if [ "$image_count" -eq 0 ]; then
    print_error "No image files found in the current directory"
    exit 1
fi

print_info "Found ${BOLD}${image_count}${NC} image(s) to process"
echo ""

# Interactive mode
if [ "$INTERACTIVE" = true ]; then
    echo -e "${CYAN}${BOLD}Interactive Mode${NC}"
    echo ""
    
    # Show sample files
    echo -e "${CYAN}Sample files in directory:${NC}"
    find . -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.tif" \) | head -5 | sed 's|./||'
    if [ "$image_count" -gt 5 ]; then
        echo "... and $((image_count - 5)) more"
    fi
    echo ""
    
    # Ask for prefix
    echo -e "${CYAN}Do you want to add a naming prefix?${NC}"
    echo "  (Leave empty for no prefix, or enter name like 'anna' for anna-1.png, anna-2.png, etc.)"
    echo -n "Prefix: "
    read user_prefix
    PREFIX="$user_prefix"
    
    # Ask for resize
    echo ""
    echo -e "${CYAN}Do you want to resize images for AI training?${NC}"
    echo "  Available sizes: 512x512, 768x768, 1024x1024, 2048x2048"
    echo "  (Leave empty to skip resizing)"
    echo -n "Size: "
    read user_size
    if [[ "$user_size" =~ ^(512|768|1024|2048)$ ]]; then
        RESIZE_SIZE="$user_size"
        
        echo ""
        echo -e "${CYAN}Crop mode:${NC}"
        echo "  1) Center crop (automatic, crops from center)"
        echo "  2) Manual crop (you specify coordinates for each image)"
        echo -n "Choice (1/2): "
        read crop_choice
        if [ "$crop_choice" = "2" ]; then
            CROP_MODE="manual"
        else
            CROP_MODE="center"
        fi
    fi
fi

# Display naming convention
echo ""
if [ -n "$PREFIX" ]; then
    print_info "Naming convention: ${BOLD}${PREFIX}-1.png, ${PREFIX}-2.png, ${PREFIX}-3.png, ...${NC}"
else
    print_info "Naming convention: ${BOLD}1.png, 2.png, 3.png, ...${NC}"
fi

if [ -n "$RESIZE_SIZE" ]; then
    print_info "Resize: ${BOLD}${RESIZE_SIZE}x${RESIZE_SIZE} (${CROP_MODE} crop)${NC}"
fi
echo ""

# Confirmation prompt (unless -y flag is used)
if [ "$SKIP_CONFIRM" = false ]; then
    print_warning "This will:"
    echo "  1. Convert all images to PNG format"
    if [ -n "$RESIZE_SIZE" ]; then
        echo "  2. Resize images to ${RESIZE_SIZE}x${RESIZE_SIZE}"
        echo "  3. Delete all original files"
        echo "  4. Rename images sequentially"
    else
        echo "  2. Delete all original files"
        echo "  3. Rename images sequentially"
    fi
    echo ""
    echo -e "${YELLOW}${BOLD}This action cannot be undone!${NC}"
    echo -n "Do you want to continue? (yes/no): "
    read confirmation
    
    if [ "$confirmation" != "yes" ] && [ "$confirmation" != "y" ]; then
        print_info "Operation cancelled by user"
        exit 0
    fi
fi

echo ""
print_step "═══════════════════════════════════════════════"
print_step "Starting Image Processing"
print_step "═══════════════════════════════════════════════"
echo ""

# Step 1: Convert and optionally resize images
if [ -n "$RESIZE_SIZE" ]; then
    print_step "Step 1: Converting and resizing to ${RESIZE_SIZE}x${RESIZE_SIZE}..."
else
    print_step "Step 1: Converting images to PNG format..."
fi
echo ""

i=1
converted=0
failed=0
total_files=$image_count

for f in *.{jpg,jpeg,JPG,JPEG,png,PNG,webp,WEBP,gif,GIF,bmp,BMP,tiff,TIFF,tif,TIF}; do
    if [ -f "$f" ] && [[ "$f" != temp_* ]]; then
        temp_name="temp_$(printf "%04d" $i).png"
        
        progress_bar $((i-1)) $total_files
        
        if [ -n "$RESIZE_SIZE" ]; then
            if [ "$CROP_MODE" = "manual" ]; then
                echo ""
                print_info "Processing: ${BOLD}$f${NC}"
                if manual_crop "$f" "$temp_name" "$RESIZE_SIZE"; then
                    ((i++))
                    ((converted++))
                else
                    print_error "Failed to process $f"
                    ((failed++))
                fi
            else
                if resize_center_crop "$f" "$temp_name" "$RESIZE_SIZE"; then
                    ((i++))
                    ((converted++))
                else
                    ((failed++))
                fi
            fi
        else
            if magick "$f" "$temp_name" 2>/dev/null; then
                ((i++))
                ((converted++))
            else
                ((failed++))
            fi
        fi
    fi
done

progress_bar $total_files $total_files
echo ""
echo ""
print_success "Step 1 completed: ${BOLD}${converted}${NC} images processed"
if [ "$failed" -gt 0 ]; then
    print_warning "$failed images failed to process"
fi

echo ""
print_info "Waiting 2 seconds before cleanup..."
sleep 2

# Step 2: Remove all original images
echo ""
print_step "Step 2: Removing original files..."
echo ""

removed=0
current=0
for f in *.{jpg,jpeg,JPG,JPEG,png,PNG,webp,WEBP,gif,GIF,bmp,BMP,tiff,TIFF,tif,TIF}; do
    if [ -f "$f" ] && [[ "$f" != temp_* ]]; then
        progress_bar $current $total_files
        if rm "$f" 2>/dev/null; then
            ((removed++))
        fi
        ((current++))
    fi
done

progress_bar $total_files $total_files
echo ""
echo ""
print_success "Step 2 completed: ${BOLD}${removed}${NC} original files removed"

# Step 3: Rename temp_ files to final names
echo ""
print_step "Step 3: Renaming to sequential numbers..."
echo ""

i=1
renamed=0
temp_count=$(ls temp_*.png 2>/dev/null | wc -l)
current=0

for f in temp_*.png; do
    if [ -f "$f" ]; then
        if [ -n "$PREFIX" ]; then
            new_name="${PREFIX}-${i}.png"
        else
            new_name="${i}.png"
        fi
        
        progress_bar $current $temp_count
        if mv "$f" "$new_name" 2>/dev/null; then
            ((i++))
            ((renamed++))
        fi
        ((current++))
    fi
done

progress_bar $temp_count $temp_count
echo ""
echo ""
print_success "Step 3 completed: ${BOLD}${renamed}${NC} files renamed"

# Final summary
echo ""
print_step "═══════════════════════════════════════════════"
print_step "Process Completed Successfully!"
print_step "═══════════════════════════════════════════════"
echo ""

if [ -n "$PREFIX" ]; then
    print_success "Created ${BOLD}${renamed}${NC} images: ${PREFIX}-1.png, ${PREFIX}-2.png, ${PREFIX}-3.png, ..."
else
    print_success "Created ${BOLD}${renamed}${NC} images: 1.png, 2.png, 3.png, ..."
fi

if [ -n "$RESIZE_SIZE" ]; then
    print_info "All images resized to ${BOLD}${RESIZE_SIZE}x${RESIZE_SIZE}${NC}"
fi

echo ""
print_info "All images are now in PNG format with sequential numbering"
echo ""
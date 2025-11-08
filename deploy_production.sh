#!/bin/bash

# Production Deployment Script for ATM Maintenance System
# This script prepares the project for deployment to Render (backend) and Hostinger (frontend)
# Usage: chmod +x deploy_production.sh && ./deploy_production.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="./backend"
FRONTEND_DIR="./frontend/atm_frontend"
BUILD_OUTPUT="./frontend/atm_frontend/build"
MEDIA_OUTPUT="./media.zip"
STATICFILES_OUTPUT="./backend/staticfiles"

echo -e "${CYAN}========================================"
echo "ATM Maintenance System - Production Deployment"
echo "========================================${NC}"
echo ""

# Step 1: Verify directories exist
echo -e "${YELLOW}[1/6] Verifying project structure...${NC}"
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}ERROR: Backend directory not found at $BACKEND_DIR${NC}"
    exit 1
fi
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}ERROR: Frontend directory not found at $FRONTEND_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Project structure verified${NC}"
echo ""

# Step 2: Build React Frontend
echo -e "${YELLOW}[2/6] Building React frontend for production...${NC}"
cd "$FRONTEND_DIR"

# Clean previous build
if [ -d "build" ]; then
    echo "  Cleaning previous build folder..."
    rm -rf build
fi

# Install dependencies
echo "  Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: npm install failed${NC}"
    exit 1
fi

# Build production
echo "  Running production build..."
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: npm run build failed${NC}"
    exit 1
fi

# Verify build output
if [ ! -d "build" ]; then
    echo -e "${RED}ERROR: Build folder not created${NC}"
    exit 1
fi

BUILD_SIZE=$(du -sh build | cut -f1)
echo -e "${GREEN}✓ React build completed successfully (Size: $BUILD_SIZE)${NC}"

# Return to project root
cd - > /dev/null
echo ""

# Step 3: Collect Django Static Files
echo -e "${YELLOW}[3/6] Collecting Django static files...${NC}"
cd "$BACKEND_DIR"

# Clean previous staticfiles
if [ -d "staticfiles" ]; then
    echo "  Cleaning previous staticfiles folder..."
    rm -rf staticfiles
fi

# Collect static files
echo "  Running collectstatic..."
python manage.py collectstatic --noinput --clear
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: collectstatic failed${NC}"
    exit 1
fi

# Verify staticfiles output
if [ ! -d "staticfiles" ]; then
    echo -e "${RED}ERROR: staticfiles folder not created${NC}"
    exit 1
fi

STATIC_SIZE=$(du -sh staticfiles | cut -f1)
echo -e "${GREEN}✓ Static files collected successfully (Size: $STATIC_SIZE)${NC}"

# Return to project root
cd - > /dev/null
echo ""

# Step 4: Package Media Files
echo -e "${YELLOW}[4/6] Packaging media files...${NC}"
MEDIA_PATH="$BACKEND_DIR/media"
if [ -d "$MEDIA_PATH" ]; then
    # Remove previous media.zip
    if [ -f "$MEDIA_OUTPUT" ]; then
        echo "  Removing previous media.zip..."
        rm "$MEDIA_OUTPUT"
    fi
    
    # Create zip file
    echo "  Creating media.zip..."
    cd "$BACKEND_DIR"
    zip -r "../media.zip" media/ > /dev/null 2>&1
    cd - > /dev/null
    
    # Verify zip file
    if [ -f "$MEDIA_OUTPUT" ]; then
        ZIP_SIZE=$(du -sh "$MEDIA_OUTPUT" | cut -f1)
        echo -e "${GREEN}✓ Media files packaged successfully (Size: $ZIP_SIZE)${NC}"
    else
        echo -e "${RED}ERROR: Failed to create media.zip${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}WARNING: Media directory not found at $MEDIA_PATH${NC}"
    echo "  Creating empty media.zip for structure..."
    zip -r "$MEDIA_OUTPUT" . -x "*.git*" > /dev/null 2>&1
fi
echo ""

# Step 5: Verify Deployment Files
echo -e "${YELLOW}[5/6] Verifying deployment files...${NC}"

ALL_FILES_PRESENT=true

if [ -d "$BUILD_OUTPUT" ]; then
    echo -e "${GREEN}  ✓ React build folder found${NC}"
else
    echo -e "${RED}  ✗ React build folder NOT found${NC}"
    ALL_FILES_PRESENT=false
fi

if [ -f "$MEDIA_OUTPUT" ]; then
    echo -e "${GREEN}  ✓ Media ZIP file found${NC}"
else
    echo -e "${RED}  ✗ Media ZIP file NOT found${NC}"
    ALL_FILES_PRESENT=false
fi

if [ -d "$STATICFILES_OUTPUT" ]; then
    echo -e "${GREEN}  ✓ Django staticfiles found${NC}"
else
    echo -e "${RED}  ✗ Django staticfiles NOT found${NC}"
    ALL_FILES_PRESENT=false
fi

if [ "$ALL_FILES_PRESENT" = false ]; then
    echo -e "${RED}ERROR: Some deployment files are missing${NC}"
    exit 1
fi
echo ""

# Step 6: Summary and Next Steps
echo -e "${GREEN}[6/6] Deployment preparation complete!${NC}"
echo ""
echo -e "${CYAN}========================================"
echo "DEPLOYMENT SUMMARY"
echo "========================================${NC}"
echo ""
echo -e "${GREEN}✓ React build folder: $BUILD_OUTPUT${NC}"
echo -e "${GREEN}✓ Media ZIP file: $MEDIA_OUTPUT${NC}"
echo -e "${GREEN}✓ Django staticfiles: $BACKEND_DIR/staticfiles${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo "1. Push changes to GitHub:"
echo "   git add ."
echo "   git commit -m 'Production build ready for deployment'"
echo "   git push origin main"
echo ""
echo "2. Restart Render deployment (it will auto-build)"
echo ""
echo "3. Download and upload to Hostinger:"
echo "   - Download: $BUILD_OUTPUT"
echo "   - Upload to: /public_html/ on Hostinger"
echo ""
echo "4. Upload media files to Hostinger:"
echo "   - Download: $MEDIA_OUTPUT"
echo "   - Extract and upload to: /public_html/media/ on Hostinger"
echo ""
echo "5. Verify deployment:"
echo "   - Frontend: https://amanisafi.com"
echo "   - Backend API: https://atm-maintenance.onrender.com/api"
echo ""
echo -e "${CYAN}========================================${NC}"

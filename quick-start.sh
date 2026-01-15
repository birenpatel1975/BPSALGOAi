#!/bin/bash

# Quick Start Script for BPSALGOAi Android Development
# This script verifies the development environment and builds the app

set -e

echo "=========================================="
echo "BPSALGOAi Android Development Quick Start"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo "ℹ $1"
}

# Check Java
echo "Checking Java installation..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}')
    print_success "Java found: $JAVA_VERSION"
else
    print_error "Java not found. Please install JDK 11 or higher."
    exit 1
fi

# Check Android SDK
echo ""
echo "Checking Android SDK..."
if [ -n "$ANDROID_HOME" ] || [ -n "$ANDROID_SDK_ROOT" ]; then
    SDK_PATH="${ANDROID_HOME:-$ANDROID_SDK_ROOT}"
    print_success "Android SDK found at: $SDK_PATH"
else
    print_warning "ANDROID_HOME or ANDROID_SDK_ROOT not set."
    print_info "The build may fail if Android SDK is not properly configured."
fi

# Make gradlew executable
echo ""
echo "Setting up Gradle wrapper..."
chmod +x gradlew
print_success "Gradle wrapper is now executable"

# Check Gradle wrapper
echo ""
echo "Checking Gradle wrapper..."
if ./gradlew --version > /dev/null 2>&1; then
    print_success "Gradle wrapper is working"
else
    print_error "Gradle wrapper check failed"
    exit 1
fi

# Clean build
echo ""
echo "Cleaning previous builds..."
./gradlew clean
print_success "Clean completed"

# Build debug APK
echo ""
echo "Building debug APK..."
if ./gradlew assembleDebug; then
    print_success "Debug APK built successfully"
    print_info "Location: app/build/outputs/apk/debug/app-debug.apk"
    
    # Check APK size
    if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
        APK_SIZE=$(du -h app/build/outputs/apk/debug/app-debug.apk | cut -f1)
        print_info "APK Size: $APK_SIZE"
    fi
else
    print_error "Debug APK build failed"
    exit 1
fi

# Offer to install on device
echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo ""
print_info "Next steps:"
echo "  1. To install on device: adb install -r app/build/outputs/apk/debug/app-debug.apk"
echo "  2. To build release APK: ./gradlew assembleRelease"
echo "  3. To build AAB bundle: ./gradlew bundleRelease"
echo "  4. For full deployment guide: see ANDROID_DEPLOYMENT.md"
echo ""

# Check if ADB is available and devices are connected
if command -v adb &> /dev/null; then
    DEVICES=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l)
    if [ "$DEVICES" -gt 0 ]; then
        echo ""
        print_info "Found $DEVICES connected device(s)"
        read -p "Install APK on device now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            adb install -r app/build/outputs/apk/debug/app-debug.apk
            print_success "APK installed successfully"
            print_info "Launch the app from your device or run:"
            echo "  adb shell am start -n com.bpsalgoai.trading/.MainActivity"
        fi
    fi
fi

echo ""
print_success "Quick start complete!"

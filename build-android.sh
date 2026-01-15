#!/bin/bash

# Build script for BPSALGOAi Android Application
# This script builds the Android APK/AAB for deployment

set -e

echo "Building BPSALGOAi Android Application..."

# Clean previous builds
echo "Cleaning previous builds..."
./gradlew clean

# Build debug APK
echo "Building debug APK..."
./gradlew assembleDebug

# Build release APK
echo "Building release APK..."
./gradlew assembleRelease

# Build release AAB (Android App Bundle)
echo "Building release AAB..."
./gradlew bundleRelease

echo "Build completed successfully!"
echo ""
echo "Build artifacts:"
echo "- Debug APK: app/build/outputs/apk/debug/app-debug.apk"
echo "- Release APK: app/build/outputs/apk/release/app-release.apk"
echo "- Release AAB: app/build/outputs/bundle/release/app-release.aab"

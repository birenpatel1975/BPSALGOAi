# Android Deployment Guide for BPSALGOAi

This guide provides instructions for building and deploying the BPSALGOAi Android application.

## Prerequisites

- **Java Development Kit (JDK)**: Version 11 or higher
- **Android SDK**: API Level 34 (Android 14)
- **Gradle**: Version 8.2 (included via wrapper)

## Project Structure

```
BPSALGOAi/
├── app/
│   ├── build.gradle                 # App-level build configuration
│   ├── proguard-rules.pro           # ProGuard rules for code obfuscation
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml  # App manifest
│           ├── java/                # Kotlin source files
│           └── res/                 # Resources (layouts, strings, etc.)
├── build.gradle                     # Project-level build configuration
├── settings.gradle                  # Project settings
├── gradle.properties                # Gradle properties
└── build-android.sh                 # Build script
```

## Building the Application

### Option 1: Using the Build Script (Recommended)

```bash
./build-android.sh
```

This script will:
1. Clean previous builds
2. Build debug APK
3. Build release APK
4. Build release AAB (Android App Bundle)

### Option 2: Using Gradle Directly

#### Build Debug APK
```bash
./gradlew assembleDebug
```
Output: `app/build/outputs/apk/debug/app-debug.apk`

#### Build Release APK
```bash
./gradlew assembleRelease
```
Output: `app/build/outputs/apk/release/app-release.apk`

#### Build Release AAB (for Google Play)
```bash
./gradlew bundleRelease
```
Output: `app/build/outputs/bundle/release/app-release.aab`

## Signing Configuration

### For Production Release

1. **Create a keystore** (if you don't have one):
```bash
keytool -genkey -v -keystore bpsalgoai-release.keystore -alias bpsalgoai -keyalg RSA -keysize 2048 -validity 10000
```

2. **Update app/build.gradle** to add signing configuration:
```gradle
android {
    signingConfigs {
        release {
            storeFile file('path/to/bpsalgoai-release.keystore')
            storePassword 'your-store-password'
            keyAlias 'bpsalgoai'
            keyPassword 'your-key-password'
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

3. **Store credentials securely**: Use environment variables or a secure keystore properties file.

## Deployment Options

### 1. Google Play Store

1. Build the AAB file:
   ```bash
   ./gradlew bundleRelease
   ```

2. Sign in to [Google Play Console](https://play.google.com/console)

3. Create a new app or select existing app

4. Upload the AAB file: `app/build/outputs/bundle/release/app-release.aab`

5. Complete the store listing and submit for review

### 2. Direct APK Distribution

1. Build the signed release APK:
   ```bash
   ./gradlew assembleRelease
   ```

2. Distribute the APK: `app/build/outputs/apk/release/app-release.apk`

3. Users must enable "Install from Unknown Sources" in Android settings

### 3. Internal Testing

Use the debug APK for internal testing:
```bash
./gradlew assembleDebug
```

Install on device:
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Build Variants

- **Debug**: Includes debugging symbols, no obfuscation
- **Release**: Optimized, obfuscated with ProGuard, ready for production

## Version Management

Update version in `app/build.gradle`:
```gradle
defaultConfig {
    versionCode 1      // Increment for each release
    versionName "1.0.0" // Semantic version
}
```

## ProGuard Configuration

ProGuard rules are defined in `app/proguard-rules.pro`. The current configuration:
- Preserves app classes
- Keeps Kotlin metadata
- Preserves AndroidX components
- Maintains line numbers for stack traces

## Minimum Requirements

- **Minimum SDK**: Android 7.0 (API 24)
- **Target SDK**: Android 14 (API 34)
- **Compile SDK**: Android 14 (API 34)

## Permissions

The app requests the following permissions:
- `INTERNET`: For network communication
- `ACCESS_NETWORK_STATE`: To check network connectivity

## Troubleshooting

### Build Fails

1. Clean the build:
   ```bash
   ./gradlew clean
   ```

2. Invalidate caches (if using Android Studio):
   File → Invalidate Caches / Restart

3. Check Java version:
   ```bash
   java -version
   ```

### Signing Issues

- Ensure keystore path is correct
- Verify passwords are correct
- Check keystore alias matches

### APK Size Optimization

The release build includes:
- ProGuard code shrinking
- Resource shrinking
- APK optimization

Expected APK size: ~5-10 MB

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/android-build.yml`:
```yaml
name: Android Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
    - name: Build with Gradle
      run: ./gradlew assembleRelease
    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: app-release
        path: app/build/outputs/apk/release/app-release.apk
```

## Support

For issues or questions, please contact the development team or create an issue in the repository.

## License

This project is proprietary software for NSE F&O AI Trading.

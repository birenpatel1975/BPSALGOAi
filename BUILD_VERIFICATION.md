# Build Verification and Testing Guide

This document provides instructions for verifying the Android build setup.

## Prerequisites Verification

### 1. Check Java Installation

```bash
java -version
```

Expected output: Java 11 or higher (Java 17 recommended)

### 2. Check Android SDK

```bash
echo $ANDROID_HOME
# or
echo $ANDROID_SDK_ROOT
```

The path should point to your Android SDK installation.

### 3. Verify SDK Components

```bash
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --list | grep "platforms;android-34"
```

Should show Android API 34 installed.

## Build Verification Steps

### 1. Clean Build

```bash
./gradlew clean
```

This should complete without errors.

### 2. Check Dependencies

```bash
./gradlew dependencies
```

This will download all required dependencies and display the dependency tree.

### 3. Build Debug APK

```bash
./gradlew assembleDebug
```

Expected output location: `app/build/outputs/apk/debug/app-debug.apk`

Verify the APK was created:
```bash
ls -lh app/build/outputs/apk/debug/app-debug.apk
```

### 4. Build Release APK

```bash
./gradlew assembleRelease
```

Expected output location: `app/build/outputs/apk/release/app-release.apk`

### 5. Build Android App Bundle (AAB)

```bash
./gradlew bundleRelease
```

Expected output location: `app/build/outputs/bundle/release/app-release.aab`

### 6. Verify APK Contents

```bash
unzip -l app/build/outputs/apk/debug/app-debug.apk
```

Should show:
- AndroidManifest.xml
- classes.dex
- resources.arsc
- res/ directory
- META-INF/ directory

### 7. Install on Device/Emulator

Connect a device or start an emulator, then:

```bash
adb devices
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Launch the app:
```bash
adb shell am start -n com.bpsalgoai.trading/.MainActivity
```

## Automated Testing

### Run Unit Tests

```bash
./gradlew test
```

Test reports will be generated in: `app/build/reports/tests/testDebugUnitTest/index.html`

### Run Instrumented Tests (requires device/emulator)

```bash
./gradlew connectedAndroidTest
```

## CI/CD Verification

The repository includes a GitHub Actions workflow (`.github/workflows/android-build.yml`) that:

1. Builds debug APK
2. Builds release APK
3. Builds release AAB
4. Runs unit tests
5. Uploads artifacts

To verify CI/CD:
1. Push to main or develop branch
2. Check Actions tab in GitHub
3. Download build artifacts from completed workflow

## Common Issues and Solutions

### Issue: Gradle daemon fails to start

**Solution:**
```bash
./gradlew --stop
./gradlew clean --no-daemon
```

### Issue: SDK not found

**Solution:**
Create or update `local.properties`:
```properties
sdk.dir=/path/to/android/sdk
```

### Issue: Build fails with "Could not resolve dependencies"

**Solution:**
1. Check internet connection
2. Clear Gradle cache:
```bash
rm -rf ~/.gradle/caches/
./gradlew clean build --refresh-dependencies
```

### Issue: APK size too large

**Solution:**
1. Ensure ProGuard is enabled (already configured in release builds)
2. Check for unnecessary resources
3. Use APK Analyzer:
```bash
$ANDROID_HOME/tools/bin/apkanalyzer apk summary app/build/outputs/apk/release/app-release.apk
```

## Build Performance Tips

### Enable Gradle Daemon

Already enabled in `gradle.properties`

### Use Build Cache

```bash
./gradlew assembleDebug --build-cache
```

### Parallel Builds

Already enabled in `gradle.properties` with:
```properties
org.gradle.parallel=true
```

## APK Signing Verification

### Verify Debug Signature

```bash
jarsigner -verify -verbose -certs app/build/outputs/apk/debug/app-debug.apk
```

### Verify Release Signature (after proper signing)

```bash
jarsigner -verify -verbose -certs app/build/outputs/apk/release/app-release.apk
```

## Security Checks

### Check for Hardcoded Secrets

```bash
grep -r "password\|secret\|api_key" app/src/ --exclude-dir=build
```

Should return no results with actual secrets.

### Verify ProGuard Rules

```bash
cat app/proguard-rules.pro
```

Ensure sensitive code is properly obfuscated in release builds.

## Performance Testing

### Measure Build Time

```bash
./gradlew clean
time ./gradlew assembleDebug
```

### APK Size Check

```bash
du -h app/build/outputs/apk/debug/app-debug.apk
du -h app/build/outputs/apk/release/app-release.apk
```

Release APK should be significantly smaller than debug due to ProGuard optimization.

## Deployment Readiness Checklist

- [ ] All builds complete successfully
- [ ] APK installs on test device
- [ ] App launches without crashes
- [ ] No hardcoded secrets in code
- [ ] ProGuard rules are properly configured
- [ ] Version code and version name are updated
- [ ] Signing configuration is set up for production
- [ ] CI/CD pipeline runs successfully
- [ ] APK size is optimized
- [ ] All unit tests pass

## Next Steps

Once all verification steps pass:

1. Set up production signing (see ANDROID_DEPLOYMENT.md)
2. Test on multiple devices/Android versions
3. Prepare store listing for Google Play
4. Submit for review

## Support

For build issues, check:
- Gradle logs: `build/outputs/logs/`
- Android Studio build output
- GitHub Actions logs (for CI/CD issues)

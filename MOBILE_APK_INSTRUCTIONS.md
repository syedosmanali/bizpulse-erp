# 📱 BizPulse Mobile APK Build Instructions

## ✅ What's Already Done:

1. ✅ Capacitor config updated to point to `/mobile` route
2. ✅ Splash screen color changed to match mobile theme (#732C3F)
3. ✅ Android Studio opened in `android/` folder

## 🚀 How to Build APK:

### Option 1: Using Android Studio (RECOMMENDED)

1. **Wait for Gradle Sync** (bottom right corner - wait for it to finish)

2. **Build APK:**
   - Click: `Build` → `Build Bundle(s) / APK(s)` → `Build APK(s)`
   - OR press: `Ctrl + Shift + A` and type "Build APK"

3. **Find Your APK:**
   - Location: `android\app\build\outputs\apk\debug\app-debug.apk`
   - Android Studio will show a notification with "locate" link

4. **Install on Phone:**
   - Copy APK to phone
   - Enable "Install from Unknown Sources"
   - Install and run!

### Option 2: Using Command Line

```cmd
cd android
gradlew assembleDebug
```

APK will be at: `android\app\build\outputs\apk\debug\app-debug.apk`

### Option 3: Build Release APK (Signed)

```cmd
cd android
gradlew assembleRelease
```

APK will be at: `android\app\build\outputs\apk\release\app-release.apk`

## 📋 What the App Will Do:

- ✅ Opens to your mobile ERP interface (`/mobile` route)
- ✅ Shows login screen
- ✅ All your existing mobile modules work:
  - Dashboard
  - Billing
  - Products
  - Customers
  - Sales
  - Inventory
  - Credit
  - Reports
- ✅ Barcode scanning (using web camera)
- ✅ Offline support (if configured)

## 🔧 Troubleshooting:

### If Gradle Sync Fails:
1. Click "File" → "Sync Project with Gradle Files"
2. Or run: `gradlew clean build`

### If Build Fails:
1. Check Java version: `java -version` (should be Java 17)
2. Update Gradle: Click notification to update
3. Clean build: `gradlew clean`

### If APK Doesn't Install:
1. Enable "Install from Unknown Sources" in phone settings
2. Check if old version is installed - uninstall first
3. Make sure APK is not corrupted

## 📱 Testing the App:

1. **Make sure your Flask server is running:**
   ```cmd
   python app.py
   ```

2. **Make sure it's accessible:**
   - Server should be at: `https://bizpulse24.com`
   - Or use ngrok for local testing

3. **Install APK and test:**
   - Login with your credentials
   - Test all modules
   - Check if data loads correctly

## 🎯 Current Configuration:

- **App Name:** BizPulse ERP
- **Package:** com.bizpulse.retail
- **Server URL:** https://bizpulse24.com/mobile
- **Splash Color:** #732C3F (Wine color matching your theme)

## 🔥 Quick Build Command:

Just run this batch file:
```cmd
BUILD_MOBILE_APK.bat
```

It will:
1. Sync Capacitor
2. Open Android Studio
3. Show you next steps

---

**Bro, tera mobile app already ready hai! Bas APK build kar aur install kar! 🚀**

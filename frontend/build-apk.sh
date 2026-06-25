#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Build Vue (prod) ==="
VITE_API_BASE=https://melicheap.onrender.com npm run build

echo "=== Sync Capacitor ==="
npx cap sync

echo "=== Patch Java 21 -> 17 ==="
sed -i 's/VERSION_21/VERSION_17/g' node_modules/@capacitor/android/capacitor/build.gradle
sed -i 's/VERSION_21/VERSION_17/g' android/app/capacitor.build.gradle
sed -i 's/VERSION_21/VERSION_17/g' android/capacitor-cordova-android-plugins/build.gradle

echo "=== Build APK ==="
cd android
ANDROID_HOME=/home/fran/Android/Sdk \
JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64 \
./gradlew assembleDebug

echo "=== APK listo ==="
find android -name "*.apk"

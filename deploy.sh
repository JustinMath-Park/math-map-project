#!/bin/bash

# Stop on error
set -e

# 1. Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js가 설치되어 있지 않습니다."
    echo "👉 https://nodejs.org/ 에서 Node.js를 먼저 설치해주세요."
    exit 1
fi

# 2. Determine Firebase Command
# Try to use global firebase if available, otherwise use npx
if command -v firebase &> /dev/null; then
    FIREBASE_CMD="firebase"
    echo "✅ Global Firebase CLI detected."
else
    echo "📦 Using npx to run Firebase CLI (no global install needed)..."
    FIREBASE_CMD="npx -y firebase-tools"
fi

# 3. Login check
echo "🔑 Firebase 로그인 확인 중..."
$FIREBASE_CMD login --reauth

# 4. Deploy Adaptive Test -> mathiter-level-test
echo "🚀 Adaptive Test (mathiter-level-test) 배포 중..."
$FIREBASE_CMD target:apply hosting adaptive-test mathiter-level-test
$FIREBASE_CMD deploy --only hosting:adaptive-test

# 5. Deploy Curriculum Navigator -> mathiter-curriculum
echo "🚀 Curriculum Navigator (mathiter-curriculum) 배포 중..."
$FIREBASE_CMD deploy --only hosting:curriculum-navigator

echo "✨ 모든 배포가 완료되었습니다!"

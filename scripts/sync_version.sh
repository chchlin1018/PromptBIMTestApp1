#!/usr/bin/env bash
# sync_version.sh — Update version number across all project files at once.
# Usage: ./scripts/sync_version.sh 2.11.0
set -euo pipefail

NEW_VERSION="${1:?Usage: $0 <version>}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 Syncing version to ${NEW_VERSION} across all project files..."

# 1. pyproject.toml
sed -i '' "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" "$PROJECT_ROOT/pyproject.toml"
echo "  ✅ pyproject.toml"

# 2. __init__.py fallback
sed -i '' "s/__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" \
    "$PROJECT_ROOT/src/promptbim/__init__.py"
echo "  ✅ __init__.py"

# 3. Info.plist — CFBundleShortVersionString
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString ${NEW_VERSION}" \
    "$PROJECT_ROOT/PromptBIMTestApp1/Info.plist" 2>/dev/null || \
    sed -i '' "s/<string>2\.[0-9]*\.[0-9]*<\/string>/<string>${NEW_VERSION}<\/string>/" \
    "$PROJECT_ROOT/PromptBIMTestApp1/Info.plist"
echo "  ✅ Info.plist"

# 4. CMakeLists.txt (if version is set there)
if grep -q "project(promptbim VERSION" "$PROJECT_ROOT/libpromptbim/CMakeLists.txt" 2>/dev/null; then
    sed -i '' "s/project(promptbim VERSION [0-9.]*/project(promptbim VERSION ${NEW_VERSION}/" \
        "$PROJECT_ROOT/libpromptbim/CMakeLists.txt"
    echo "  ✅ CMakeLists.txt"
fi

# 5. Increment CFBundleVersion (build number)
PLIST="$PROJECT_ROOT/PromptBIMTestApp1/Info.plist"
CURRENT_BUILD=$(/usr/libexec/PlistBuddy -c "Print :CFBundleVersion" "$PLIST" 2>/dev/null || echo "24")
NEW_BUILD=$((CURRENT_BUILD + 1))
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion ${NEW_BUILD}" "$PLIST" 2>/dev/null || true
echo "  ✅ Build number: ${CURRENT_BUILD} → ${NEW_BUILD}"

echo ""
echo "✅ Version synced to ${NEW_VERSION} (build ${NEW_BUILD})"
echo "   Files updated: pyproject.toml, __init__.py, Info.plist, CMakeLists.txt"

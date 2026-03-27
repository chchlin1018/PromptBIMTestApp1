pragma Singleton
import QtQuick

QtObject {
    id: theme

    property bool isDark: true

    // Background colors
    readonly property color bgPrimary: isDark ? "#1a1a2e" : "#f5f5f5"
    readonly property color bgSecondary: isDark ? "#16213e" : "#ffffff"
    readonly property color bgTertiary: isDark ? "#0d1117" : "#e8e8e8"
    readonly property color bgInput: isDark ? "#0a1628" : "#ffffff"
    readonly property color bgCard: isDark ? "#0a1628" : "#f0f0f0"
    readonly property color bgCardHover: isDark ? "#1a3a5c" : "#e0e8f0"

    // Text colors
    readonly property color textPrimary: isDark ? "#ffffff" : "#1a1a2e"
    readonly property color textSecondary: isDark ? "#8892b0" : "#666666"
    readonly property color textMuted: isDark ? "#555555" : "#999999"

    // Accent colors (same in both themes)
    readonly property color accent: "#4a9eff"
    readonly property color accentGreen: "#4ade80"
    readonly property color accentYellow: "#f59e0b"
    readonly property color accentRed: "#ef4444"

    // Border
    readonly property color border: isDark ? "#333333" : "#cccccc"
    readonly property color borderFocus: accent

    // 3D viewport
    readonly property color viewport: isDark ? "#1a1a2e" : "#dde4ec"
    readonly property color ground: isDark ? "#2a2a3e" : "#cccccc"

    function toggle() {
        isDark = !isDark
    }
}

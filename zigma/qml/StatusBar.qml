import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: ThemeManager.bgTertiary

    property var agentBridge: null

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 16

        // AI Status indicator
        Row {
            spacing: 6
            Rectangle {
                width: 8; height: 8; radius: 4
                anchors.verticalCenter: parent.verticalCenter
                color: {
                    if (!agentBridge) return "#666"
                    if (agentBridge.reconnecting) return "#f59e0b"
                    if (agentBridge.busy) return "#f59e0b"
                    if (agentBridge.connected) return "#4ade80"
                    return "#ef4444"
                }
                SequentialAnimation on opacity {
                    running: agentBridge && agentBridge.reconnecting
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.3; duration: 500 }
                    NumberAnimation { to: 1.0; duration: 500 }
                }
            }
            Label {
                text: {
                    if (!agentBridge) return "No Agent"
                    if (agentBridge.reconnecting) return "Reconnecting..."
                    if (agentBridge.busy) return "Busy"
                    if (agentBridge.connected) return "Connected"
                    return "Disconnected"
                }
                color: ThemeManager.textSecondary
                font.pixelSize: 11
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Progress
        ProgressBar {
            id: progressBar
            Layout.fillWidth: true
            Layout.maximumWidth: 200
            value: 0
            visible: agentBridge && agentBridge.busy

            background: Rectangle { color: ThemeManager.bgPrimary; radius: 3 }
            contentItem: Rectangle {
                width: progressBar.visualPosition * progressBar.width
                height: progressBar.height
                radius: 3
                color: "#4a9eff"
            }
        }

        Label {
            id: statusText
            Layout.fillWidth: true
            text: "Ready"
            color: ThemeManager.textSecondary
            font.pixelSize: 11
            elide: Text.ElideRight
        }

        Label {
            text: "Zigma v0.1.0"
            color: ThemeManager.textMuted
            font.pixelSize: 11
        }
    }

    Connections {
        target: agentBridge
        function onStatusUpdate(message, progress) {
            statusText.text = message
            progressBar.value = progress
        }
        function onResultReady() {
            statusText.text = "Ready"
            progressBar.value = 0
        }
        function onErrorOccurred(error) {
            statusText.text = "Error: " + error
        }
    }
}

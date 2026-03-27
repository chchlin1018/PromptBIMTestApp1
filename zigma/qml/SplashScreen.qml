import QtQuick
import QtQuick.Controls

Rectangle {
    id: splash
    color: "#0d1117"
    z: 200

    signal finished()

    SequentialAnimation {
        id: splashAnim
        running: true

        PauseAnimation { duration: 300 }
        NumberAnimation { target: logoText; property: "opacity"; from: 0; to: 1; duration: 600 }
        PauseAnimation { duration: 200 }
        NumberAnimation { target: subtitleText; property: "opacity"; from: 0; to: 1; duration: 400 }
        PauseAnimation { duration: 200 }
        NumberAnimation { target: loadingBar; property: "width"; from: 0; to: 200; duration: 800; easing.type: Easing.InOutQuad }
        PauseAnimation { duration: 400 }
        NumberAnimation { target: splash; property: "opacity"; from: 1; to: 0; duration: 400 }

        onFinished: {
            splash.visible = false
            splash.finished()
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: 16

        Text {
            id: logoText
            text: "⬡ Zigma"
            color: "#4a9eff"
            font.pixelSize: 42
            font.bold: true
            opacity: 0
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            id: subtitleText
            text: "PromptToBuild"
            color: "#8892b0"
            font.pixelSize: 16
            opacity: 0
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Item {
            width: 200; height: 3
            anchors.horizontalCenter: parent.horizontalCenter

            Rectangle {
                anchors.bottom: parent.bottom
                height: 3
                width: 200
                color: "#1a1a2e"
                radius: 2
            }
            Rectangle {
                id: loadingBar
                anchors.bottom: parent.bottom
                height: 3
                width: 0
                color: "#4a9eff"
                radius: 2
            }
        }

        Text {
            text: "v0.1.0"
            color: "#555"
            font.pixelSize: 11
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}

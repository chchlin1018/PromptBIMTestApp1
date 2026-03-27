import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: Qt.rgba(0, 0, 0, 0.6)
    visible: false
    z: 100

    property string statusText: "Generating..."

    function show(text) {
        statusText = text || "Generating..."
        visible = true
        spinAnim.running = true
    }
    function hide() {
        visible = false
        spinAnim.running = false
    }

    MouseArea { anchors.fill: parent } // block clicks

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 16

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 48; height: 48; radius: 24
            color: "transparent"
            border.color: "#4a9eff"
            border.width: 3

            Rectangle {
                width: 12; height: 12; radius: 6
                color: "#4a9eff"
                x: 18; y: -2
            }

            RotationAnimation on rotation {
                id: spinAnim
                from: 0; to: 360
                duration: 1000
                loops: Animation.Infinite
                running: false
            }
        }

        Label {
            Layout.alignment: Qt.AlignHCenter
            text: root.statusText
            color: "white"
            font.pixelSize: 14
        }

        Label {
            Layout.alignment: Qt.AlignHCenter
            text: "AI is working on your design..."
            color: "#8892b0"
            font.pixelSize: 11
        }
    }
}

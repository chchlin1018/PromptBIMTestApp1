import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    title: "Zigma PromptToBuild"
    width: 1280
    height: 800
    visible: true

    color: "#1a1a2e"

    Text {
        anchors.centerIn: parent
        text: "Zigma PromptToBuild v0.1.0"
        color: "white"
        font.pixelSize: 24
    }
}

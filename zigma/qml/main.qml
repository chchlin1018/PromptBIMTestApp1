import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Zigma

ApplicationWindow {
    id: root
    title: "Zigma PromptToBuild"
    width: 1280
    height: 800
    visible: true
    color: "#1a1a2e"

    AgentBridge { id: agentBridge }
    BIMSceneBuilder { id: sceneBuilder }
    BIMMaterialLibrary { id: materialLibrary }

    menuBar: MenuBar {
        Menu {
            title: "File"
            Action { text: "New Scene"; shortcut: "Ctrl+N" }
            MenuSeparator {}
            Action { text: "Quit"; shortcut: "Ctrl+Q"; onTriggered: Qt.quit() }
        }
        Menu {
            title: "View"
            Action { text: "Perspective"; shortcut: "1"; onTriggered: bimView.setView(0) }
            Action { text: "Top"; shortcut: "2"; onTriggered: bimView.setView(1) }
            Action { text: "Front"; shortcut: "3"; onTriggered: bimView.setView(2) }
            Action { text: "Right"; shortcut: "4"; onTriggered: bimView.setView(3) }
        }
        Menu {
            title: "Help"
            Action { text: "About"; onTriggered: aboutDialog.open() }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal

            ChatPanel {
                id: chatPanel
                SplitView.preferredWidth: 300
                SplitView.minimumWidth: 200
                agentBridge: agentBridge
            }

            BIMView3D {
                id: bimView
                SplitView.fillWidth: true
                SplitView.minimumWidth: 400
                sceneBuilder: sceneBuilder
                materialLibrary: materialLibrary
                onElementPicked: function(elemId, elemData) {
                    propertyPanel.showElement(elemId, elemData)
                }
            }

            PropertyPanel {
                id: propertyPanel
                SplitView.preferredWidth: 280
                SplitView.minimumWidth: 200
            }
        }

        StatusBar {
            id: statusBar
            Layout.fillWidth: true
            Layout.preferredHeight: 32
            agentBridge: agentBridge
        }
    }

    // Connect AgentBridge signals
    Connections {
        target: agentBridge
        function onResultReady(result) {
            if (result.model) {
                sceneBuilder.buildScene(result.model)
                bimView.fitToScene()
            }
            chatPanel.addMessage("ai", "Generation complete!")
        }
        function onDeltaReady(delta) {
            if (delta.model) {
                sceneBuilder.buildScene(delta.model)
            }
            chatPanel.addMessage("ai", "Modification applied.")
        }
        function onStatusUpdate(message, progress) {
            chatPanel.addMessage("ai", message)
        }
        function onErrorOccurred(error) {
            chatPanel.addMessage("system", "Error: " + error)
        }
    }

    Dialog {
        id: aboutDialog
        title: "About Zigma"
        modal: true
        anchors.centerIn: parent
        standardButtons: Dialog.Ok
        Label {
            text: "Zigma PromptToBuild v0.1.0\nBIM generation powered by AI"
            color: "white"
        }
    }
}

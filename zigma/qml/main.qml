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

            // Left panel with Chat + ScenePicker tabs
            Rectangle {
                SplitView.preferredWidth: 300
                SplitView.minimumWidth: 200
                color: "#16213e"

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    TabBar {
                        id: leftTabBar
                        Layout.fillWidth: true
                        background: Rectangle { color: "#0d1117" }

                        TabButton {
                            text: "Chat"
                            contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: leftTabBar.currentIndex === 0 ? "#16213e" : "#0d1117" }
                        }
                        TabButton {
                            text: "Scenes"
                            contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: leftTabBar.currentIndex === 1 ? "#16213e" : "#0d1117" }
                        }
                        TabButton {
                            text: "Assets"
                            contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: leftTabBar.currentIndex === 2 ? "#16213e" : "#0d1117" }
                        }
                    }

                    StackLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: leftTabBar.currentIndex

                        ChatPanel {
                            id: chatPanel
                            agentBridge: agentBridge
                        }
                        ScenePicker {
                            id: scenePicker
                            onSceneSelected: function(sceneId, prompt, landData) {
                                chatPanel.addMessage("user", prompt)
                                if (agentBridge) agentBridge.generate(prompt, landData)
                                leftTabBar.currentIndex = 0
                            }
                        }
                        AssetBrowser {
                            id: assetBrowser
                            onAssetSelected: function(assetId, category, name) {
                                chatPanel.addMessage("system", "Selected: " + name)
                            }
                        }
                    }
                }
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

            // Right panel with tabs
            Rectangle {
                SplitView.preferredWidth: 300
                SplitView.minimumWidth: 220
                color: "#16213e"

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    TabBar {
                        id: rightTabBar
                        Layout.fillWidth: true
                        background: Rectangle { color: "#0d1117" }

                        TabButton {
                            text: "Properties"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 0 ? "#16213e" : "#0d1117" }
                        }
                        TabButton {
                            text: "Cost"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 1 ? "#16213e" : "#0d1117" }
                        }
                        TabButton {
                            text: "Delta"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 2 ? "#16213e" : "#0d1117" }
                        }
                        TabButton {
                            text: "Schedule"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 3 ? "#16213e" : "#0d1117" }
                        }
                    }

                    StackLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: rightTabBar.currentIndex

                        PropertyPanel {
                            id: propertyPanel
                        }
                        CostPanel {
                            id: costPanel
                        }
                        DeltaPanel {
                            id: deltaPanel
                            onUndoRequested: {
                                if (agentBridge) agentBridge.modify("undo")
                            }
                        }
                        SchedulePanel {
                            id: schedulePanel
                        }
                    }
                }
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
            if (result.cost) costPanel.costData = result.cost
            if (result.schedule) schedulePanel.scheduleData = result.schedule
            chatPanel.addMessage("ai", "Generation complete!")
        }
        function onDeltaReady(delta) {
            if (delta.model) {
                sceneBuilder.buildScene(delta.model)
            }
            if (delta.cost) costPanel.costData = delta.cost
            deltaPanel.addDelta(
                delta.modification ? delta.modification.description : "Modification",
                delta.cost ? (delta.cost.total_cost_twd || 0) : 0,
                0, 0
            )
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

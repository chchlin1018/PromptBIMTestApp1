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
    color: ThemeManager.bgPrimary

    AgentBridge { id: agentBridge }
    BIMSceneBuilder { id: sceneBuilder }
    BIMMaterialLibrary { id: materialLibrary }

    // Keyboard shortcuts (Task 59)
    Shortcut { sequence: "F"; onActivated: bimView.fitToScene() }
    Shortcut { sequence: "1"; onActivated: bimView.setView(0) }
    Shortcut { sequence: "2"; onActivated: bimView.setView(1) }
    Shortcut { sequence: "3"; onActivated: bimView.setView(2) }
    Shortcut { sequence: "4"; onActivated: bimView.setView(3) }
    Shortcut { sequence: "T"; onActivated: ThemeManager.toggle() }

    menuBar: MenuBar {
        Menu {
            title: "File"
            Action { text: "New Scene"; shortcut: "Ctrl+N" }
            MenuSeparator {}
            Action { text: "Quit"; shortcut: "Ctrl+Q"; onTriggered: Qt.quit() }
        }
        Menu {
            title: "View"
            Action { text: "Perspective"; onTriggered: bimView.setView(0) }
            Action { text: "Top"; onTriggered: bimView.setView(1) }
            Action { text: "Front"; onTriggered: bimView.setView(2) }
            Action { text: "Right"; onTriggered: bimView.setView(3) }
            MenuSeparator {}
            Action { text: "Fit to View"; onTriggered: bimView.fitToScene() }
            Action { text: "Toggle Theme"; onTriggered: ThemeManager.toggle() }
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
                color: ThemeManager.bgSecondary

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    TabBar {
                        id: leftTabBar
                        Layout.fillWidth: true
                        background: Rectangle { color: ThemeManager.bgTertiary }

                        TabButton {
                            text: "Chat"
                            contentItem: Text { text: parent.text; color: ThemeManager.textPrimary; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: leftTabBar.currentIndex === 0 ? ThemeManager.bgSecondary : ThemeManager.bgTertiary }
                        }
                        TabButton {
                            text: "Scenes"
                            contentItem: Text { text: parent.text; color: ThemeManager.textPrimary; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: leftTabBar.currentIndex === 1 ? ThemeManager.bgSecondary : ThemeManager.bgTertiary }
                        }
                        TabButton {
                            text: "Assets"
                            contentItem: Text { text: parent.text; color: ThemeManager.textPrimary; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: leftTabBar.currentIndex === 2 ? ThemeManager.bgSecondary : ThemeManager.bgTertiary }
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
                color: ThemeManager.bgSecondary

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    TabBar {
                        id: rightTabBar
                        Layout.fillWidth: true
                        background: Rectangle { color: ThemeManager.bgTertiary }

                        TabButton {
                            text: "Properties"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: ThemeManager.textPrimary; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 0 ? ThemeManager.bgSecondary : ThemeManager.bgTertiary }
                        }
                        TabButton {
                            text: "Cost"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: ThemeManager.textPrimary; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 1 ? ThemeManager.bgSecondary : ThemeManager.bgTertiary }
                        }
                        TabButton {
                            text: "Delta"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: ThemeManager.textPrimary; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 2 ? ThemeManager.bgSecondary : ThemeManager.bgTertiary }
                        }
                        TabButton {
                            text: "Schedule"
                            width: implicitWidth
                            contentItem: Text { text: parent.text; color: ThemeManager.textPrimary; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
                            background: Rectangle { color: rightTabBar.currentIndex === 3 ? ThemeManager.bgSecondary : ThemeManager.bgTertiary }
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

    // Loading overlay (Task 57)
    LoadingOverlay {
        id: loadingOverlay
        anchors.fill: parent
    }

    // Splash screen (Task 58)
    SplashScreen {
        id: splashScreen
        anchors.fill: parent
    }

    // Connect AgentBridge signals
    Connections {
        target: agentBridge
        function onResultReady(result) {
            loadingOverlay.hide()
            if (result.model) {
                sceneBuilder.buildScene(result.model)
                bimView.fitToScene()
            }
            if (result.cost) costPanel.costData = result.cost
            if (result.schedule) schedulePanel.scheduleData = result.schedule
            chatPanel.addMessage("ai", "Generation complete!")
        }
        function onDeltaReady(delta) {
            loadingOverlay.hide()
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
            loadingOverlay.show(message)
            chatPanel.addMessage("ai", message)
        }
        function onErrorOccurred(error) {
            loadingOverlay.hide()
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
            color: ThemeManager.textPrimary
        }
    }
}

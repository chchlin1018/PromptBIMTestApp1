import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    property var agentBridge: null

    // Undo/redo operation history (UI-side stack)
    property var operationHistory: []
    property int historyIndex: -1

    function addMessage(role, text) {
        chatModel.append({"role": role, "text": text})
        chatList.positionViewAtEnd()
    }

    function addOperationResult(action, result) {
        var msg = ""
        if (action === "move" && result.success) {
            msg = "Moved entity: " + (result.id || "")
        } else if (action === "rotate" && result.success) {
            msg = "Rotated entity: " + (result.id || "")
        } else if (action === "resize" && result.success) {
            msg = "Resized entity: " + (result.id || "")
        } else if (action === "add" && result.success) {
            msg = "Added entity: " + (result.id || "")
        } else if (action === "delete" && result.success) {
            msg = "Deleted entity: " + (result.id || "")
        } else if (action === "connect" && result.success) {
            msg = "Connected: " + (result.from || "") + " → " + (result.to || "")
        } else if (result.cost_delta) {
            var delta = result.cost_delta.total_delta_ntd || 0
            if (delta !== 0) {
                var sign = delta > 0 ? "+" : ""
                msg += "\nCost delta: " + sign + "NT$" + Math.abs(Math.round(delta)).toLocaleString()
            }
        }

        if (msg) {
            addMessage("ai", msg)
            // Push to operation history for undo
            operationHistory.push({action: action, result: result, timestamp: Date.now()})
            historyIndex = operationHistory.length - 1
        }
    }

    function undo() {
        if (historyIndex < 0) return
        var op = operationHistory[historyIndex]
        addMessage("system", "Undo: " + op.action + " (UI only)")
        historyIndex--
    }

    function redo() {
        if (historyIndex >= operationHistory.length - 1) return
        historyIndex++
        var op = operationHistory[historyIndex]
        addMessage("system", "Redo: " + op.action + " (UI only)")
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        Label {
            text: "Chat"
            color: "#8892b0"
            font.pixelSize: 14
            font.bold: true
        }

        ListView {
            id: chatList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 6
            model: ListModel { id: chatModel }

            delegate: Rectangle {
                width: chatList.width
                height: msgText.implicitHeight + 16
                radius: 8
                color: role === "user" ? "#1a3a5c" :
                       role === "ai" ? "#1e3a2e" : "#3a1a1a"

                Text {
                    id: msgText
                    anchors.fill: parent
                    anchors.margins: 8
                    text: model.text
                    color: "white"
                    wrapMode: Text.WordWrap
                    font.pixelSize: 13
                }
            }

            Component.onCompleted: {
                chatModel.append({"role": "ai", "text": "Welcome to Zigma! Enter a building prompt to generate a 3D BIM model."})
            }
        }

        // Undo/Redo row
        RowLayout {
            Layout.fillWidth: true
            spacing: 4
            visible: operationHistory.length > 0

            Button {
                text: "Undo"
                enabled: historyIndex >= 0
                onClicked: root.undo()
                implicitWidth: 60
                implicitHeight: 24
                background: Rectangle { color: enabled ? "#555" : "#333"; radius: 4 }
                contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
            }
            Button {
                text: "Redo"
                enabled: historyIndex < operationHistory.length - 1
                onClicked: root.redo()
                implicitWidth: 60
                implicitHeight: 24
                background: Rectangle { color: enabled ? "#555" : "#333"; radius: 4 }
                contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter }
            }
            Label {
                text: (historyIndex + 1) + "/" + operationHistory.length + " ops"
                color: "#8892b0"
                font.pixelSize: 10
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 4

            TextField {
                id: inputField
                Layout.fillWidth: true
                placeholderText: "Describe a building..."
                color: "white"
                placeholderTextColor: "#666"
                background: Rectangle {
                    color: "#0a1628"
                    radius: 6
                    border.color: inputField.activeFocus ? "#4a9eff" : "#333"
                    border.width: 1
                }
                onAccepted: sendBtn.clicked()
            }

            Button {
                id: sendBtn
                text: "Send"
                enabled: inputField.text.length > 0 && agentBridge && !agentBridge.busy
                onClicked: {
                    var prompt = inputField.text
                    root.addMessage("user", prompt)
                    if (agentBridge) {
                        agentBridge.generate(prompt, {"width": 100, "depth": 80})
                    }
                    inputField.text = ""
                }
                background: Rectangle {
                    color: sendBtn.enabled ? "#4a9eff" : "#333"
                    radius: 6
                }
                contentItem: Text {
                    text: sendBtn.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }
    }
}

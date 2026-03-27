import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    property var agentBridge: null

    function addMessage(role, text) {
        chatModel.append({"role": role, "text": text})
        chatList.positionViewAtEnd()
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

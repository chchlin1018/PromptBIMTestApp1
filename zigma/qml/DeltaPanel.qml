import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    property var deltaHistory: ListModel { id: historyModel }
    property var currentDelta: null

    // Undo stack
    property var undoStack: []
    property int maxUndo: 10

    signal undoRequested()

    function addDelta(description, costDelta, gfaDelta, scheduleDelta) {
        var entry = {
            "description": description,
            "costDelta": costDelta,
            "gfaDelta": gfaDelta,
            "scheduleDelta": scheduleDelta,
            "timestamp": new Date().toLocaleTimeString()
        }
        historyModel.insert(0, entry)
        if (historyModel.count > maxUndo)
            historyModel.remove(historyModel.count - 1)

        undoStack.push(entry)
        currentDelta = entry
    }

    function formatDelta(value, unit) {
        if (!value || value === 0) return "-"
        var prefix = value > 0 ? "+" : ""
        var color = value > 0 ? "#ef4444" : "#4ade80"
        return prefix + Math.round(value).toLocaleString() + " " + unit
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Changes"
                color: "#8892b0"
                font.pixelSize: 14
                font.bold: true
                Layout.fillWidth: true
            }
            Button {
                text: "Undo"
                enabled: undoStack.length > 0
                onClicked: root.undoRequested()
                implicitWidth: 60
                implicitHeight: 28
                background: Rectangle {
                    color: parent.enabled ? "#4a9eff" : "#333"
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        // Current delta summary
        Rectangle {
            Layout.fillWidth: true
            height: currentDelta ? 80 : 0
            visible: currentDelta !== null
            radius: 8
            color: "#0a1628"

            GridLayout {
                anchors.fill: parent
                anchors.margins: 8
                columns: 3
                rowSpacing: 4
                columnSpacing: 8

                Label { text: "Cost"; color: "#8892b0"; font.pixelSize: 11 }
                Label { text: "GFA"; color: "#8892b0"; font.pixelSize: 11 }
                Label { text: "Schedule"; color: "#8892b0"; font.pixelSize: 11 }

                Label {
                    text: currentDelta ? formatDelta(currentDelta.costDelta, "NT$") : ""
                    color: currentDelta && currentDelta.costDelta > 0 ? "#ef4444" : "#4ade80"
                    font.pixelSize: 14
                    font.bold: true
                }
                Label {
                    text: currentDelta ? formatDelta(currentDelta.gfaDelta, "m²") : ""
                    color: currentDelta && currentDelta.gfaDelta > 0 ? "#f59e0b" : "#4ade80"
                    font.pixelSize: 14
                    font.bold: true
                }
                Label {
                    text: currentDelta ? formatDelta(currentDelta.scheduleDelta, "days") : ""
                    color: currentDelta && currentDelta.scheduleDelta > 0 ? "#ef4444" : "#4ade80"
                    font.pixelSize: 14
                    font.bold: true
                }
            }
        }

        // History list
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 4
            model: historyModel

            delegate: Rectangle {
                width: parent ? parent.width : 0
                height: 44
                radius: 6
                color: index === 0 ? "#1a2744" : "#0a1628"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 6
                    spacing: 2
                    Label {
                        text: model.description || ""
                        color: "white"
                        font.pixelSize: 12
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    Label {
                        text: model.timestamp || ""
                        color: "#555"
                        font.pixelSize: 10
                    }
                }
            }
        }

        Label {
            text: "No changes yet"
            color: "#555"
            font.pixelSize: 13
            Layout.alignment: Qt.AlignHCenter
            visible: historyModel.count === 0
        }
    }
}

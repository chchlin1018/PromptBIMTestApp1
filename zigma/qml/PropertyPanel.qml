import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    property var currentElement: null

    function showElement(elemId, elemData) {
        currentElement = elemData
    }

    function formatCost(value) {
        if (!value) return "N/A"
        var str = Math.round(value).toString()
        return "NT$ " + str.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        Label {
            text: "Properties"
            color: "#8892b0"
            font.pixelSize: 14
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#0a1628"
            radius: 8

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8
                visible: currentElement !== null

                Label {
                    text: currentElement ? (currentElement.id || "Unknown") : ""
                    color: "#4a9eff"
                    font.pixelSize: 16
                    font.bold: true
                }

                GridLayout {
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 6
                    Layout.fillWidth: true

                    Label { text: "Type"; color: "#8892b0"; font.pixelSize: 12 }
                    Label { text: currentElement ? (currentElement.type || "") : ""; color: "white"; font.pixelSize: 12 }

                    Label { text: "Material"; color: "#8892b0"; font.pixelSize: 12 }
                    Label { text: currentElement ? (currentElement.material || "") : ""; color: "white"; font.pixelSize: 12 }

                    Label { text: "Story"; color: "#8892b0"; font.pixelSize: 12 }
                    Label { text: currentElement ? String(currentElement.story || 0) : ""; color: "white"; font.pixelSize: 12 }

                    Label { text: "Width"; color: "#8892b0"; font.pixelSize: 12 }
                    Label {
                        text: currentElement && currentElement.dimensions ? (currentElement.dimensions.width + " m") : ""
                        color: "white"; font.pixelSize: 12
                    }

                    Label { text: "Height"; color: "#8892b0"; font.pixelSize: 12 }
                    Label {
                        text: currentElement && currentElement.dimensions ? (currentElement.dimensions.height + " m") : ""
                        color: "white"; font.pixelSize: 12
                    }

                    Label { text: "Depth"; color: "#8892b0"; font.pixelSize: 12 }
                    Label {
                        text: currentElement && currentElement.dimensions ? (currentElement.dimensions.depth + " m") : ""
                        color: "white"; font.pixelSize: 12
                    }

                    Label { text: "Cost"; color: "#8892b0"; font.pixelSize: 12 }
                    Label {
                        text: currentElement ? formatCost(currentElement.cost) : ""
                        color: "#4ade80"; font.pixelSize: 12
                    }
                }
            }

            Label {
                anchors.centerIn: parent
                text: "Click a 3D element\nto view properties"
                color: "#555"
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 14
                visible: currentElement === null
            }
        }
    }
}

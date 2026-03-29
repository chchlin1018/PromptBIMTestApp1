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

    function formatVector(arr) {
        if (!arr) return ""
        if (Array.isArray(arr))
            return "(" + arr.map(function(v){ return Math.round(v*10)/10 }).join(", ") + ")"
        return String(arr)
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
                    text: currentElement ? (currentElement.name || currentElement.id || "Unknown") : ""
                    color: "#4a9eff"
                    font.pixelSize: 16
                    font.bold: true
                }

                GridLayout {
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 6
                    Layout.fillWidth: true

                    Label { text: "ID"; color: "#8892b0"; font.pixelSize: 12 }
                    Label { text: currentElement ? (currentElement.id || "") : ""; color: "white"; font.pixelSize: 12 }

                    Label { text: "Type"; color: "#8892b0"; font.pixelSize: 12 }
                    Label { text: currentElement ? (currentElement.type || "") : ""; color: "white"; font.pixelSize: 12 }

                    Label { text: "Name"; color: "#8892b0"; font.pixelSize: 12 }
                    Label { text: currentElement ? (currentElement.name || "") : ""; color: "white"; font.pixelSize: 12 }

                    Label { text: "Position"; color: "#8892b0"; font.pixelSize: 12 }
                    Label {
                        text: currentElement ? formatVector(currentElement.position) : ""
                        color: "white"; font.pixelSize: 12
                    }

                    Label { text: "Dimensions"; color: "#8892b0"; font.pixelSize: 12 }
                    Label {
                        text: currentElement ? formatVector(currentElement.dimensions) : ""
                        color: "white"; font.pixelSize: 12
                    }

                    // Legacy fields for dynamic BIM elements
                    Label {
                        text: "Material"; color: "#8892b0"; font.pixelSize: 12
                        visible: currentElement && currentElement.material
                    }
                    Label {
                        text: currentElement ? (currentElement.material || "") : ""
                        color: "white"; font.pixelSize: 12
                        visible: currentElement && currentElement.material
                    }

                    Label { text: "Cost"; color: "#8892b0"; font.pixelSize: 12 }
                    Label {
                        text: {
                            if (!currentElement) return ""
                            if (currentElement.cost) return formatCost(currentElement.cost)
                            if (currentElement.properties && currentElement.properties.cost_ntd)
                                return formatCost(currentElement.properties.cost_ntd)
                            return "N/A"
                        }
                        color: "#4ade80"; font.pixelSize: 12
                    }
                }

                // BIMEntity connections
                Label {
                    text: "Connections"
                    color: "#8892b0"
                    font.pixelSize: 12
                    font.bold: true
                    visible: currentElement && currentElement.connections && currentElement.connections.length > 0
                }
                Label {
                    text: currentElement && currentElement.connections ? currentElement.connections.join(", ") : ""
                    color: "white"
                    font.pixelSize: 11
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    visible: currentElement && currentElement.connections && currentElement.connections.length > 0
                }

                // BIMEntity custom properties
                Label {
                    text: "Custom Properties"
                    color: "#8892b0"
                    font.pixelSize: 12
                    font.bold: true
                    visible: currentElement && currentElement.properties && Object.keys(currentElement.properties).length > 0
                }
                Repeater {
                    model: {
                        if (!currentElement || !currentElement.properties) return []
                        var keys = Object.keys(currentElement.properties)
                        var items = []
                        for (var i = 0; i < keys.length; i++) {
                            items.push({key: keys[i], value: currentElement.properties[keys[i]]})
                        }
                        return items
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label { text: modelData.key; color: "#8892b0"; font.pixelSize: 11; Layout.preferredWidth: 100 }
                        Label { text: String(modelData.value); color: "white"; font.pixelSize: 11 }
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

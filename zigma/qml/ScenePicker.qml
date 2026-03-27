import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    signal sceneSelected(string sceneId, string prompt, var landData)

    property var scenes: [
        {
            id: "s1_villa",
            name: "S1: Villa with Pool",
            description: "1200m² | 4 stories | BCR=45%",
            prompt: "Build a luxury villa with swimming pool, 30m x 40m land",
            land: { width: 30, depth: 40 }
        },
        {
            id: "s2_fab",
            name: "S2: TSMC Semiconductor Fab",
            description: "9600m² | 4 stories | Cleanroom",
            prompt: "Build a TSMC-style semiconductor fab on 120m x 80m land with cleanroom floors",
            land: { width: 120, depth: 80 }
        },
        {
            id: "s3_datacenter",
            name: "S3: Data Center",
            description: "4800m² | 5 stories | TIA-942",
            prompt: "Build a tier-3 data center on 80m x 60m land with raised floor and cooling",
            land: { width: 80, depth: 60 }
        }
    ]

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        Label {
            text: "Scene Templates"
            color: "#8892b0"
            font.pixelSize: 14
            font.bold: true
        }

        Repeater {
            model: scenes

            Rectangle {
                Layout.fillWidth: true
                height: 70
                radius: 8
                color: sceneMouseArea.containsMouse ? "#1a3a5c" : "#0a1628"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 4

                    Label {
                        text: modelData.name
                        color: "#4a9eff"
                        font.pixelSize: 13
                        font.bold: true
                    }
                    Label {
                        text: modelData.description
                        color: "#8892b0"
                        font.pixelSize: 11
                    }
                }

                MouseArea {
                    id: sceneMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.sceneSelected(modelData.id, modelData.prompt, modelData.land)
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}

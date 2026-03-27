import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    signal assetSelected(string assetId, string category, string name)

    property string searchText: ""

    property var assets: [
        { id: "beam_h200", category: "Structural", name: "H200 Steel Beam", material: "steel" },
        { id: "beam_h300", category: "Structural", name: "H300 Steel Beam", material: "steel" },
        { id: "col_400", category: "Structural", name: "400mm RC Column", material: "concrete" },
        { id: "col_600", category: "Structural", name: "600mm RC Column", material: "concrete" },
        { id: "slab_200", category: "Structural", name: "200mm RC Slab", material: "concrete" },
        { id: "wall_ext", category: "Envelope", name: "Exterior Wall 200mm", material: "concrete" },
        { id: "wall_int", category: "Envelope", name: "Interior Wall 100mm", material: "concrete" },
        { id: "curtain_wall", category: "Envelope", name: "Curtain Wall Glass", material: "glass" },
        { id: "win_1200", category: "Openings", name: "Window 1200x1500", material: "glass" },
        { id: "win_2400", category: "Openings", name: "Window 2400x1500", material: "glass" },
        { id: "door_900", category: "Openings", name: "Door 900x2100", material: "wood" },
        { id: "door_1200", category: "Openings", name: "Double Door 1200x2100", material: "wood" },
        { id: "ahu_unit", category: "MEP", name: "AHU Unit", material: "steel" },
        { id: "chiller", category: "MEP", name: "Chiller", material: "steel" },
        { id: "ups_rack", category: "MEP", name: "UPS Rack", material: "steel" },
        { id: "hepa_filter", category: "MEP", name: "HEPA Filter Unit", material: "steel" },
        { id: "raised_floor", category: "Interior", name: "Raised Floor Tile", material: "steel" },
        { id: "ceiling_tile", category: "Interior", name: "Ceiling Tile 600x600", material: "concrete" },
        { id: "parking_space", category: "Site", name: "Parking Space", material: "concrete" },
        { id: "pool", category: "Site", name: "Swimming Pool", material: "glass" },
        { id: "solar_panel", category: "Site", name: "Solar Panel", material: "glass" },
        { id: "elevator", category: "Vertical", name: "Elevator Shaft", material: "steel" },
        { id: "stair", category: "Vertical", name: "Staircase", material: "concrete" },
        { id: "ramp", category: "Vertical", name: "Access Ramp", material: "concrete" }
    ]

    property var filteredAssets: {
        if (searchText.length === 0) return assets
        var lower = searchText.toLowerCase()
        return assets.filter(function(a) {
            return a.name.toLowerCase().indexOf(lower) >= 0 ||
                   a.category.toLowerCase().indexOf(lower) >= 0
        })
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        Label {
            text: "Asset Browser"
            color: "#8892b0"
            font.pixelSize: 14
            font.bold: true
        }

        TextField {
            id: searchField
            Layout.fillWidth: true
            placeholderText: "Search assets..."
            color: "white"
            placeholderTextColor: "#666"
            onTextChanged: root.searchText = text
            background: Rectangle {
                color: "#0a1628"
                radius: 6
                border.color: searchField.activeFocus ? "#4a9eff" : "#333"
                border.width: 1
            }
        }

        Label {
            text: filteredAssets.length + " assets"
            color: "#555"
            font.pixelSize: 11
        }

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 4
            model: filteredAssets

            delegate: Rectangle {
                width: parent ? parent.width : 0
                height: 48
                radius: 6
                color: assetMouse.containsMouse ? "#1a3a5c" : "#0a1628"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Rectangle {
                        width: 32; height: 32; radius: 4
                        color: {
                            var m = modelData.material
                            if (m === "steel") return "#8888aa"
                            if (m === "glass") return "#7799cc"
                            if (m === "wood") return "#886633"
                            return "#666666"
                        }
                        Label {
                            anchors.centerIn: parent
                            text: modelData.category.charAt(0)
                            color: "white"
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Layout.fillWidth: true
                        Label {
                            text: modelData.name
                            color: "white"
                            font.pixelSize: 12
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        Label {
                            text: modelData.category
                            color: "#8892b0"
                            font.pixelSize: 10
                        }
                    }
                }

                MouseArea {
                    id: assetMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.assetSelected(modelData.id, modelData.category, modelData.name)
                }
            }
        }
    }
}

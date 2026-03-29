import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    property var costData: null
    property double totalCost: costData ? (costData.total_cost_twd || 0) : 0
    property var breakdown: costData ? (costData.breakdown || []) : []
    property var costDelta: null
    property double deltaAmount: costDelta ? (costDelta.total_delta_ntd || 0) : 0

    onBreakdownChanged: pieChart.requestPaint()

    function applyCostDelta(delta) {
        costDelta = delta
    }

    function formatNTD(value) {
        var str = Math.round(value).toString()
        return "NT$ " + str.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        Label {
            text: "Cost Estimate"
            color: "#8892b0"
            font.pixelSize: 14
            font.bold: true
        }

        // Total cost
        Rectangle {
            Layout.fillWidth: true
            height: 60
            radius: 8
            color: "#0a1628"

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 2
                Label {
                    text: "Total"
                    color: "#8892b0"
                    font.pixelSize: 11
                    Layout.alignment: Qt.AlignHCenter
                }
                Label {
                    text: formatNTD(totalCost)
                    color: "#4ade80"
                    font.pixelSize: 20
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        // Pie chart canvas
        Canvas {
            id: pieChart
            Layout.fillWidth: true
            Layout.preferredHeight: 150
            visible: breakdown.length > 0

            property var colors: ["#4a9eff", "#4ade80", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]

            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                if (root.breakdown.length === 0) return

                var cx = width / 2, cy = height / 2, r = Math.min(cx, cy) - 10
                var total = 0
                for (var i = 0; i < root.breakdown.length; i++)
                    total += (root.breakdown[i].cost_twd || root.breakdown[i].ratio || 1)

                var startAngle = -Math.PI / 2
                for (var j = 0; j < root.breakdown.length; j++) {
                    var value = root.breakdown[j].cost_twd || root.breakdown[j].ratio || 1
                    var sweep = (value / total) * 2 * Math.PI
                    ctx.beginPath()
                    ctx.moveTo(cx, cy)
                    ctx.arc(cx, cy, r, startAngle, startAngle + sweep)
                    ctx.closePath()
                    ctx.fillStyle = colors[j % colors.length]
                    ctx.fill()
                    startAngle += sweep
                }
            }
        }

        // Breakdown list
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 4
            model: breakdown

            delegate: RowLayout {
                width: parent ? parent.width : 0
                spacing: 8

                Rectangle {
                    width: 10; height: 10; radius: 2
                    color: pieChart.colors[index % pieChart.colors.length]
                }
                Label {
                    text: modelData.label || modelData.category || ""
                    color: "white"
                    font.pixelSize: 12
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                Label {
                    text: root.formatNTD(modelData.cost_twd || 0)
                    color: "#8892b0"
                    font.pixelSize: 12
                }
            }
        }

        // Cost delta indicator
        Rectangle {
            Layout.fillWidth: true
            height: 40
            radius: 6
            color: deltaAmount > 0 ? "#3a1a1a" : deltaAmount < 0 ? "#1a3a1a" : "#1a1a3a"
            visible: costDelta !== null

            RowLayout {
                anchors.centerIn: parent
                spacing: 8
                Label {
                    text: "Delta"
                    color: "#8892b0"
                    font.pixelSize: 11
                }
                Label {
                    text: (deltaAmount >= 0 ? "+" : "") + formatNTD(deltaAmount)
                    color: deltaAmount > 0 ? "#ef4444" : deltaAmount < 0 ? "#4ade80" : "#8892b0"
                    font.pixelSize: 14
                    font.bold: true
                }
            }
        }

        Label {
            text: "No cost data"
            color: "#555"
            font.pixelSize: 13
            Layout.alignment: Qt.AlignHCenter
            visible: !costData
        }
    }
}

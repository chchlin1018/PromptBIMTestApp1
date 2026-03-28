import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#16213e"

    property var scheduleData: null
    property int totalDays: scheduleData ? (scheduleData.total_days || 360) : 360
    property var phases: scheduleData ? (scheduleData.phases || []) : []
    property int currentDay: 0
    property bool playing: false
    property real playSpeed: 1.0

    signal dayClicked(int day)
    signal phaseClicked(string phaseName)

    onCurrentDayChanged: ganttChart.requestPaint()
    onPhasesChanged: ganttChart.requestPaint()

    Timer {
        id: playTimer
        interval: 100 / playSpeed
        repeat: true
        running: playing
        onTriggered: {
            if (currentDay < totalDays) {
                currentDay += 1
                root.dayClicked(currentDay)
            } else {
                playing = false
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Schedule"
                color: "#8892b0"
                font.pixelSize: 14
                font.bold: true
                Layout.fillWidth: true
            }
            Label {
                text: totalDays + " days"
                color: "#4a9eff"
                font.pixelSize: 12
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Button {
                text: playing ? "\u23F8" : "\u25B6"
                implicitWidth: 36; implicitHeight: 28
                onClicked: playing = !playing
                background: Rectangle { color: "#333355"; radius: 4 }
                contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter }
            }

            Slider {
                id: timeSlider
                Layout.fillWidth: true
                from: 0; to: totalDays
                value: currentDay
                onValueChanged: {
                    currentDay = Math.round(value)
                    root.dayClicked(currentDay)
                }

                background: Rectangle {
                    x: timeSlider.leftPadding
                    y: timeSlider.topPadding + timeSlider.availableHeight / 2 - 3
                    width: timeSlider.availableWidth; height: 6; radius: 3
                    color: "#0a1628"
                    Rectangle {
                        width: timeSlider.visualPosition * parent.width
                        height: parent.height; radius: 3; color: "#4a9eff"
                    }
                }
                handle: Rectangle {
                    x: timeSlider.leftPadding + timeSlider.visualPosition * (timeSlider.availableWidth - width)
                    y: timeSlider.topPadding + timeSlider.availableHeight / 2 - height / 2
                    width: 14; height: 14; radius: 7; color: "#4a9eff"
                }
            }

            Label {
                text: "Day " + currentDay
                color: "white"
                font.pixelSize: 11
                Layout.minimumWidth: 60
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 4
            Label { text: "Speed:"; color: "#8892b0"; font.pixelSize: 11 }
            Repeater {
                model: [1, 2, 5, 10]
                Button {
                    text: modelData + "x"
                    implicitWidth: 36; implicitHeight: 24
                    onClicked: { root.playSpeed = modelData; playTimer.interval = 100 / modelData }
                    background: Rectangle {
                        color: root.playSpeed === modelData ? "#4a9eff" : "#333355"
                        radius: 4
                    }
                    contentItem: Text { text: parent.text; color: "white"; font.pixelSize: 10; horizontalAlignment: Text.AlignHCenter }
                }
            }
        }

        Canvas {
            id: ganttChart
            Layout.fillWidth: true
            Layout.fillHeight: true

            property var phaseColors: ["#4a9eff", "#4ade80", "#f59e0b", "#ef4444",
                                        "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16",
                                        "#f97316", "#6366f1", "#14b8a6", "#e11d48"]

            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                if (root.phases.length === 0) return

                var barH = Math.min(20, (height - 20) / root.phases.length - 2)
                var scale = (width - 120) / root.totalDays

                for (var i = 0; i < root.phases.length; i++) {
                    var p = root.phases[i]
                    var y = i * (barH + 2) + 2
                    var x = 120 + (p.start_day || 0) * scale
                    var w = ((p.end_day || 0) - (p.start_day || 0)) * scale

                    ctx.fillStyle = "#8892b0"
                    ctx.font = "10px sans-serif"
                    ctx.fillText((p.phase || "").substring(0, 15), 4, y + barH - 4)

                    var day = root.currentDay
                    var startDay = p.start_day || 0
                    var endDay = p.end_day || 0

                    if (day >= endDay) {
                        ctx.fillStyle = phaseColors[i % phaseColors.length]
                        ctx.globalAlpha = 1.0
                    } else if (day >= startDay) {
                        ctx.fillStyle = phaseColors[i % phaseColors.length]
                        ctx.globalAlpha = 0.5
                    } else {
                        ctx.fillStyle = "#333"
                        ctx.globalAlpha = 0.3
                    }

                    ctx.fillRect(x, y, Math.max(w, 2), barH)
                    ctx.globalAlpha = 1.0
                }

                var dayX = 120 + root.currentDay * scale
                ctx.strokeStyle = "#ef4444"
                ctx.lineWidth = 2
                ctx.beginPath()
                ctx.moveTo(dayX, 0)
                ctx.lineTo(dayX, height)
                ctx.stroke()
            }

            MouseArea {
                anchors.fill: parent
                onClicked: function(mouse) {
                    var scale = (parent.width - 120) / root.totalDays
                    var day = Math.round((mouse.x - 120) / scale)
                    if (day >= 0 && day <= root.totalDays) {
                        root.currentDay = day
                        timeSlider.value = day
                    }
                }
            }
        }

        Label {
            text: "No schedule data"
            color: "#555"
            font.pixelSize: 13
            Layout.alignment: Qt.AlignHCenter
            visible: phases.length === 0
        }
    }
}

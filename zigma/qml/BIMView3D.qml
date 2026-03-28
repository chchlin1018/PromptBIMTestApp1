import QtQuick
import QtQuick.Controls
import QtQuick3D
import QtQuick3D.Helpers

Item {
    id: root

    signal elementPicked(string elementId, var elementData)

    property alias sceneRoot: bimDynamicRoot
    property var sceneBuilder: null
    property var materialLibrary: null
    property int currentView: 0
    property bool demoMode: true

    function fitToScene() {
        perspCamera.position = Qt.vector3d(-80, 60, 100)
        perspCamera.eulerRotation = Qt.vector3d(-25, -30, 0)
    }

    function setView(viewIndex) {
        currentView = viewIndex
        switch(viewIndex) {
        case 0:
            cameraAnim.to = Qt.vector3d(-80, 60, 100)
            rotAnim.to = Qt.vector3d(-25, -30, 0)
            break
        case 1:
            cameraAnim.to = Qt.vector3d(0, 150, 0)
            rotAnim.to = Qt.vector3d(-90, 0, 0)
            break
        case 2:
            cameraAnim.to = Qt.vector3d(0, 20, 120)
            rotAnim.to = Qt.vector3d(0, 0, 0)
            break
        case 3:
            cameraAnim.to = Qt.vector3d(120, 20, 0)
            rotAnim.to = Qt.vector3d(0, 90, 0)
            break
        }
        cameraAnim.running = true
        rotAnim.running = true
    }

    View3D {
        id: view3d
        anchors.fill: parent

        environment: SceneEnvironment {
            backgroundMode: SceneEnvironment.Color
            clearColor: ThemeManager.viewport
            antialiasingMode: SceneEnvironment.MSAA
            antialiasingQuality: SceneEnvironment.High
            aoEnabled: true
            aoStrength: 50
            aoDistance: 20
        }

        PerspectiveCamera {
            id: perspCamera
            position: Qt.vector3d(-80, 60, 100)
            eulerRotation: Qt.vector3d(-25, -30, 0)
            clipNear: 0.1
            clipFar: 2000
            fieldOfView: 60

            Vector3dAnimation on position {
                id: cameraAnim
                duration: 500
                easing.type: Easing.InOutQuad
                running: false
            }
            Vector3dAnimation on eulerRotation {
                id: rotAnim
                duration: 500
                easing.type: Easing.InOutQuad
                running: false
            }
        }

        OrbitCameraController {
            origin: sceneCenter
            camera: perspCamera
        }

        // Main directional light with shadows
        DirectionalLight {
            eulerRotation: Qt.vector3d(-45, 25, 0)
            brightness: 1.0
            castsShadow: true
            shadowMapQuality: Light.ShadowMapQualityHigh
        }

        // Fill light
        DirectionalLight {
            eulerRotation: Qt.vector3d(-30, -120, 0)
            brightness: 0.3
        }

        // Ambient point light
        PointLight {
            position: Qt.vector3d(0, 80, 0)
            brightness: 0.2
            quadraticFade: 0.001
        }

        Node {
            id: sceneCenter

            // Demo scene — visible when demoMode is on
            DemoScene {
                visible: root.demoMode
            }

            // BIM dynamic root — visible when demoMode is off
            Node {
                id: bimDynamicRoot
                visible: !root.demoMode

                Model {
                    source: "#Rectangle"
                    scale: Qt.vector3d(5, 5, 1)
                    eulerRotation.x: -90
                    materials: PrincipledMaterial {
                        baseColor: ThemeManager.ground
                        roughness: 0.95
                    }
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton
            onClicked: function(mouse) {
                var result = view3d.pick(mouse.x, mouse.y)
                if (result.objectHit && result.objectHit.elementData) {
                    root.elementPicked(
                        result.objectHit.elementData.id || "",
                        result.objectHit.elementData
                    )
                }
            }
        }
    }

    // View buttons — top right
    Row {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 8
        spacing: 4
        z: 10

        Repeater {
            model: ["3D", "Top", "Front", "Right"]
            Button {
                text: modelData
                flat: true
                highlighted: root.currentView === index
                onClicked: root.setView(index)
                background: Rectangle {
                    color: root.currentView === index ? "#4a9eff" : "#333355"
                    radius: 4
                    opacity: 0.8
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignHCenter
                }
                implicitWidth: 50
                implicitHeight: 28
            }
        }
    }

    // Mode label — top right below view buttons
    Label {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 42
        anchors.rightMargin: 8
        text: root.demoMode ? "DEMO" : "BIM"
        color: root.demoMode ? "#4aff9e" : "#ff9e4a"
        font.pixelSize: 10
        font.bold: true
        z: 10
        background: Rectangle {
            color: "#222244"
            radius: 3
            opacity: 0.7
        }
        padding: 4
    }

    // Bottom hint
    Label {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 8
        text: "Scroll to zoom · Drag to orbit · Right-drag to pan"
        color: "#aaaacc"
        font.pixelSize: 10
        z: 10
        background: Rectangle {
            color: "#1a1a2e"
            radius: 4
            opacity: 0.6
        }
        padding: 4
    }

    Component.onCompleted: {
        if (typeof zigmaLogger !== "undefined") {
            zigmaLogger.logFromQml("BIMView3D", "INFO", "3D viewport initialized, demoMode=" + root.demoMode)
        }
    }
}

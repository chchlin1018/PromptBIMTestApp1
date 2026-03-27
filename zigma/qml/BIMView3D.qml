import QtQuick
import QtQuick.Controls
import QtQuick3D
import QtQuick3D.Helpers

Item {
    id: root

    signal elementPicked(string elementId, var elementData)

    property alias sceneRoot: sceneNode
    property var sceneBuilder: null
    property var materialLibrary: null
    property int currentView: 0

    function fitToScene() {
        perspCamera.position = Qt.vector3d(50, 50, 50)
        perspCamera.eulerRotation = Qt.vector3d(-35, 45, 0)
    }

    function setView(viewIndex) {
        currentView = viewIndex
        switch(viewIndex) {
        case 0:
            cameraAnim.to = Qt.vector3d(50, 50, 50)
            rotAnim.to = Qt.vector3d(-35, 45, 0)
            break
        case 1:
            cameraAnim.to = Qt.vector3d(0, 100, 0)
            rotAnim.to = Qt.vector3d(-90, 0, 0)
            break
        case 2:
            cameraAnim.to = Qt.vector3d(0, 15, 80)
            rotAnim.to = Qt.vector3d(0, 0, 0)
            break
        case 3:
            cameraAnim.to = Qt.vector3d(80, 15, 0)
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
        }

        PerspectiveCamera {
            id: perspCamera
            position: Qt.vector3d(50, 50, 50)
            eulerRotation: Qt.vector3d(-35, 45, 0)
            clipNear: 0.1
            clipFar: 1000

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
            origin: sceneNode
            camera: perspCamera
        }

        DirectionalLight {
            eulerRotation: Qt.vector3d(-45, 25, 0)
            brightness: 1.0
            castsShadow: true
            shadowMapQuality: Light.ShadowMapQualityHigh
        }

        DirectionalLight {
            eulerRotation: Qt.vector3d(-30, -120, 0)
            brightness: 0.3
        }

        DirectionalLight {
            eulerRotation: Qt.vector3d(80, 0, 0)
            brightness: 0.2
        }

        Node {
            id: sceneNode

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
}

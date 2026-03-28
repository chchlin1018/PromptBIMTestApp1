import QtQuick
import QtQuick3D

Node {
    id: demoRoot

    // Ground plane 200x200m
    Model {
        source: "#Rectangle"
        scale: Qt.vector3d(20, 20, 1)
        eulerRotation.x: -90
        materials: PrincipledMaterial {
            baseColor: "#8fbc8f"
            roughness: 0.95
        }
    }

    // Main Fab building 80x25x50m - light gray white
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 12.5, 0)
        scale: Qt.vector3d(0.80, 0.25, 0.50)
        materials: PrincipledMaterial {
            baseColor: "#e8e8e8"
            roughness: 0.6
            metalness: 0.1
        }
    }

    // Rooftop equipment layer 75x4x45m
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 27, 0)
        scale: Qt.vector3d(0.75, 0.04, 0.45)
        materials: PrincipledMaterial {
            baseColor: "#cccccc"
            roughness: 0.7
            metalness: 0.2
        }
    }

    // Office building 25x20x20m - light blue
    Model {
        source: "#Cube"
        position: Qt.vector3d(-55, 10, 0)
        scale: Qt.vector3d(0.25, 0.20, 0.20)
        materials: PrincipledMaterial {
            baseColor: "#b0c4de"
            roughness: 0.5
            metalness: 0.1
        }
    }

    // CUB (Central Utility Building) 30x16x25m - light green
    Model {
        source: "#Cube"
        position: Qt.vector3d(55, 8, 0)
        scale: Qt.vector3d(0.30, 0.16, 0.25)
        materials: PrincipledMaterial {
            baseColor: "#90ee90"
            roughness: 0.6
        }
    }

    // Cooling towers x4 - cylinders
    Repeater3D {
        model: 4
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(55 + index * 8 - 12, 6, 30)
            scale: Qt.vector3d(0.06, 0.12, 0.06)
            materials: PrincipledMaterial {
                baseColor: "#a9a9a9"
                roughness: 0.7
            }
        }
    }

    // Exhaust stacks x3 - 35m tall, red
    Repeater3D {
        model: 3
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(-20 + index * 20, 17.5, -35)
            scale: Qt.vector3d(0.02, 0.35, 0.02)
            materials: PrincipledMaterial {
                baseColor: "#cd5c5c"
                roughness: 0.5
                metalness: 0.3
            }
        }
    }

    // Pipe rack corridor - yellow, 60x5x4m
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 6, 25)
        scale: Qt.vector3d(0.60, 0.05, 0.04)
        materials: PrincipledMaterial {
            baseColor: "#f0c040"
            roughness: 0.6
            metalness: 0.2
        }
    }

    // Pipe rack supports x6
    Repeater3D {
        model: 6
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(-25 + index * 10, 3, 25)
            scale: Qt.vector3d(0.008, 0.06, 0.008)
            materials: PrincipledMaterial {
                baseColor: "#808080"
                roughness: 0.7
                metalness: 0.4
            }
        }
    }

    // Perimeter walls (4 sides)
    // North wall
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 1.5, -80)
        scale: Qt.vector3d(1.60, 0.03, 0.01)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }
    // South wall
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 1.5, 80)
        scale: Qt.vector3d(1.60, 0.03, 0.01)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }
    // East wall
    Model {
        source: "#Cube"
        position: Qt.vector3d(80, 1.5, 0)
        scale: Qt.vector3d(0.01, 0.03, 1.60)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }
    // West wall
    Model {
        source: "#Cube"
        position: Qt.vector3d(-80, 1.5, 0)
        scale: Qt.vector3d(0.01, 0.03, 1.60)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }

    // Road - dark asphalt strip
    Model {
        source: "#Rectangle"
        position: Qt.vector3d(0, 0.05, 55)
        eulerRotation.x: -90
        scale: Qt.vector3d(12, 2, 1)
        materials: PrincipledMaterial { baseColor: "#404040"; roughness: 0.9 }
    }

    // Parking lot
    Model {
        source: "#Rectangle"
        position: Qt.vector3d(-55, 0.05, 55)
        eulerRotation.x: -90
        scale: Qt.vector3d(3, 2, 1)
        materials: PrincipledMaterial { baseColor: "#555555"; roughness: 0.85 }
    }

    Component.onCompleted: {
        if (typeof zigmaLogger !== "undefined") {
            zigmaLogger.logFromQml("DemoScene", "INFO", "TSMC fab demo scene loaded — 16 elements")
        }
    }
}

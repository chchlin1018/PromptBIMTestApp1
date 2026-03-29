import QtQuick
import QtQuick3D

Node {
    id: demoRoot

    // SceneGraph reference — set from main.qml
    property var sceneGraph: null

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

    // === Buildings ===

    // Main Fab building 80x25x50m
    Model {
        id: mainFab
        objectName: "main-fab"
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

    // Office building 25x20x20m
    Model {
        id: office
        objectName: "office"
        source: "#Cube"
        position: Qt.vector3d(-55, 10, 0)
        scale: Qt.vector3d(0.25, 0.20, 0.20)
        materials: PrincipledMaterial {
            baseColor: "#b0c4de"
            roughness: 0.5
            metalness: 0.1
        }
    }

    // CUB (Central Utility Building) 30x16x25m
    Model {
        id: cub
        objectName: "cub"
        source: "#Cube"
        position: Qt.vector3d(55, 8, 0)
        scale: Qt.vector3d(0.30, 0.16, 0.25)
        materials: PrincipledMaterial {
            baseColor: "#90ee90"
            roughness: 0.6
        }
    }

    // === CUB Equipment: Chillers ===

    Model {
        id: chillerA
        objectName: "chiller-A"
        source: "#Cube"
        position: Qt.vector3d(48, 3, -5)
        scale: Qt.vector3d(0.06, 0.06, 0.04)
        materials: PrincipledMaterial { baseColor: "#4a9eff"; roughness: 0.4; metalness: 0.6 }
    }

    Model {
        id: chillerB
        objectName: "chiller-B"
        source: "#Cube"
        position: Qt.vector3d(55, 3, -5)
        scale: Qt.vector3d(0.06, 0.06, 0.04)
        materials: PrincipledMaterial { baseColor: "#4a9eff"; roughness: 0.4; metalness: 0.6 }
    }

    Model {
        id: chillerC
        objectName: "chiller-C"
        source: "#Cube"
        position: Qt.vector3d(62, 3, -5)
        scale: Qt.vector3d(0.06, 0.06, 0.04)
        materials: PrincipledMaterial { baseColor: "#4a9eff"; roughness: 0.4; metalness: 0.6 }
    }

    // === CUB Equipment: Compressors ===

    Model {
        id: compressor01
        objectName: "compressor-01"
        source: "#Cylinder"
        position: Qt.vector3d(50, 2.5, 5)
        scale: Qt.vector3d(0.03, 0.05, 0.03)
        materials: PrincipledMaterial { baseColor: "#ff9e4a"; roughness: 0.5; metalness: 0.4 }
    }

    Model {
        id: compressor02
        objectName: "compressor-02"
        source: "#Cylinder"
        position: Qt.vector3d(60, 2.5, 5)
        scale: Qt.vector3d(0.03, 0.05, 0.03)
        materials: PrincipledMaterial { baseColor: "#ff9e4a"; roughness: 0.5; metalness: 0.4 }
    }

    // === Columns C1-C6 inside CUB ===

    Model {
        id: columnC1
        objectName: "column-C1"
        source: "#Cylinder"
        position: Qt.vector3d(43, 8, -8)
        scale: Qt.vector3d(0.008, 0.16, 0.008)
        materials: PrincipledMaterial { baseColor: "#888888"; roughness: 0.7; metalness: 0.3 }
    }
    Model {
        id: columnC2
        objectName: "column-C2"
        source: "#Cylinder"
        position: Qt.vector3d(55, 8, -8)
        scale: Qt.vector3d(0.008, 0.16, 0.008)
        materials: PrincipledMaterial { baseColor: "#888888"; roughness: 0.7; metalness: 0.3 }
    }
    Model {
        id: columnC3
        objectName: "column-C3"
        source: "#Cylinder"
        position: Qt.vector3d(67, 8, -8)
        scale: Qt.vector3d(0.008, 0.16, 0.008)
        materials: PrincipledMaterial { baseColor: "#888888"; roughness: 0.7; metalness: 0.3 }
    }
    Model {
        id: columnC4
        objectName: "column-C4"
        source: "#Cylinder"
        position: Qt.vector3d(43, 8, 8)
        scale: Qt.vector3d(0.008, 0.16, 0.008)
        materials: PrincipledMaterial { baseColor: "#888888"; roughness: 0.7; metalness: 0.3 }
    }
    Model {
        id: columnC5
        objectName: "column-C5"
        source: "#Cylinder"
        position: Qt.vector3d(55, 8, 8)
        scale: Qt.vector3d(0.008, 0.16, 0.008)
        materials: PrincipledMaterial { baseColor: "#888888"; roughness: 0.7; metalness: 0.3 }
    }
    Model {
        id: columnC6
        objectName: "column-C6"
        source: "#Cylinder"
        position: Qt.vector3d(67, 8, 8)
        scale: Qt.vector3d(0.008, 0.16, 0.008)
        materials: PrincipledMaterial { baseColor: "#888888"; roughness: 0.7; metalness: 0.3 }
    }

    // === Cooling Towers ===

    Model {
        id: coolingTower01
        objectName: "cooling-tower-01"
        source: "#Cylinder"
        position: Qt.vector3d(43, 6, 30)
        scale: Qt.vector3d(0.06, 0.12, 0.06)
        materials: PrincipledMaterial { baseColor: "#a9a9a9"; roughness: 0.7 }
    }
    Model {
        id: coolingTower02
        objectName: "cooling-tower-02"
        source: "#Cylinder"
        position: Qt.vector3d(51, 6, 30)
        scale: Qt.vector3d(0.06, 0.12, 0.06)
        materials: PrincipledMaterial { baseColor: "#a9a9a9"; roughness: 0.7 }
    }
    Model {
        id: coolingTower03
        objectName: "cooling-tower-03"
        source: "#Cylinder"
        position: Qt.vector3d(59, 6, 30)
        scale: Qt.vector3d(0.06, 0.12, 0.06)
        materials: PrincipledMaterial { baseColor: "#a9a9a9"; roughness: 0.7 }
    }
    Model {
        id: coolingTower04
        objectName: "cooling-tower-04"
        source: "#Cylinder"
        position: Qt.vector3d(67, 6, 30)
        scale: Qt.vector3d(0.06, 0.12, 0.06)
        materials: PrincipledMaterial { baseColor: "#a9a9a9"; roughness: 0.7 }
    }

    // === Exhaust Stacks ===

    Model {
        id: exhaustStack01
        objectName: "exhaust-stack-01"
        source: "#Cylinder"
        position: Qt.vector3d(-20, 17.5, -35)
        scale: Qt.vector3d(0.02, 0.35, 0.02)
        materials: PrincipledMaterial { baseColor: "#cd5c5c"; roughness: 0.5; metalness: 0.3 }
    }
    Model {
        id: exhaustStack02
        objectName: "exhaust-stack-02"
        source: "#Cylinder"
        position: Qt.vector3d(0, 17.5, -35)
        scale: Qt.vector3d(0.02, 0.35, 0.02)
        materials: PrincipledMaterial { baseColor: "#cd5c5c"; roughness: 0.5; metalness: 0.3 }
    }
    Model {
        id: exhaustStack03
        objectName: "exhaust-stack-03"
        source: "#Cylinder"
        position: Qt.vector3d(20, 17.5, -35)
        scale: Qt.vector3d(0.02, 0.35, 0.02)
        materials: PrincipledMaterial { baseColor: "#cd5c5c"; roughness: 0.5; metalness: 0.3 }
    }

    // === MEP Pipes (Phase 3) ===

    // Chilled water supply — Chillers to pipe rack (blue)
    Repeater3D {
        model: 3
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(48 + index * 7, 4.5, 10)
            scale: Qt.vector3d(0.005, 0.15, 0.005)
            eulerRotation.x: 90
            materials: PrincipledMaterial { baseColor: "#2196F3"; roughness: 0.3; metalness: 0.7; opacity: 0.8 }
        }
    }

    // Condenser water — Chillers to CoolingTowers (green)
    Repeater3D {
        model: 3
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(48 + index * 7, 5, 12.5)
            scale: Qt.vector3d(0.005, 0.35, 0.005)
            materials: PrincipledMaterial { baseColor: "#4CAF50"; roughness: 0.3; metalness: 0.7; opacity: 0.8 }
        }
    }

    // Condenser water horizontal header — connecting all cooling towers
    Model {
        source: "#Cylinder"
        position: Qt.vector3d(55, 5, 30)
        scale: Qt.vector3d(0.005, 0.25, 0.005)
        eulerRotation.z: 90
        materials: PrincipledMaterial { baseColor: "#4CAF50"; roughness: 0.3; metalness: 0.7; opacity: 0.8 }
    }

    // Power cables — Compressors to CUB (red)
    Repeater3D {
        model: 2
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(50 + index * 10, 1.5, 2.5)
            scale: Qt.vector3d(0.003, 0.05, 0.003)
            eulerRotation.x: 90
            materials: PrincipledMaterial { baseColor: "#F44336"; roughness: 0.4; metalness: 0.5; opacity: 0.8 }
        }
    }

    // Chilled water main header — connecting all chillers horizontally
    Model {
        source: "#Cylinder"
        position: Qt.vector3d(55, 3, -5)
        scale: Qt.vector3d(0.005, 0.15, 0.005)
        eulerRotation.z: 90
        materials: PrincipledMaterial { baseColor: "#2196F3"; roughness: 0.3; metalness: 0.7; opacity: 0.8 }
    }

    // === Infrastructure ===

    // Pipe rack corridor 60x5x4m
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 6, 25)
        scale: Qt.vector3d(0.60, 0.05, 0.04)
        materials: PrincipledMaterial { baseColor: "#f0c040"; roughness: 0.6; metalness: 0.2 }
    }

    // Pipe rack supports x6
    Repeater3D {
        model: 6
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(-25 + index * 10, 3, 25)
            scale: Qt.vector3d(0.008, 0.06, 0.008)
            materials: PrincipledMaterial { baseColor: "#808080"; roughness: 0.7; metalness: 0.4 }
        }
    }

    // Perimeter walls
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 1.5, -80)
        scale: Qt.vector3d(1.60, 0.03, 0.01)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }
    Model {
        source: "#Cube"
        position: Qt.vector3d(0, 1.5, 80)
        scale: Qt.vector3d(1.60, 0.03, 0.01)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }
    Model {
        source: "#Cube"
        position: Qt.vector3d(80, 1.5, 0)
        scale: Qt.vector3d(0.01, 0.03, 1.60)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }
    Model {
        source: "#Cube"
        position: Qt.vector3d(-80, 1.5, 0)
        scale: Qt.vector3d(0.01, 0.03, 1.60)
        materials: PrincipledMaterial { baseColor: "#696969"; roughness: 0.8 }
    }

    // Road
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
            zigmaLogger.logFromQml("DemoScene", "INFO", "TSMC fab demo scene loaded — 22 named entities")
        }

        // Register all named entities to SceneGraph
        if (sceneGraph) {
            var entities = [
                { id: "main-fab",    type: "Building.Fab",         name: "Main Fab",        pos: Qt.vector3d(0, 12.5, 0),    dims: Qt.vector3d(80, 25, 50),  props: {area_sqm: 4000, cleanroom_class: "1000"} },
                { id: "office",      type: "Building.Office",      name: "Office",          pos: Qt.vector3d(-55, 10, 0),    dims: Qt.vector3d(25, 20, 20),  props: {floors: 4} },
                { id: "cub",         type: "Building.CUB",         name: "CUB",             pos: Qt.vector3d(55, 8, 0),      dims: Qt.vector3d(30, 16, 25),  props: {capacity_mw: 12} },
                { id: "chiller-A",   type: "MEP.Chiller",          name: "冰水主機-A",       pos: Qt.vector3d(48, 3, -5),     dims: Qt.vector3d(6, 6, 4),     props: {capacity_rt: 500, power_kw: 350, cost_ntd: 2500000} },
                { id: "chiller-B",   type: "MEP.Chiller",          name: "冰水主機-B",       pos: Qt.vector3d(55, 3, -5),     dims: Qt.vector3d(6, 6, 4),     props: {capacity_rt: 500, power_kw: 350, cost_ntd: 2500000} },
                { id: "chiller-C",   type: "MEP.Chiller",          name: "冰水主機-C",       pos: Qt.vector3d(62, 3, -5),     dims: Qt.vector3d(6, 6, 4),     props: {capacity_rt: 500, power_kw: 350, cost_ntd: 2500000} },
                { id: "compressor-01", type: "MEP.Compressor",     name: "Compressor-01",   pos: Qt.vector3d(50, 2.5, 5),    dims: Qt.vector3d(3, 5, 3),     props: {pressure_bar: 7, power_kw: 150, cost_ntd: 800000} },
                { id: "compressor-02", type: "MEP.Compressor",     name: "Compressor-02",   pos: Qt.vector3d(60, 2.5, 5),    dims: Qt.vector3d(3, 5, 3),     props: {pressure_bar: 7, power_kw: 150, cost_ntd: 800000} },
                { id: "column-C1",   type: "Structural.Column",    name: "Column-C1",       pos: Qt.vector3d(43, 8, -8),     dims: Qt.vector3d(0.8, 16, 0.8), props: {} },
                { id: "column-C2",   type: "Structural.Column",    name: "Column-C2",       pos: Qt.vector3d(55, 8, -8),     dims: Qt.vector3d(0.8, 16, 0.8), props: {} },
                { id: "column-C3",   type: "Structural.Column",    name: "Column-C3",       pos: Qt.vector3d(67, 8, -8),     dims: Qt.vector3d(0.8, 16, 0.8), props: {} },
                { id: "column-C4",   type: "Structural.Column",    name: "Column-C4",       pos: Qt.vector3d(43, 8, 8),      dims: Qt.vector3d(0.8, 16, 0.8), props: {} },
                { id: "column-C5",   type: "Structural.Column",    name: "Column-C5",       pos: Qt.vector3d(55, 8, 8),      dims: Qt.vector3d(0.8, 16, 0.8), props: {} },
                { id: "column-C6",   type: "Structural.Column",    name: "Column-C6",       pos: Qt.vector3d(67, 8, 8),      dims: Qt.vector3d(0.8, 16, 0.8), props: {} },
                { id: "cooling-tower-01", type: "MEP.CoolingTower", name: "CoolingTower-01", pos: Qt.vector3d(43, 6, 30),    dims: Qt.vector3d(6, 12, 6),    props: {capacity_rt: 600, cost_ntd: 1500000} },
                { id: "cooling-tower-02", type: "MEP.CoolingTower", name: "CoolingTower-02", pos: Qt.vector3d(51, 6, 30),    dims: Qt.vector3d(6, 12, 6),    props: {capacity_rt: 600, cost_ntd: 1500000} },
                { id: "cooling-tower-03", type: "MEP.CoolingTower", name: "CoolingTower-03", pos: Qt.vector3d(59, 6, 30),    dims: Qt.vector3d(6, 12, 6),    props: {capacity_rt: 600, cost_ntd: 1500000} },
                { id: "cooling-tower-04", type: "MEP.CoolingTower", name: "CoolingTower-04", pos: Qt.vector3d(67, 6, 30),    dims: Qt.vector3d(6, 12, 6),    props: {capacity_rt: 600, cost_ntd: 1500000} },
                { id: "exhaust-stack-01", type: "MEP.ExhaustStack", name: "ExhaustStack-01", pos: Qt.vector3d(-20, 17.5, -35), dims: Qt.vector3d(2, 35, 2),  props: {height_m: 35, cost_ntd: 600000} },
                { id: "exhaust-stack-02", type: "MEP.ExhaustStack", name: "ExhaustStack-02", pos: Qt.vector3d(0, 17.5, -35),   dims: Qt.vector3d(2, 35, 2),  props: {height_m: 35, cost_ntd: 600000} },
                { id: "exhaust-stack-03", type: "MEP.ExhaustStack", name: "ExhaustStack-03", pos: Qt.vector3d(20, 17.5, -35),  dims: Qt.vector3d(2, 35, 2),  props: {height_m: 35, cost_ntd: 600000} },
            ]

            for (var i = 0; i < entities.length; i++) {
                var e = entities[i]
                sceneGraph.registerEntity(e.id, e.type, e.name, e.pos, e.dims, e.props)
            }
        }
    }
}

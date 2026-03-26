import SwiftUI
import SceneKit

/// SwiftUI wrapper for SceneKit 3D preview.
/// Displays BIM models (loaded from .usda or generated geometry) in an interactive 3D view.
struct SceneKitView: NSViewRepresentable {
    @Binding var scene: SCNScene?
    var allowsCameraControl: Bool = true

    func makeNSView(context: Context) -> SCNView {
        let scnView = SCNView()
        scnView.scene = scene ?? SCNScene()
        scnView.allowsCameraControl = allowsCameraControl
        scnView.autoenablesDefaultLighting = true
        scnView.backgroundColor = NSColor(calibratedWhite: 0.15, alpha: 1.0)

        // Default camera
        let cameraNode = SCNNode()
        cameraNode.camera = SCNCamera()
        cameraNode.camera?.automaticallyAdjustsZRange = true
        cameraNode.position = SCNVector3(x: 20, y: 15, z: 30)
        cameraNode.look(at: SCNVector3(x: 0, y: 3, z: 0))
        scnView.scene?.rootNode.addChildNode(cameraNode)
        scnView.pointOfView = cameraNode

        // Add ground plane
        let floor = SCNFloor()
        floor.reflectivity = 0.05
        floor.firstMaterial?.diffuse.contents = NSColor(calibratedWhite: 0.3, alpha: 1.0)
        let floorNode = SCNNode(geometry: floor)
        scnView.scene?.rootNode.addChildNode(floorNode)

        return scnView
    }

    func updateNSView(_ nsView: SCNView, context: Context) {
        if let newScene = scene, nsView.scene !== newScene {
            // Preserve camera settings
            let existingCamera = nsView.pointOfView
            nsView.scene = newScene

            // Re-add camera and floor
            if let cam = existingCamera {
                newScene.rootNode.addChildNode(cam)
                nsView.pointOfView = cam
            }

            let floor = SCNFloor()
            floor.reflectivity = 0.05
            floor.firstMaterial?.diffuse.contents = NSColor(calibratedWhite: 0.3, alpha: 1.0)
            let floorNode = SCNNode(geometry: floor)
            newScene.rootNode.addChildNode(floorNode)
        }
    }
}

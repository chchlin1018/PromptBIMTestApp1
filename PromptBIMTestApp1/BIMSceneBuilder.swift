import SwiftUI
import SceneKit

// MARK: - BIM Scene Builder

/// Builds a SceneKit scene from building plan data (JSON).
class BIMSceneBuilder {
    /// Create a simple building from plan JSON.
    static func buildScene(fromPlanJSON json: String) -> SCNScene? {
        guard let data = json.data(using: .utf8),
              let plan = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
        else { return nil }

        let scene = SCNScene()
        let rootNode = scene.rootNode

        // Extract stories
        guard let stories = plan["stories"] as? [[String: Any]] else {
            // No stories — create a default box
            let box = SCNBox(width: 10, height: 3, length: 10, chamferRadius: 0)
            box.firstMaterial?.diffuse.contents = NSColor.systemGray
            let boxNode = SCNNode(geometry: box)
            boxNode.position = SCNVector3(0, 1.5, 0)
            rootNode.addChildNode(boxNode)
            return scene
        }

        var currentElevation: CGFloat = 0.0
        for (index, story) in stories.enumerated() {
            let height = (story["height_m"] as? Double) ?? 3.0
            let boundary = story["slab_boundary"] as? [[Double]]

            if let coords = boundary, coords.count >= 3 {
                // Create extruded floor slab from boundary
                let path = NSBezierPath()
                for (i, coord) in coords.enumerated() {
                    let point = CGPoint(x: coord[0], y: coord[1])
                    if i == 0 {
                        path.move(to: point)
                    } else {
                        path.line(to: point)
                    }
                }
                path.close()

                let shape = SCNShape(path: path, extrusionDepth: CGFloat(height))
                shape.firstMaterial?.diffuse.contents = storyColor(index: index)
                shape.firstMaterial?.transparency = 0.85

                let node = SCNNode(geometry: shape)
                // SCNShape extrudes along Z; rotate to make Y-up
                node.eulerAngles.x = -.pi / 2
                node.position.y = currentElevation

                rootNode.addChildNode(node)
            } else {
                // Fallback: simple box
                let box = SCNBox(width: 10, height: CGFloat(height), length: 10, chamferRadius: 0)
                box.firstMaterial?.diffuse.contents = storyColor(index: index)
                box.firstMaterial?.transparency = 0.85
                let boxNode = SCNNode(geometry: box)
                boxNode.position = SCNVector3(0, Float(currentElevation + height / 2.0), 0)
                rootNode.addChildNode(boxNode)
            }

            currentElevation += height
        }

        // Add axes helper
        addAxesHelper(to: rootNode)

        return scene
    }

    /// Load a .usda file into a SceneKit scene.
    static func loadUSDA(at path: String) -> SCNScene? {
        // Path injection defense: resolve symlinks and normalize
        let resolvedPath = (path as NSString).resolvingSymlinksInPath
        let allowedExtensions = ["usda", "usdz", "usd"]
        let ext = (resolvedPath as NSString).pathExtension.lowercased()
        guard allowedExtensions.contains(ext) else {
            NSLog("[BIMSceneBuilder] Rejected file with extension: \(ext)")
            return nil
        }
        let url = URL(fileURLWithPath: resolvedPath)
        guard FileManager.default.fileExists(atPath: resolvedPath) else {
            NSLog("[BIMSceneBuilder] File not found: \(resolvedPath)")
            return nil
        }

        do {
            let scene = try SCNScene(url: url, options: [
                .checkConsistency: true
            ])
            NSLog("[BIMSceneBuilder] Loaded USDA: \(path)")
            return scene
        } catch {
            NSLog("[BIMSceneBuilder] Failed to load USDA: \(error)")
            // SceneKit may not support all USDA features;
            // fall back to building from JSON if available
            return nil
        }
    }

    // MARK: - Private helpers

    private static func storyColor(index: Int) -> NSColor {
        let colors: [NSColor] = [
            .systemBlue, .systemCyan, .systemTeal,
            .systemGreen, .systemYellow, .systemOrange,
        ]
        return colors[index % colors.count]
    }

    private static func addAxesHelper(to node: SCNNode) {
        let length: CGFloat = 2.0
        let radius: CGFloat = 0.02

        // X axis (red)
        let xCyl = SCNCylinder(radius: radius, height: length)
        xCyl.firstMaterial?.diffuse.contents = NSColor.red
        let xNode = SCNNode(geometry: xCyl)
        xNode.eulerAngles.z = -.pi / 2
        xNode.position = SCNVector3(Float(length / 2), 0, 0)
        node.addChildNode(xNode)

        // Y axis (green)
        let yCyl = SCNCylinder(radius: radius, height: length)
        yCyl.firstMaterial?.diffuse.contents = NSColor.green
        let yNode = SCNNode(geometry: yCyl)
        yNode.position = SCNVector3(0, Float(length / 2), 0)
        node.addChildNode(yNode)

        // Z axis (blue)
        let zCyl = SCNCylinder(radius: radius, height: length)
        zCyl.firstMaterial?.diffuse.contents = NSColor.blue
        let zNode = SCNNode(geometry: zCyl)
        zNode.eulerAngles.x = .pi / 2
        zNode.position = SCNVector3(0, 0, Float(length / 2))
        node.addChildNode(zNode)
    }
}

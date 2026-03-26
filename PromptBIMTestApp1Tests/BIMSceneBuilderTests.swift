import XCTest
import SceneKit
@testable import PromptBIMTestApp1

final class BIMSceneBuilderTests: XCTestCase {
    func testBuildSceneFromValidJSON() {
        let json = """
        {
            "name": "TestBuilding",
            "stories": [
                {
                    "name": "1F",
                    "height_m": 3.0,
                    "slab_boundary": [[0,0],[10,0],[10,8],[0,8]]
                }
            ]
        }
        """
        let scene = BIMSceneBuilder.buildScene(fromPlanJSON: json)
        XCTAssertNotNil(scene)
        // Should have at least 1 node (story) + axes helper nodes
        XCTAssertGreaterThan(scene!.rootNode.childNodes.count, 0)
    }

    func testBuildSceneFromInvalidJSON() {
        let scene = BIMSceneBuilder.buildScene(fromPlanJSON: "not json")
        XCTAssertNil(scene)
    }

    func testBuildSceneWithNoStories() {
        let json = """
        {"name": "EmptyBuilding"}
        """
        let scene = BIMSceneBuilder.buildScene(fromPlanJSON: json)
        XCTAssertNotNil(scene)
        // Should have a fallback box node
        XCTAssertGreaterThan(scene!.rootNode.childNodes.count, 0)
    }

    func testBuildSceneMultiStory() {
        let json = """
        {
            "name": "Multi",
            "stories": [
                {"name": "1F", "height_m": 3.0},
                {"name": "2F", "height_m": 3.0},
                {"name": "3F", "height_m": 3.0}
            ]
        }
        """
        let scene = BIMSceneBuilder.buildScene(fromPlanJSON: json)
        XCTAssertNotNil(scene)
    }

    func testLoadUSDAMissingFile() {
        let scene = BIMSceneBuilder.loadUSDA(at: "/nonexistent/path.usda")
        XCTAssertNil(scene)
    }
}

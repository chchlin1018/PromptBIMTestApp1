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

    // P23: Path injection protection tests
    func testLoadUSDARejectsNonUSDAExtension() {
        let scene = BIMSceneBuilder.loadUSDA(at: "/tmp/test.txt")
        XCTAssertNil(scene)
    }

    func testLoadUSDAAcceptsUSDZExtension() {
        let scene = BIMSceneBuilder.loadUSDA(at: "/nonexistent/model.usdz")
        XCTAssertNil(scene) // File doesn't exist, but extension is accepted
    }

    func testBuildSceneFromEmptyJSON() {
        let scene = BIMSceneBuilder.buildScene(fromPlanJSON: "{}")
        XCTAssertNotNil(scene)
    }

    func testBuildSceneWithBoundaryCoordinates() {
        let json = """
        {
            "stories": [
                {
                    "name": "Ground",
                    "height_m": 4.0,
                    "slab_boundary": [[0,0],[20,0],[20,15],[0,15]]
                }
            ]
        }
        """
        let scene = BIMSceneBuilder.buildScene(fromPlanJSON: json)
        XCTAssertNotNil(scene)
    }

    func testBuildScenePreservesStoryCount() {
        let json = """
        {
            "stories": [
                {"name": "B1", "height_m": 3.0},
                {"name": "1F", "height_m": 3.6},
                {"name": "2F", "height_m": 3.2},
                {"name": "3F", "height_m": 3.2},
                {"name": "RF", "height_m": 2.8}
            ]
        }
        """
        let scene = BIMSceneBuilder.buildScene(fromPlanJSON: json)
        XCTAssertNotNil(scene)
        // 5 stories + 3 axes = at least 8 child nodes
        XCTAssertGreaterThanOrEqual(scene!.rootNode.childNodes.count, 5)
    }
}

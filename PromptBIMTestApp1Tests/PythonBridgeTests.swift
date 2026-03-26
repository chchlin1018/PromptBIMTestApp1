import XCTest
@testable import PromptBIMTestApp1

final class PythonBridgeTests: XCTestCase {
    func testFindCondaPythonReturnsPath() {
        let path = PythonBridge.findCondaPython()
        XCTAssertFalse(path.isEmpty)
        // Should always return at least /usr/bin/python3
        XCTAssertTrue(path.hasSuffix("python") || path.hasSuffix("python3"))
    }

    func testFindProjectRootReturnsURL() {
        let root = PythonBridge.findProjectRoot()
        XCTAssertFalse(root.path.isEmpty)
    }

    func testPythonBridgeInit() {
        let bridge = PythonBridge()
        XCTAssertNotNil(bridge)
        XCTAssertNotNil(bridge.statusMessage)
    }

    func testTimeoutConstant() {
        XCTAssertGreaterThan(PythonBridge.defaultTimeoutSeconds, 0)
        XCTAssertLessThanOrEqual(PythonBridge.defaultTimeoutSeconds, 300)
    }
}

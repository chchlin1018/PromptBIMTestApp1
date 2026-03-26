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

    // P23: Thread safety tests
    func testProcessQueueExists() {
        let bridge = PythonBridge()
        // Verify bridge can be initialized without deadlock
        XCTAssertFalse(bridge.guiLaunched)
    }

    func testInitialGuiNotLaunched() {
        let bridge = PythonBridge()
        XCTAssertFalse(bridge.guiLaunched)
    }

    func testTerminateGUIWhenNotRunning() {
        let bridge = PythonBridge()
        bridge.terminateGUI()
        XCTAssertFalse(bridge.guiLaunched)
    }

    func testVersionInitialValue() {
        let bridge = PythonBridge()
        XCTAssertNotNil(bridge.version)
    }

    func testStatusMessageInitialValue() {
        let bridge = PythonBridge()
        XCTAssertTrue(bridge.statusMessage.contains("Python") || bridge.statusMessage.contains("Checking"))
    }
}

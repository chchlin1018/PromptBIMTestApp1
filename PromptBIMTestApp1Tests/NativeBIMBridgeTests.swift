import XCTest
@testable import PromptBIMTestApp1

final class NativeBIMBridgeTests: XCTestCase {
    func testSharedInstanceExists() {
        let bridge = NativeBIMBridge.shared
        XCTAssertNotNil(bridge)
    }

    func testGenerateIFCWithInvalidJSON() {
        let bridge = NativeBIMBridge.shared
        // If library not loaded, should return false gracefully
        let result = bridge.generateIFC(planJSON: "not json", outputPath: "/tmp/test.ifc")
        // Either false (lib not loaded) or false (invalid JSON)
        XCTAssertFalse(result)
    }

    func testParseLandGeoJSONInvalid() {
        let bridge = NativeBIMBridge.shared
        let result = bridge.parseLandGeoJSON("not json")
        // Should return nil (not crash) even with invalid input
        // Result is nil if library not loaded or parse fails
        if bridge.isAvailable {
            XCTAssertNil(result)
        }
    }

    func testVersionNotNilWhenAvailable() {
        let bridge = NativeBIMBridge.shared
        if bridge.isAvailable {
            let ver = bridge.version()
            XCTAssertNotNil(ver)
            XCTAssertFalse(ver!.isEmpty)
        }
    }
}

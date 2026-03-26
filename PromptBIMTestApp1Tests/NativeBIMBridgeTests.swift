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

    // P22.1: PBResult integration tests
    func testGenerateIFCResultNotAvailable() {
        let bridge = NativeBIMBridge.shared
        if !bridge.isAvailable {
            let result = bridge.generateIFCResult(planJSON: "{}", outputPath: "/tmp/test.ifc")
            XCTAssertFalse(result.success)
            XCTAssertNotNil(result.error)
            if case .libraryNotLoaded = result.error {
                // Expected
            } else {
                XCTFail("Expected libraryNotLoaded error")
            }
        }
    }

    func testGenerateUSDResultNotAvailable() {
        let bridge = NativeBIMBridge.shared
        if !bridge.isAvailable {
            let result = bridge.generateUSDResult(planJSON: "{}", outputPath: "/tmp/test.usda")
            XCTAssertFalse(result.success)
            XCTAssertNotNil(result.error)
        }
    }

    func testGenerateIFCResultInvalidJSON() {
        let bridge = NativeBIMBridge.shared
        let result = bridge.generateIFCResult(planJSON: "not json", outputPath: "/tmp/test.ifc")
        XCTAssertFalse(result.success)
        // Either libraryNotLoaded or invalidInput
        XCTAssertNotNil(result.error)
    }

    func testGenerateIFCBoolBackwardsCompat() {
        let bridge = NativeBIMBridge.shared
        // Bool wrapper should match PBResult
        let boolResult = bridge.generateIFC(planJSON: "not json", outputPath: "/tmp/test.ifc")
        let pbResult = bridge.generateIFCResult(planJSON: "not json", outputPath: "/tmp/test.ifc")
        XCTAssertEqual(boolResult, pbResult.success)
    }

    func testGenerateUSDResultInvalidJSON() {
        let bridge = NativeBIMBridge.shared
        let result = bridge.generateUSDResult(planJSON: "not json", outputPath: "/tmp/test.usda")
        XCTAssertFalse(result.success)
        XCTAssertNotNil(result.error)
    }
}

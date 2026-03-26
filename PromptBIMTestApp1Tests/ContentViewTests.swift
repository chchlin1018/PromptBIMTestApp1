import XCTest
@testable import PromptBIMTestApp1

final class ContentViewTests: XCTestCase {
    func testAppThemeRawValues() {
        XCTAssertEqual(AppTheme.system.rawValue, "system")
        XCTAssertEqual(AppTheme.light.rawValue, "light")
        XCTAssertEqual(AppTheme.dark.rawValue, "dark")
    }

    func testAppThemeLabels() {
        XCTAssertEqual(AppTheme.system.label, "System")
        XCTAssertEqual(AppTheme.light.label, "Light")
        XCTAssertEqual(AppTheme.dark.label, "Dark")
    }

    func testAppThemeColorScheme() {
        XCTAssertNil(AppTheme.system.colorScheme)
        XCTAssertNotNil(AppTheme.light.colorScheme)
        XCTAssertNotNil(AppTheme.dark.colorScheme)
    }

    func testAppThemeIcons() {
        XCTAssertFalse(AppTheme.system.icon.isEmpty)
        XCTAssertFalse(AppTheme.light.icon.isEmpty)
        XCTAssertFalse(AppTheme.dark.icon.isEmpty)
    }

    func testAppThemeAllCases() {
        XCTAssertEqual(AppTheme.allCases.count, 3)
    }

    func testPipelineStepStatuses() {
        var step = PipelineStep(name: "Test", icon: "circle", status: .pending)
        XCTAssertEqual(step.name, "Test")

        step.status = .running
        step.status = .completed
        step.status = .failed
        // Just verify no crash
    }
}

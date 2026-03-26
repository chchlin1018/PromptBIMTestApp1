import XCTest
@testable import PromptBIMTestApp1

final class PBResultTests: XCTestCase {
    func testOkResult() {
        let result = PBResult<String>.ok("hello")
        XCTAssertTrue(result.success)
        XCTAssertEqual(result.value, "hello")
        XCTAssertNil(result.error)
    }

    func testFailResult() {
        let result = PBResult<String>.fail(.libraryNotLoaded)
        XCTAssertFalse(result.success)
        XCTAssertNil(result.value)
        XCTAssertNotNil(result.error)
    }

    func testErrorDescriptions() {
        XCTAssertNotNil(PBError.libraryNotLoaded.errorDescription)
        XCTAssertNotNil(PBError.symbolMissing("test").errorDescription)
        XCTAssertNotNil(PBError.generationFailed("reason").errorDescription)
        XCTAssertNotNil(PBError.timeout(30).errorDescription)
        XCTAssertNotNil(PBError.pythonError("err").errorDescription)
        XCTAssertNotNil(PBError.invalidInput("bad").errorDescription)
    }
}

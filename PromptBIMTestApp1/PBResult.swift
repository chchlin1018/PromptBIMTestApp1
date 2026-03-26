import Foundation

/// Cross-layer result type for PromptBIM operations.
/// Provides structured error propagation from C++ -> Swift -> UI.
struct PBResult<T> {
    let success: Bool
    let value: T?
    let error: PBError?

    static func ok(_ value: T) -> PBResult<T> {
        PBResult(success: true, value: value, error: nil)
    }

    static func fail(_ error: PBError) -> PBResult<T> {
        PBResult(success: false, value: nil, error: error)
    }
}

enum PBError: Error, LocalizedError {
    case libraryNotLoaded
    case symbolMissing(String)
    case generationFailed(String)
    case timeout(TimeInterval)
    case pythonError(String)
    case invalidInput(String)

    var errorDescription: String? {
        switch self {
        case .libraryNotLoaded: return "Native library not loaded"
        case .symbolMissing(let sym): return "Missing symbol: \(sym)"
        case .generationFailed(let msg): return "Generation failed: \(msg)"
        case .timeout(let t): return "Operation timed out after \(t)s"
        case .pythonError(let msg): return "Python error: \(msg)"
        case .invalidInput(let msg): return "Invalid input: \(msg)"
        }
    }
}

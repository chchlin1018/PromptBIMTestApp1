import Foundation

/// Swift bridge to libpromptbim C ABI.
/// Provides direct access to C++ BIM/GIS engines via C function calls.
///
/// This replaces the Python subprocess approach for BIM generation,
/// enabling native performance on macOS.
class NativeBIMBridge {
    /// Shared singleton instance
    static let shared = NativeBIMBridge()

    /// Whether the native library is available
    private(set) var isAvailable: Bool = false

    /// Dynamic library handle
    private var libHandle: UnsafeMutableRawPointer?

    // C function pointers
    private var _pb_version: (@convention(c) () -> UnsafePointer<CChar>?)?
    private var _pb_free_string: (@convention(c) (UnsafeMutablePointer<CChar>?) -> Void)?
    private var _pb_plan_from_json: (@convention(c) (UnsafePointer<CChar>?) -> OpaquePointer?)?
    private var _pb_plan_free: (@convention(c) (OpaquePointer?) -> Void)?
    private var _pb_plan_to_json: (@convention(c) (OpaquePointer?) -> UnsafeMutablePointer<CChar>?)?
    private var _pb_generate_ifc: (@convention(c) (OpaquePointer?, UnsafePointer<CChar>?) -> Int32)?
    private var _pb_generate_usd: (@convention(c) (OpaquePointer?, UnsafePointer<CChar>?) -> Int32)?
    private var _pb_generate_usdz: (@convention(c) (UnsafePointer<CChar>?, UnsafePointer<CChar>?) -> Int32)?
    private var _pb_land_from_geojson_string: (@convention(c) (UnsafePointer<CChar>?) -> OpaquePointer?)?
    private var _pb_land_to_json: (@convention(c) (OpaquePointer?) -> UnsafeMutablePointer<CChar>?)?
    private var _pb_land_free: (@convention(c) (OpaquePointer?) -> Void)?
    private var _pb_check_compliance: (@convention(c) (UnsafePointer<CChar>?, UnsafePointer<CChar>?, UnsafePointer<CChar>?) -> UnsafeMutablePointer<CChar>?)?
    private var _pb_estimate_cost: (@convention(c) (UnsafePointer<CChar>?) -> UnsafeMutablePointer<CChar>?)?

    private init() {
        loadLibrary()
    }

    deinit {
        if let handle = libHandle {
            dlclose(handle)
        }
    }

    // MARK: - Library Loading

    private func loadLibrary() {
        let candidates = findLibraryCandidates()

        for path in candidates {
            if let handle = dlopen(path, RTLD_NOW | RTLD_LOCAL) {
                libHandle = handle
                bindFunctions(handle)
                isAvailable = true
                NSLog("[NativeBIMBridge] Loaded libpromptbim from: \(path)")
                if let ver = version() {
                    NSLog("[NativeBIMBridge] Version: \(ver)")
                }
                return
            }
        }

        NSLog("[NativeBIMBridge] libpromptbim not found — native BIM disabled")
    }

    private func findLibraryCandidates() -> [String] {
        var candidates: [String] = []

        // Search relative to app bundle
        if let bundlePath = Bundle.main.resourceURL {
            var url = bundlePath
            for _ in 0..<6 {
                url = url.deletingLastPathComponent()
                let libPath = url.appendingPathComponent("libpromptbim/build/libpromptbim.dylib").path
                if FileManager.default.fileExists(atPath: libPath) {
                    candidates.append(libPath)
                }
            }
        }

        // Search from working directory
        let cwd = FileManager.default.currentDirectoryPath
        candidates.append("\(cwd)/libpromptbim/build/libpromptbim.dylib")

        // Well-known project paths
        let home = NSHomeDirectory()
        candidates.append("\(home)/Documents/MyProjects/PromptBIMTestApp1/libpromptbim/build/libpromptbim.dylib")

        return candidates
    }

    private func bindFunctions(_ handle: UnsafeMutableRawPointer) {
        _pb_version = unsafeBitCast(dlsym(handle, "pb_version"), to: (@convention(c) () -> UnsafePointer<CChar>?).self)
        _pb_free_string = unsafeBitCast(dlsym(handle, "pb_free_string"), to: (@convention(c) (UnsafeMutablePointer<CChar>?) -> Void).self)
        _pb_plan_from_json = unsafeBitCast(dlsym(handle, "pb_plan_from_json"), to: (@convention(c) (UnsafePointer<CChar>?) -> OpaquePointer?).self)
        _pb_plan_free = unsafeBitCast(dlsym(handle, "pb_plan_free"), to: (@convention(c) (OpaquePointer?) -> Void).self)
        _pb_plan_to_json = unsafeBitCast(dlsym(handle, "pb_plan_to_json"), to: (@convention(c) (OpaquePointer?) -> UnsafeMutablePointer<CChar>?).self)
        _pb_generate_ifc = unsafeBitCast(dlsym(handle, "pb_generate_ifc"), to: (@convention(c) (OpaquePointer?, UnsafePointer<CChar>?) -> Int32).self)
        _pb_generate_usd = unsafeBitCast(dlsym(handle, "pb_generate_usd"), to: (@convention(c) (OpaquePointer?, UnsafePointer<CChar>?) -> Int32).self)
        _pb_generate_usdz = unsafeBitCast(dlsym(handle, "pb_generate_usdz"), to: (@convention(c) (UnsafePointer<CChar>?, UnsafePointer<CChar>?) -> Int32).self)
        _pb_land_from_geojson_string = unsafeBitCast(dlsym(handle, "pb_land_from_geojson_string"), to: (@convention(c) (UnsafePointer<CChar>?) -> OpaquePointer?).self)
        _pb_land_to_json = unsafeBitCast(dlsym(handle, "pb_land_to_json"), to: (@convention(c) (OpaquePointer?) -> UnsafeMutablePointer<CChar>?).self)
        _pb_land_free = unsafeBitCast(dlsym(handle, "pb_land_free"), to: (@convention(c) (OpaquePointer?) -> Void).self)
        _pb_check_compliance = unsafeBitCast(dlsym(handle, "pb_check_compliance"), to: (@convention(c) (UnsafePointer<CChar>?, UnsafePointer<CChar>?, UnsafePointer<CChar>?) -> UnsafeMutablePointer<CChar>?).self)
        _pb_estimate_cost = unsafeBitCast(dlsym(handle, "pb_estimate_cost"), to: (@convention(c) (UnsafePointer<CChar>?) -> UnsafeMutablePointer<CChar>?).self)
    }

    // MARK: - Public API

    func version() -> String? {
        guard let fn = _pb_version, let cstr = fn() else { return nil }
        return String(cString: cstr)
    }

    /// Generate an IFC file from a building plan JSON.
    func generateIFC(planJSON: String, outputPath: String) -> Bool {
        guard let fromJSON = _pb_plan_from_json,
              let genIFC = _pb_generate_ifc,
              let planFree = _pb_plan_free
        else { return false }

        guard let plan = fromJSON(planJSON) else {
            NSLog("[NativeBIMBridge] Failed to parse plan JSON")
            return false
        }
        defer { planFree(plan) }

        let result = genIFC(plan, outputPath)
        return result == 0
    }

    /// Generate a USDA file from a building plan JSON.
    func generateUSD(planJSON: String, outputPath: String) -> Bool {
        guard let fromJSON = _pb_plan_from_json,
              let genUSD = _pb_generate_usd,
              let planFree = _pb_plan_free
        else { return false }

        guard let plan = fromJSON(planJSON) else {
            NSLog("[NativeBIMBridge] Failed to parse plan JSON")
            return false
        }
        defer { planFree(plan) }

        let result = genUSD(plan, outputPath)
        return result == 0
    }

    /// Generate a USDZ file from a USDA file.
    func generateUSDZ(usdPath: String, outputPath: String) -> Bool {
        guard let genUSDZ = _pb_generate_usdz else { return false }
        return genUSDZ(usdPath, outputPath) == 0
    }

    /// Parse GeoJSON string and return land parcel JSON.
    func parseLandGeoJSON(_ geojsonStr: String) -> String? {
        guard let parse = _pb_land_from_geojson_string,
              let toJSON = _pb_land_to_json,
              let free = _pb_land_free,
              let freeStr = _pb_free_string
        else { return nil }

        guard let parcel = parse(geojsonStr) else { return nil }
        defer { free(parcel) }

        guard let jsonPtr = toJSON(parcel) else { return nil }
        let result = String(cString: jsonPtr)
        freeStr(jsonPtr)
        return result
    }

    /// Run compliance check. Returns JSON string with results.
    func checkCompliance(planJSON: String, landJSON: String, zoningJSON: String) -> String? {
        guard let fn = _pb_check_compliance,
              let freeStr = _pb_free_string
        else { return nil }

        guard let resultPtr = fn(planJSON, landJSON, zoningJSON) else { return nil }
        let result = String(cString: resultPtr)
        freeStr(resultPtr)
        return result
    }

    /// Estimate construction cost. Returns JSON string.
    func estimateCost(planJSON: String) -> String? {
        guard let fn = _pb_estimate_cost,
              let freeStr = _pb_free_string
        else { return nil }

        guard let resultPtr = fn(planJSON) else { return nil }
        let result = String(cString: resultPtr)
        freeStr(resultPtr)
        return result
    }
}

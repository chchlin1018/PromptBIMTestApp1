import Foundation
import Combine

/// Bridges Swift UI to the Python backend via Process().
/// Launches the PySide6 GUI and manages the Python process lifecycle.
class PythonBridge: ObservableObject {
    @Published var pythonAvailable: Bool = false
    @Published var statusMessage: String = "Checking Python environment..."
    @Published var guiLaunched: Bool = false
    @Published var version: String = "..."

    private let pythonPath: String
    private var guiProcess: Process?
    private let projectRoot: URL
    private let processQueue = DispatchQueue(label: "com.promptbim.pythonbridge.process")

    init() {
        self.projectRoot = PythonBridge.findProjectRoot()
        self.pythonPath = PythonBridge.findCondaPython()
        NSLog("[PythonBridge] init — single instance created (python: \(self.pythonPath))")
        checkPython()
    }

    // MARK: - Python Environment Detection

    /// Auto-detect conda promptbim environment Python path.
    /// Priority: PROMPTBIM_PYTHON env var > miniforge3 > miniconda3 > which python3 > system python
    static func findCondaPython() -> String {
        // 1. Environment variable override
        if let envPython = ProcessInfo.processInfo.environment["PROMPTBIM_PYTHON"],
           FileManager.default.fileExists(atPath: envPython) {
            NSLog("[PythonBridge] Using PROMPTBIM_PYTHON override: \(envPython)")
            return envPython
        }

        let home = NSHomeDirectory()
        let candidates = [
            // Apple Silicon paths
            "\(home)/miniforge3/envs/promptbim/bin/python",
            "\(home)/miniconda3/envs/promptbim/bin/python",
            "/opt/homebrew/Caskroom/miniforge/base/envs/promptbim/bin/python",
            "\(home)/anaconda3/envs/promptbim/bin/python",
            // Intel Mac paths
            "/usr/local/Caskroom/miniforge/base/envs/promptbim/bin/python",
            "/usr/local/miniconda3/envs/promptbim/bin/python",
            "\(home)/opt/miniconda3/envs/promptbim/bin/python",
            "\(home)/opt/anaconda3/envs/promptbim/bin/python",
        ]
        if let found = candidates.first(where: { FileManager.default.fileExists(atPath: $0) }) {
            return found
        }

        // Fallback: which python3
        let whichProcess = Process()
        whichProcess.executableURL = URL(fileURLWithPath: "/usr/bin/which")
        whichProcess.arguments = ["python3"]
        let pipe = Pipe()
        whichProcess.standardOutput = pipe
        do {
            try whichProcess.run()
            whichProcess.waitUntilExit()
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            if let path = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines),
               !path.isEmpty,
               FileManager.default.fileExists(atPath: path) {
                NSLog("[PythonBridge] Using which python3 fallback: \(path)")
                return path
            }
        } catch {
            NSLog("[PythonBridge] which python3 failed: \(error)")
        }

        return "/usr/bin/python3"
    }

    /// Find the project root directory from Bundle or working directory.
    static func findProjectRoot() -> URL {
        // Try 1: Look for pyproject.toml relative to the app bundle
        if let bundlePath = Bundle.main.resourceURL {
            // App bundle is at PromptBIMTestApp1.app/Contents/Resources
            // Project root is typically 3-5 levels up
            var url = bundlePath
            for _ in 0..<6 {
                url = url.deletingLastPathComponent()
                let pyproject = url.appendingPathComponent("pyproject.toml")
                if FileManager.default.fileExists(atPath: pyproject.path) {
                    return url
                }
            }
        }

        // Try 2: Check the current working directory
        let cwd = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        let cwdPyproject = cwd.appendingPathComponent("pyproject.toml")
        if FileManager.default.fileExists(atPath: cwdPyproject.path) {
            return cwd
        }

        // Try 3: Well-known project paths (including macOS lowercase variants)
        let home = NSHomeDirectory()
        let knownPaths = [
            "\(home)/Documents/MyProjects/PromptBIMTestApp1",
            "\(home)/documents/myprojects/PromptBIMTestApp1",
        ]
        for path in knownPaths {
            let knownURL = URL(fileURLWithPath: path)
            let knownPyproject = knownURL.appendingPathComponent("pyproject.toml")
            if FileManager.default.fileExists(atPath: knownPyproject.path) {
                return knownURL
            }
        }

        // Fallback to current directory
        return cwd
    }

    // MARK: - .env Loading

    /// Load .env file and parse key=value pairs into a dictionary.
    func loadDotEnv() -> [String: String]? {
        let home = NSHomeDirectory()
        let candidates = [
            projectRoot.appendingPathComponent(".env"),
            URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
                .appendingPathComponent(".env"),
            URL(fileURLWithPath: "\(home)/Documents/MyProjects/PromptBIMTestApp1/.env"),
            URL(fileURLWithPath: "\(home)/documents/myprojects/PromptBIMTestApp1/.env"),
        ]

        for url in candidates {
            if let contents = try? String(contentsOf: url, encoding: .utf8) {
                // Check file permissions — warn if world-readable
                let fm = FileManager.default
                if let attrs = try? fm.attributesOfItem(atPath: url.path),
                   let posix = attrs[.posixPermissions] as? NSNumber {
                    let mode = posix.int16Value
                    if mode & 0o044 != 0 {
                        NSLog("[PythonBridge] ⚠️ .env file at \(url.path) is readable by group/others. Run: chmod 600 \(url.path)")
                    }
                }
                var dict = [String: String]()
                for line in contents.components(separatedBy: .newlines) {
                    let trimmed = line.trimmingCharacters(in: .whitespaces)
                    if trimmed.isEmpty || trimmed.hasPrefix("#") { continue }
                    let parts = trimmed.split(separator: "=", maxSplits: 1)
                    if parts.count == 2 {
                        let key = String(parts[0]).trimmingCharacters(in: .whitespaces)
                        var value = String(parts[1]).trimmingCharacters(in: .whitespaces)
                        // Remove surrounding quotes
                        if (value.hasPrefix("\"") && value.hasSuffix("\"")) ||
                           (value.hasPrefix("'") && value.hasSuffix("'")) {
                            value = String(value.dropFirst().dropLast())
                        }
                        dict[key] = value
                    }
                }
                return dict
            }
        }
        return nil
    }

    // MARK: - Python Check

    func checkPython() {
        runCommand(arguments: ["-m", "promptbim", "--version"]) { [weak self] result in
            DispatchQueue.main.async {
                if let output = result, !output.isEmpty {
                    self?.pythonAvailable = true
                    let trimmed = output.trimmingCharacters(in: .whitespacesAndNewlines)
                    self?.statusMessage = "Python backend ready: \(trimmed)"
                    // Parse version from output like "promptbim 2.4.0"
                    let parts = trimmed.components(separatedBy: " ")
                    if parts.count >= 2 {
                        self?.version = parts.last ?? trimmed
                    } else {
                        self?.version = trimmed
                    }
                } else {
                    self?.pythonAvailable = false
                    self?.version = "N/A"
                    self?.statusMessage = "Python backend not available. Run: conda activate promptbim && pip install -e ."
                }
            }
        }
    }

    // MARK: - PySide6 GUI Launch

    /// Launch the PySide6 GUI as a subprocess.
    func launchPySide6GUI() {
        processQueue.sync {
            guard guiProcess == nil || !(guiProcess?.isRunning ?? false) else {
                DispatchQueue.main.async { self.statusMessage = "PySide6 GUI is already running" }
                return
            }
        }

        DispatchQueue.global(qos: .userInitiated).async { [self] in
            let process = Process()
            process.executableURL = URL(fileURLWithPath: pythonPath)
            process.arguments = ["-m", "promptbim", "gui"]
            process.currentDirectoryURL = projectRoot

            // Build environment with .env variables
            var env = ProcessInfo.processInfo.environment
            if let dotenv = loadDotEnv() {
                for (key, value) in dotenv {
                    env[key] = value
                }
            }
            env["PROMPTBIM_DEBUG"] = "1"
            // Ensure Python can find the src package
            let srcPath = projectRoot.appendingPathComponent("src").path
            if let existing = env["PYTHONPATH"] {
                env["PYTHONPATH"] = "\(srcPath):\(existing)"
            } else {
                env["PYTHONPATH"] = srcPath
            }
            process.environment = env

            let errorPipe = Pipe()
            process.standardError = errorPipe

            process.terminationHandler = { [weak self] proc in
                // SW-02 fix: Always re-enable sudden termination when process ends
                ProcessInfo.processInfo.enableSuddenTermination()
                self?.processQueue.sync { self?.guiProcess = nil }
                DispatchQueue.main.async {
                    self?.guiLaunched = false
                    if proc.terminationStatus != 0 {
                        // Read stderr for error info
                        let errData = errorPipe.fileHandleForReading.readDataToEndOfFile()
                        let errStr = String(data: errData, encoding: .utf8) ?? ""
                        self?.statusMessage = "PySide6 GUI exited (code \(proc.terminationStatus)): \(errStr.prefix(200))"
                    } else {
                        self?.statusMessage = "PySide6 GUI closed"
                    }
                }
            }

            do {
                ProcessInfo.processInfo.disableSuddenTermination()
                try process.run()
                self.processQueue.sync { self.guiProcess = process }
                DispatchQueue.main.async {
                    self.guiLaunched = true
                    self.statusMessage = "PySide6 GUI launched"
                }
            } catch {
                // SW-02 fix: Always re-enable sudden termination on failure
                ProcessInfo.processInfo.enableSuddenTermination()
                DispatchQueue.main.async {
                    self.statusMessage = "Failed to launch PySide6 GUI: \(error.localizedDescription)"
                }
            }
        }
    }

    /// Terminate the PySide6 GUI process.
    func terminateGUI() {
        processQueue.sync {
            if let process = guiProcess, process.isRunning {
                process.terminate()
                guiProcess = nil
                DispatchQueue.main.async {
                    self.guiLaunched = false
                    self.statusMessage = "PySide6 GUI terminated"
                }
                ProcessInfo.processInfo.enableSuddenTermination()
            }
        }
    }

    // MARK: - Command Execution

    /// Default subprocess timeout in seconds (SW-01 fix: prevent indefinite hangs).
    static let defaultTimeoutSeconds: TimeInterval = 60.0

    func runCommand(arguments: [String], timeout: TimeInterval = PythonBridge.defaultTimeoutSeconds, completion: @escaping (String?) -> Void) {
        DispatchQueue.global(qos: .userInitiated).async { [pythonPath] in
            let process = Process()
            process.executableURL = URL(fileURLWithPath: pythonPath)
            process.arguments = arguments

            let stdoutPipe = Pipe()
            let stderrPipe = Pipe()
            process.standardOutput = stdoutPipe
            process.standardError = stderrPipe

            do {
                try process.run()

                // QA-08 fix: Read pipe asynchronously BEFORE waiting for exit
                // to prevent deadlock when output exceeds pipe buffer (~64KB).
                var stdoutData = Data()
                var stderrData = Data()
                let readGroup = DispatchGroup()

                readGroup.enter()
                DispatchQueue.global().async {
                    stdoutData = stdoutPipe.fileHandleForReading.readDataToEndOfFile()
                    readGroup.leave()
                }
                readGroup.enter()
                DispatchQueue.global().async {
                    stderrData = stderrPipe.fileHandleForReading.readDataToEndOfFile()
                    readGroup.leave()
                }

                // SW-01 fix: Timeout-guarded wait to prevent indefinite hang
                let deadline = DispatchTime.now() + timeout
                let waitGroup = DispatchGroup()
                waitGroup.enter()
                DispatchQueue.global().async {
                    process.waitUntilExit()
                    waitGroup.leave()
                }
                let result = waitGroup.wait(timeout: deadline)
                if result == .timedOut {
                    NSLog("[PythonBridge] Process timed out after \(timeout)s, terminating")
                    process.terminate()
                    completion(nil)
                    return
                }

                // Wait for pipe reads to finish
                readGroup.wait()

                let output = String(data: stdoutData, encoding: .utf8)
                completion(output)
            } catch {
                completion(nil)
            }
        }
    }

    func generateBuilding(prompt: String, landFile: String? = nil, completion: @escaping (String?) -> Void) {
        var args = ["-m", "promptbim", "generate", prompt]
        if let land = landFile {
            args.insert(contentsOf: ["--land", land], at: 3)
        }
        runCommand(arguments: args, completion: completion)
    }

    func getVersion(completion: @escaping (String?) -> Void) {
        runCommand(arguments: ["-m", "promptbim", "--version"], completion: completion)
    }
}

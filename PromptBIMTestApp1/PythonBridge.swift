import Foundation
import Combine

/// Bridges Swift UI to the Python backend via Process().
/// Launches the PySide6 GUI and manages the Python process lifecycle.
class PythonBridge: ObservableObject {
    @Published var pythonAvailable: Bool = false
    @Published var statusMessage: String = "Checking Python environment..."
    @Published var guiLaunched: Bool = false

    private let pythonPath: String
    private var guiProcess: Process?
    private let projectRoot: URL

    init() {
        self.projectRoot = PythonBridge.findProjectRoot()
        self.pythonPath = PythonBridge.findCondaPython()
        checkPython()
    }

    // MARK: - Python Environment Detection

    /// Auto-detect conda promptbim environment Python path.
    /// Priority: miniforge3 > miniconda3 > system python
    static func findCondaPython() -> String {
        let home = NSHomeDirectory()
        let candidates = [
            "\(home)/miniforge3/envs/promptbim/bin/python",
            "\(home)/miniconda3/envs/promptbim/bin/python",
            "/opt/homebrew/Caskroom/miniforge/base/envs/promptbim/bin/python",
            "\(home)/anaconda3/envs/promptbim/bin/python",
        ]
        return candidates.first { FileManager.default.fileExists(atPath: $0) }
            ?? "/usr/bin/python3"
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

        // Try 3: Well-known project path
        let home = NSHomeDirectory()
        let knownPath = URL(fileURLWithPath: "\(home)/Documents/MyProjects/PromptBIMTestApp1")
        let knownPyproject = knownPath.appendingPathComponent("pyproject.toml")
        if FileManager.default.fileExists(atPath: knownPyproject.path) {
            return knownPath
        }

        // Fallback to current directory
        return cwd
    }

    // MARK: - .env Loading

    /// Load .env file and parse key=value pairs into a dictionary.
    func loadDotEnv() -> [String: String]? {
        let candidates = [
            projectRoot.appendingPathComponent(".env"),
            URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
                .appendingPathComponent(".env"),
            URL(fileURLWithPath: NSHomeDirectory())
                .appendingPathComponent("Documents/MyProjects/PromptBIMTestApp1/.env"),
        ]

        for url in candidates {
            if let contents = try? String(contentsOf: url, encoding: .utf8) {
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
                    self?.statusMessage = "Python backend ready: \(output.trimmingCharacters(in: .whitespacesAndNewlines))"
                } else {
                    self?.pythonAvailable = false
                    self?.statusMessage = "Python backend not available. Run: conda activate promptbim && pip install -e ."
                }
            }
        }
    }

    // MARK: - PySide6 GUI Launch

    /// Launch the PySide6 GUI as a subprocess.
    func launchPySide6GUI() {
        guard guiProcess == nil || !(guiProcess?.isRunning ?? false) else {
            statusMessage = "PySide6 GUI is already running"
            return
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
            let pythonPath = projectRoot.appendingPathComponent("src").path
            if let existing = env["PYTHONPATH"] {
                env["PYTHONPATH"] = "\(pythonPath):\(existing)"
            } else {
                env["PYTHONPATH"] = pythonPath
            }
            process.environment = env

            let errorPipe = Pipe()
            process.standardError = errorPipe

            process.terminationHandler = { [weak self] proc in
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
                try process.run()
                DispatchQueue.main.async {
                    self.guiProcess = process
                    self.guiLaunched = true
                    self.statusMessage = "PySide6 GUI launched"
                }
            } catch {
                DispatchQueue.main.async {
                    self.statusMessage = "Failed to launch PySide6 GUI: \(error.localizedDescription)"
                }
            }
        }
    }

    /// Terminate the PySide6 GUI process.
    func terminateGUI() {
        if let process = guiProcess, process.isRunning {
            process.terminate()
            guiProcess = nil
            guiLaunched = false
            statusMessage = "PySide6 GUI terminated"
        }
    }

    // MARK: - Command Execution

    func runCommand(arguments: [String], completion: @escaping (String?) -> Void) {
        DispatchQueue.global(qos: .userInitiated).async { [pythonPath] in
            let process = Process()
            process.executableURL = URL(fileURLWithPath: pythonPath)
            process.arguments = arguments

            let pipe = Pipe()
            process.standardOutput = pipe
            process.standardError = pipe

            do {
                try process.run()
                process.waitUntilExit()
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                let output = String(data: data, encoding: .utf8)
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

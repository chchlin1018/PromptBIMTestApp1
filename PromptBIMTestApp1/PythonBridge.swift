import Foundation
import Combine

/// Bridges Swift UI to the Python backend via Process().
/// Calls `python -m promptbim` subcommands and parses output.
class PythonBridge: ObservableObject {
    @Published var pythonAvailable: Bool = false
    @Published var statusMessage: String = "Checking Python environment..."

    private let pythonPath: String

    init() {
        // Try to find python in conda promptbim environment
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        let condaPython = "\(home)/miniforge3/envs/promptbim/bin/python"
        if FileManager.default.fileExists(atPath: condaPython) {
            self.pythonPath = condaPython
        } else {
            self.pythonPath = "/usr/bin/python3"
        }
        checkPython()
    }

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

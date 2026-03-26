import SwiftUI
import SceneKit

struct ContentView: View {
    @EnvironmentObject var bridge: PythonBridge
    @State private var selectedTab = 0
    @State private var scene: SCNScene? = nil
    @State private var isGenerating = false
    @State private var generationStatus = ""
    @State private var nativeBridge = NativeBIMBridge.shared

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Image(systemName: "building.2")
                    .font(.title)
                Text("PromptBIM")
                    .font(.title)
                    .fontWeight(.bold)
                Text("AI-Powered BIM Generator")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                Spacer()
                if nativeBridge.isAvailable {
                    Text("C++")
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.green.opacity(0.2))
                        .cornerRadius(4)
                        .foregroundColor(.green)
                }
                Text("v\(bridge.version)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()

            Divider()

            // Tab bar
            HStack(spacing: 0) {
                tabButton(title: "Dashboard", icon: "house", index: 0)
                tabButton(title: "3D Preview", icon: "cube", index: 1)
            }
            .padding(.horizontal)
            .padding(.top, 4)

            Divider()

            // Tab content
            if selectedTab == 0 {
                dashboardView
            } else {
                preview3DView
            }

            Divider()

            // Status bar
            HStack {
                Text(bridge.statusMessage)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
                Spacer()
                Circle()
                    .fill(bridge.pythonAvailable ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                Text("Python: \(bridge.pythonAvailable ? "Connected" : "Not Found")")
                    .font(.caption)
                    .foregroundColor(bridge.pythonAvailable ? .green : .red)
                if nativeBridge.isAvailable {
                    Circle()
                        .fill(Color.green)
                        .frame(width: 8, height: 8)
                    Text("C++: v\(nativeBridge.version() ?? "?")")
                        .font(.caption)
                        .foregroundColor(.green)
                }
                if bridge.guiLaunched {
                    Circle()
                        .fill(Color.blue)
                        .frame(width: 8, height: 8)
                    Text("GUI: Running")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }
            .padding(.horizontal)
            .padding(.bottom, 4)
        }
    }

    // MARK: - Tab Button

    private func tabButton(title: String, icon: String, index: Int) -> some View {
        Button(action: { selectedTab = index }) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                Text(title)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(selectedTab == index ? Color.accentColor.opacity(0.15) : Color.clear)
            .cornerRadius(6)
        }
        .buttonStyle(.plain)
        .foregroundColor(selectedTab == index ? .accentColor : .secondary)
    }

    // MARK: - Dashboard View (original content)

    private var dashboardView: some View {
        Group {
            if bridge.guiLaunched {
                VStack(spacing: 20) {
                    Spacer()
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 48))
                        .foregroundColor(.green)
                    Text("PySide6 GUI is running")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("The full PromptBIM interface is open in a separate window.")
                        .foregroundColor(.secondary)
                    Text("You can close this window or keep it open for status monitoring.")
                        .foregroundColor(.secondary)
                        .font(.caption)
                    Button("Restart GUI") {
                        bridge.terminateGUI()
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                            bridge.launchPySide6GUI()
                        }
                    }
                    .buttonStyle(.bordered)
                    Spacer()
                }
                .frame(maxWidth: .infinity)
            } else if !bridge.pythonAvailable {
                VStack(spacing: 16) {
                    Spacer()
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 48))
                        .foregroundColor(.orange)
                    Text("Python Environment Not Found")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("PromptBIM requires a conda environment named 'promptbim'.")
                        .foregroundColor(.secondary)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Setup steps:")
                            .fontWeight(.semibold)
                        Text("1. Install Miniforge: brew install miniforge")
                            .font(.system(.body, design: .monospaced))
                        Text("2. conda create -n promptbim python=3.11 -y")
                            .font(.system(.body, design: .monospaced))
                        Text("3. conda activate promptbim")
                            .font(.system(.body, design: .monospaced))
                        Text("4. pip install -e .")
                            .font(.system(.body, design: .monospaced))
                        Text("5. See SETUP.md for full instructions")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
                    Button("Retry") {
                        bridge.checkPython()
                    }
                    .buttonStyle(.borderedProminent)
                    Spacer()
                }
                .frame(maxWidth: .infinity)
                .padding()
            } else {
                VStack(spacing: 20) {
                    Spacer()
                    ProgressView()
                        .scaleEffect(1.5)
                    Text("PromptBIM is starting...")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("Launching PySide6 GUI...")
                        .foregroundColor(.secondary)
                    Spacer()
                }
                .frame(maxWidth: .infinity)
                .onAppear {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                        if bridge.pythonAvailable && !bridge.guiLaunched {
                            bridge.launchPySide6GUI()
                        }
                    }
                }
            }
        }
    }

    // MARK: - 3D Preview View

    private var preview3DView: some View {
        VStack(spacing: 0) {
            // Toolbar
            HStack {
                Button(action: generateSampleBuilding) {
                    HStack(spacing: 4) {
                        Image(systemName: "plus.cube")
                        Text("Generate Sample")
                    }
                }
                .buttonStyle(.bordered)
                .disabled(isGenerating)

                Button(action: loadUSDAFile) {
                    HStack(spacing: 4) {
                        Image(systemName: "doc.badge.plus")
                        Text("Load USDA")
                    }
                }
                .buttonStyle(.bordered)

                Button(action: { scene = nil }) {
                    HStack(spacing: 4) {
                        Image(systemName: "trash")
                        Text("Clear")
                    }
                }
                .buttonStyle(.bordered)
                .disabled(scene == nil)

                Spacer()

                if isGenerating {
                    ProgressView()
                        .scaleEffect(0.7)
                    Text(generationStatus)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(8)

            // 3D View
            SceneKitView(scene: $scene)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    // MARK: - Actions

    private func generateSampleBuilding() {
        isGenerating = true
        generationStatus = "Generating..."

        DispatchQueue.global(qos: .userInitiated).async {
            // Sample building plan JSON
            let planJSON = """
            {
                "project_name": "Sample Building",
                "stories": [
                    {"name": "1F", "height_m": 3.6, "elevation_m": 0,
                     "slab_boundary": [[0,0],[15,0],[15,10],[0,10]]},
                    {"name": "2F", "height_m": 3.2, "elevation_m": 3.6,
                     "slab_boundary": [[0,0],[15,0],[15,10],[0,10]]},
                    {"name": "3F", "height_m": 3.2, "elevation_m": 6.8,
                     "slab_boundary": [[0,0],[15,0],[15,10],[0,10]]}
                ],
                "building_footprint": [[0,0],[15,0],[15,10],[0,10]]
            }
            """

            // Try native USD generation first
            var loadedScene: SCNScene? = nil
            if nativeBridge.isAvailable {
                let tmpDir = NSTemporaryDirectory()
                let usdPath = "\(tmpDir)promptbim_preview.usda"

                if nativeBridge.generateUSD(planJSON: planJSON, outputPath: usdPath) {
                    loadedScene = BIMSceneBuilder.loadUSDA(at: usdPath)
                }
            }

            // Fallback: build scene from JSON directly
            if loadedScene == nil {
                loadedScene = BIMSceneBuilder.buildScene(fromPlanJSON: planJSON)
            }

            DispatchQueue.main.async {
                scene = loadedScene
                isGenerating = false
                generationStatus = ""
            }
        }
    }

    private func loadUSDAFile() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.init(filenameExtension: "usda")!, .init(filenameExtension: "usdz")!]
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false

        if panel.runModal() == .OK, let url = panel.url {
            let loadedScene = BIMSceneBuilder.loadUSDA(at: url.path)
            if let s = loadedScene {
                scene = s
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(PythonBridge())
}

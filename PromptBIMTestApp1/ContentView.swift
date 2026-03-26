import SwiftUI
import SceneKit

// MARK: - Theme System (Task 11)

enum AppTheme: String, CaseIterable {
    case system, light, dark

    var colorScheme: ColorScheme? {
        switch self {
        case .system: return nil
        case .light: return .light
        case .dark: return .dark
        }
    }

    var label: String {
        switch self {
        case .system: return "System"
        case .light: return "Light"
        case .dark: return "Dark"
        }
    }

    var icon: String {
        switch self {
        case .system: return "circle.lefthalf.filled"
        case .light: return "sun.max"
        case .dark: return "moon"
        }
    }
}

// MARK: - Pipeline Progress (Task 16)

struct PipelineStep: Identifiable {
    let id = UUID()
    let name: String
    let icon: String
    var status: StepStatus

    enum StepStatus {
        case pending, running, completed, failed
    }
}

// MARK: - ContentView

struct ContentView: View {
    @EnvironmentObject var bridge: PythonBridge
    @State private var selectedTab = 0
    @State private var scene: SCNScene? = nil
    @State private var isGenerating = false
    @State private var generationStatus = ""
    @State private var nativeBridge = NativeBIMBridge.shared

    // Task 11: Theme
    @AppStorage("appTheme") private var selectedTheme: String = AppTheme.system.rawValue
    // Task 12: Sidebar
    @State private var sidebarExpanded = true
    @State private var sectionLand = true
    @State private var sectionBuild = true
    @State private var sectionInfo = false
    // Task 13: 2D view
    @State private var showBoundary = true
    @State private var showAreaLabels = true
    @State private var showSetback = false
    // Task 14: 3D enhancements
    @State private var floorCutLevel: Double = -1
    @State private var buildingOpacity: Double = 0.85
    // Task 15: Properties
    @State private var complianceStatus: String = "Not checked"
    @State private var costEstimate: String = "N/A"
    // Task 16: Pipeline progress
    @State private var pipelineSteps: [PipelineStep] = []
    // Task 24: Voice input
    @State private var isRecordingVoice = false
    @State private var voiceTranscript = ""

    private var theme: AppTheme {
        AppTheme(rawValue: selectedTheme) ?? .system
    }

    var body: some View {
        let content = HSplitView {
            // Left sidebar (Task 12)
            if sidebarExpanded {
                sidebarView
                    .frame(minWidth: 220, idealWidth: 250, maxWidth: 320)
            }

            // Main content area
            VStack(spacing: 0) {
                headerView
                Divider()
                tabBar
                Divider()
                tabContent
                Divider()

                // Pipeline progress (Task 16)
                if !pipelineSteps.isEmpty {
                    pipelineProgressView
                    Divider()
                }

                statusBar
            }
        }

        if let scheme = theme.colorScheme {
            content.preferredColorScheme(scheme)
        } else {
            content
        }
    }

    // MARK: - Header (Task 11: theme picker)

    private var headerView: some View {
        HStack {
            Button(action: { withAnimation { sidebarExpanded.toggle() } }) {
                Image(systemName: "sidebar.left")
            }
            .buttonStyle(.plain)
            .help("Toggle Sidebar")

            Image(systemName: "building.2")
                .font(.title)
            Text("PromptBIM")
                .font(.title)
                .fontWeight(.bold)
            Text("AI-Powered BIM Generator")
                .font(.subheadline)
                .foregroundColor(.secondary)
            Spacer()

            // Voice button (Task 24)
            Button(action: toggleVoiceRecording) {
                Image(systemName: isRecordingVoice ? "mic.fill" : "mic")
                    .foregroundColor(isRecordingVoice ? .red : .secondary)
            }
            .buttonStyle(.plain)
            .help(isRecordingVoice ? "Stop Recording" : "Push to Talk")

            if !voiceTranscript.isEmpty {
                Text(voiceTranscript)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
                    .frame(maxWidth: 200)
            }

            // Theme picker (Task 11)
            Menu {
                ForEach(AppTheme.allCases, id: \.rawValue) { t in
                    Button(action: { selectedTheme = t.rawValue }) {
                        Label(t.label, systemImage: t.icon)
                    }
                }
            } label: {
                Image(systemName: theme.icon)
                    .font(.body)
            }
            .menuStyle(.borderlessButton)
            .frame(width: 28)
            .help("Theme")

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
    }

    // MARK: - Sidebar (Task 12)

    private var sidebarView: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                // Land section
                CollapsibleSection(title: "Land Parcel", icon: "map", isExpanded: $sectionLand) {
                    VStack(alignment: .leading, spacing: 8) {
                        // Task 13: 2D layer toggles
                        Toggle(isOn: $showBoundary) {
                            Label("Boundary", systemImage: "square.dashed")
                        }
                        .toggleStyle(.checkbox)
                        Toggle(isOn: $showAreaLabels) {
                            Label("Area Labels", systemImage: "textformat.size")
                        }
                        .toggleStyle(.checkbox)
                        Toggle(isOn: $showSetback) {
                            Label("Setback Lines", systemImage: "arrow.left.and.right")
                        }
                        .toggleStyle(.checkbox)

                        Divider()
                        Text("Area: 150.0 m\u{00B2}")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("Perimeter: 50.0 m")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                // Building section
                CollapsibleSection(title: "Building", icon: "building.2", isExpanded: $sectionBuild) {
                    VStack(alignment: .leading, spacing: 8) {
                        // Task 14: 3D controls
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Opacity")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Slider(value: $buildingOpacity, in: 0.1...1.0)
                        }

                        VStack(alignment: .leading, spacing: 2) {
                            Text("Floor Section Cut")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Slider(value: $floorCutLevel, in: -1...10, step: 1)
                            Text(floorCutLevel < 0 ? "Off" : "Level \(Int(floorCutLevel))")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                // Properties section (Task 15)
                CollapsibleSection(title: "Properties", icon: "info.circle", isExpanded: $sectionInfo) {
                    VStack(alignment: .leading, spacing: 8) {
                        PropertyRow(label: "Compliance", value: complianceStatus,
                                    color: complianceStatus == "Pass" ? .green : .orange)
                        PropertyRow(label: "Cost Est.", value: costEstimate, color: .secondary)
                        PropertyRow(label: "Stories", value: "3", color: .secondary)
                        PropertyRow(label: "Total Area", value: "450 m\u{00B2}", color: .secondary)
                        PropertyRow(label: "BCR", value: "42%", color: .secondary)
                        PropertyRow(label: "FAR", value: "126%", color: .secondary)
                    }
                }
            }
            .padding()
        }
        .background(Color(nsColor: .controlBackgroundColor))
    }

    // MARK: - Tab Bar

    private var tabBar: some View {
        HStack(spacing: 0) {
            tabButton(title: "Dashboard", icon: "house", index: 0)
            tabButton(title: "2D View", icon: "square.grid.2x2", index: 1)
            tabButton(title: "3D Preview", icon: "cube", index: 2)
        }
        .padding(.horizontal)
        .padding(.top, 4)
    }

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case 0: dashboardView
        case 1: cadastralView2D
        case 2: preview3DView
        default: EmptyView()
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

    // MARK: - Dashboard View

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
            } else if !bridge.guiLaunched && bridge.pythonAvailable {
                VStack(spacing: 20) {
                    Spacer()
                    Image(systemName: "building.2.fill")
                        .font(.system(size: 48))
                        .foregroundColor(.accentColor)
                    Text("Demo Project Loaded")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("Taipei Xinyi District \u{2014} 3-story Residential")
                        .foregroundColor(.secondary)
                    Text("Launching PySide6 GUI with demo data...")
                        .foregroundColor(.secondary)
                        .font(.caption)
                    ProgressView()
                        .scaleEffect(0.8)
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
            }
        }
    }

    // MARK: - 2D Cadastral View (Task 13)

    private var cadastralView2D: some View {
        GeometryReader { geo in
            Canvas { context, size in
                let scale: CGFloat = min(size.width, size.height) / 30.0
                let offsetX = size.width / 2 - 10 * scale
                let offsetY = size.height / 2 - 7.5 * scale

                // Land boundary
                if showBoundary {
                    let coords: [(CGFloat, CGFloat)] = [(0, 0), (20, 0), (20, 15), (0, 15)]
                    var path = Path()
                    for (i, c) in coords.enumerated() {
                        let pt = CGPoint(x: offsetX + c.0 * scale, y: offsetY + (15 - c.1) * scale)
                        if i == 0 { path.move(to: pt) } else { path.addLine(to: pt) }
                    }
                    path.closeSubpath()
                    context.stroke(path, with: .color(.green), lineWidth: 2)
                    context.fill(path, with: .color(.green.opacity(0.08)))
                }

                // Setback lines
                if showSetback {
                    let setback: CGFloat = 2
                    let inner: [(CGFloat, CGFloat)] = [
                        (setback, setback), (20 - setback, setback),
                        (20 - setback, 15 - setback), (setback, 15 - setback),
                    ]
                    var sPath = Path()
                    for (i, c) in inner.enumerated() {
                        let pt = CGPoint(x: offsetX + c.0 * scale, y: offsetY + (15 - c.1) * scale)
                        if i == 0 { sPath.move(to: pt) } else { sPath.addLine(to: pt) }
                    }
                    sPath.closeSubpath()
                    context.stroke(sPath, with: .color(.orange), style: StrokeStyle(lineWidth: 1, dash: [5, 3]))
                }

                // Building footprint
                let building: [(CGFloat, CGFloat)] = [(2.5, 2.5), (17.5, 2.5), (17.5, 12.5), (2.5, 12.5)]
                var bPath = Path()
                for (i, c) in building.enumerated() {
                    let pt = CGPoint(x: offsetX + c.0 * scale, y: offsetY + (15 - c.1) * scale)
                    if i == 0 { bPath.move(to: pt) } else { bPath.addLine(to: pt) }
                }
                bPath.closeSubpath()
                context.fill(bPath, with: .color(.blue.opacity(0.15)))
                context.stroke(bPath, with: .color(.blue), lineWidth: 1.5)

                // Area labels (Task 13)
                if showAreaLabels {
                    let landCenter = CGPoint(x: offsetX + 10 * scale, y: offsetY + 1.5 * scale)
                    context.draw(
                        Text("Land: 300 m\u{00B2}").font(.caption).foregroundColor(.green),
                        at: landCenter
                    )
                    let buildCenter = CGPoint(x: offsetX + 10 * scale, y: offsetY + 7.5 * scale)
                    context.draw(
                        Text("Building: 150 m\u{00B2}").font(.caption).foregroundColor(.blue),
                        at: buildCenter
                    )
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(nsColor: .controlBackgroundColor))
    }

    // MARK: - 3D Preview View (Task 14 + P24-Task 7)

    private var preview3DView: some View {
        VStack(spacing: 0) {
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

            SceneKitView(scene: $scene)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .onAppear { loadDemoSceneIfNeeded() }
        }
    }

    /// P24-Task 7: Auto-load demo USDA on 3D tab appear
    private func loadDemoSceneIfNeeded() {
        guard scene == nil else { return }
        // Try loading demo USDA from resources/demo/
        let demoUSDA = BIMSceneBuilder.findDemoUSDA()
        if let path = demoUSDA, let loaded = BIMSceneBuilder.loadUSDA(at: path) {
            scene = loaded
            return
        }
        // Fallback: generate sample scene from embedded plan JSON
        scene = BIMSceneBuilder.buildDemoScene()
    }

    // MARK: - Pipeline Progress (Task 16)

    private var pipelineProgressView: some View {
        HStack(spacing: 12) {
            ForEach(pipelineSteps) { step in
                HStack(spacing: 4) {
                    Group {
                        switch step.status {
                        case .pending:
                            Image(systemName: "circle")
                                .foregroundColor(.secondary)
                        case .running:
                            ProgressView()
                                .scaleEffect(0.5)
                                .frame(width: 14, height: 14)
                        case .completed:
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                        case .failed:
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.red)
                        }
                    }
                    .font(.caption)
                    Text(step.name)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                if step.id != pipelineSteps.last?.id {
                    Image(systemName: "chevron.right")
                        .font(.caption2)
                        .foregroundColor(.secondary.opacity(0.5))
                }
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 6)
    }

    // MARK: - Status Bar

    private var statusBar: some View {
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

    // MARK: - Actions

    private func generateSampleBuilding() {
        isGenerating = true
        generationStatus = "Generating..."

        // Task 16: Pipeline progress
        pipelineSteps = [
            PipelineStep(name: "Parse", icon: "doc.text", status: .running),
            PipelineStep(name: "Plan", icon: "rectangle.3.group", status: .pending),
            PipelineStep(name: "Generate", icon: "cube", status: .pending),
            PipelineStep(name: "Render", icon: "eye", status: .pending),
        ]

        DispatchQueue.global(qos: .userInitiated).async {
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

            DispatchQueue.main.async {
                pipelineSteps[0].status = .completed
                pipelineSteps[1].status = .running
            }

            var loadedScene: SCNScene? = nil
            if nativeBridge.isAvailable {
                let tmpDir = NSTemporaryDirectory()
                let usdPath = "\(tmpDir)promptbim_preview.usda"

                DispatchQueue.main.async {
                    pipelineSteps[1].status = .completed
                    pipelineSteps[2].status = .running
                }

                if nativeBridge.generateUSD(planJSON: planJSON, outputPath: usdPath) {
                    loadedScene = BIMSceneBuilder.loadUSDA(at: usdPath)
                }
            }

            if loadedScene == nil {
                DispatchQueue.main.async {
                    pipelineSteps[1].status = .completed
                    pipelineSteps[2].status = .running
                }
                loadedScene = BIMSceneBuilder.buildScene(fromPlanJSON: planJSON)
            }

            DispatchQueue.main.async {
                pipelineSteps[2].status = .completed
                pipelineSteps[3].status = .running
            }

            DispatchQueue.main.async {
                scene = loadedScene
                isGenerating = false
                generationStatus = ""
                pipelineSteps[3].status = .completed

                DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                    pipelineSteps = []
                }
            }
        }
    }

    // MARK: - Voice (Task 24/25)

    private func toggleVoiceRecording() {
        if isRecordingVoice {
            isRecordingVoice = false
            voiceTranscript = "Processing..."
            // Voice → AI pipeline (Task 25): send transcript to Python backend
            bridge.runCommand(arguments: ["-m", "promptbim", "voice", "stop-transcribe"]) { result in
                DispatchQueue.main.async {
                    let transcript = result?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
                    voiceTranscript = transcript.isEmpty ? "No speech detected" : transcript
                    if !transcript.isEmpty {
                        // Auto-generate from voice input
                        generateFromVoice(transcript)
                    }
                }
            }
        } else {
            isRecordingVoice = true
            voiceTranscript = "Listening..."
            bridge.runCommand(arguments: ["-m", "promptbim", "voice", "start-record"]) { _ in }
        }
    }

    private func generateFromVoice(_ transcript: String) {
        isGenerating = true
        generationStatus = "Generating from voice: \(transcript.prefix(50))..."
        bridge.generateBuilding(prompt: transcript) { result in
            DispatchQueue.main.async {
                isGenerating = false
                generationStatus = ""
                if let json = result {
                    if let planScene = BIMSceneBuilder.buildScene(fromPlanJSON: json) {
                        scene = planScene
                    }
                }
            }
        }
    }

    private func loadUSDAFile() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.init(filenameExtension: "usda"), .init(filenameExtension: "usdz")].compactMap { $0 }
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

// MARK: - Collapsible Section (Task 12)

struct CollapsibleSection<Content: View>: View {
    let title: String
    let icon: String
    @Binding var isExpanded: Bool
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button(action: { withAnimation(.easeInOut(duration: 0.2)) { isExpanded.toggle() } }) {
                HStack {
                    Image(systemName: icon)
                        .foregroundColor(.accentColor)
                        .frame(width: 20)
                    Text(title)
                        .fontWeight(.semibold)
                    Spacer()
                    Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .buttonStyle(.plain)

            if isExpanded {
                content()
                    .padding(.leading, 24)
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Property Row (Task 15)

struct PropertyRow: View {
    let label: String
    let value: String
    let color: Color

    var body: some View {
        HStack {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(color)
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(PythonBridge())
}

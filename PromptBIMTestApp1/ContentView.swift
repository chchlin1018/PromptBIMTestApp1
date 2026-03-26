import SwiftUI

struct ContentView: View {
    @EnvironmentObject var bridge: PythonBridge

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
                Text("v\(bridge.version)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()

            Divider()

            // Main content — splash screen while launching
            if bridge.guiLaunched {
                // GUI is running — show status
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
                // Python not found — show setup instructions
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
                // Python available, GUI not yet launched — splash screen
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
                    // Auto-launch PySide6 GUI once Python is confirmed
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                        if bridge.pythonAvailable && !bridge.guiLaunched {
                            bridge.launchPySide6GUI()
                        }
                    }
                }
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
}

#Preview {
    ContentView()
        .environmentObject(PythonBridge())
}

import SwiftUI

struct ContentView: View {
    @StateObject private var bridge = PythonBridge()

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
                Text("v0.1.0")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()

            Divider()

            // Main content area
            HSplitView {
                // Left panel - Land info
                VStack(alignment: .leading, spacing: 12) {
                    Text("Land Info")
                        .font(.headline)
                    Text("No land data loaded")
                        .foregroundColor(.secondary)
                    Spacer()
                }
                .frame(minWidth: 250, maxWidth: 350)
                .padding()

                // Center - Tab view
                TabView {
                    Text("2D View — Land parcel will appear here")
                        .tabItem { Label("2D Map", systemImage: "map") }

                    Text("3D View — Building model will appear here")
                        .tabItem { Label("3D Model", systemImage: "cube") }
                }
                .frame(minWidth: 500)
            }

            Divider()

            // Bottom - Chat panel
            HStack {
                Image(systemName: "bubble.left")
                TextField("Describe the building you want to create...", text: .constant(""))
                    .textFieldStyle(.roundedBorder)
                Button(action: {}) {
                    Image(systemName: "mic")
                }
                Button("Generate") {}
                    .buttonStyle(.borderedProminent)
            }
            .padding()

            // Status bar
            HStack {
                Text(bridge.statusMessage)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text("Python: \(bridge.pythonAvailable ? "Connected" : "Not Found")")
                    .font(.caption)
                    .foregroundColor(bridge.pythonAvailable ? .green : .red)
            }
            .padding(.horizontal)
            .padding(.bottom, 4)
        }
    }
}

#Preview {
    ContentView()
}

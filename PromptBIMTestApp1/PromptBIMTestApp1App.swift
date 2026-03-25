import SwiftUI

@main
struct PromptBIMTestApp1App: App {
    @StateObject private var bridge = PythonBridge()

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.titleBar)
        .defaultSize(width: 800, height: 500)
    }
}

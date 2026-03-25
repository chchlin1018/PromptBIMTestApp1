import SwiftUI

@main
struct PromptBIMTestApp1App: App {
    @StateObject private var bridge = PythonBridge()
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(bridge)
                .onAppear { appDelegate.bridge = bridge }
        }
        .windowStyle(.titleBar)
        .defaultSize(width: 800, height: 500)
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var bridge: PythonBridge?

    func applicationWillTerminate(_ notification: Notification) {
        bridge?.terminateGUI()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }
}

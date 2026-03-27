cmake_minimum_required(VERSION 3.21)
project(Zigma VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Qml Quick Quick3D)

qt_standard_project_setup()

qt_add_executable(zigma_app
    src/main.cpp
    src/AgentBridge.h src/AgentBridge.cpp
    src/BIMGeometryProvider.h src/BIMGeometryProvider.cpp
    src/BIMMaterialLibrary.h src/BIMMaterialLibrary.cpp
    src/BIMSceneBuilder.h src/BIMSceneBuilder.cpp
)
set_target_properties(zigma_app PROPERTIES OUTPUT_NAME ZigmaApp)

set_source_files_properties(qml/ThemeManager.qml PROPERTIES QT_QML_SINGLETON_TYPE TRUE)

qt_add_qml_module(zigma_app
    URI Zigma
    VERSION 1.0
    QML_FILES
        qml/main.qml
        qml/BIMView3D.qml
        qml/ChatPanel.qml
        qml/PropertyPanel.qml
        qml/CostPanel.qml
        qml/DeltaPanel.qml
        qml/SchedulePanel.qml
        qml/StatusBar.qml
        qml/ScenePicker.qml
        qml/AssetBrowser.qml
        qml/ThemeManager.qml
        qml/LoadingOverlay.qml
        qml/SplashScreen.qml
)

target_include_directories(zigma_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_link_libraries(zigma_app PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Qml
    Qt6::Quick
    Qt6::Quick3D
)

# Tests
enable_testing()
find_package(Qt6 REQUIRED COMPONENTS Test)

qt_add_executable(test_agent_bridge tests/test_agent_bridge.cpp
    src/AgentBridge.h src/AgentBridge.cpp)
target_link_libraries(test_agent_bridge PRIVATE Qt6::Core Qt6::Test Qt6::Gui Qt6::Qml Qt6::Quick)
add_test(NAME AgentBridgeTests COMMAND test_agent_bridge)

qt_add_executable(test_bim_components tests/test_bim_components.cpp
    src/BIMGeometryProvider.h src/BIMGeometryProvider.cpp
    src/BIMMaterialLibrary.h src/BIMMaterialLibrary.cpp
    src/BIMSceneBuilder.h src/BIMSceneBuilder.cpp)
target_link_libraries(test_bim_components PRIVATE Qt6::Core Qt6::Test Qt6::Gui Qt6::Qml Qt6::Quick Qt6::Quick3D)
add_test(NAME BIMComponentTests COMMAND test_bim_components)

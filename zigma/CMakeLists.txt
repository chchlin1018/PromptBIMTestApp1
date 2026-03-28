cmake_minimum_required(VERSION 3.21)
project(Zigma VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Qml Quick Quick3D ShaderTools)

qt_standard_project_setup()

qt_add_executable(zigma_app
    ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/AgentBridge.h ${CMAKE_CURRENT_SOURCE_DIR}/src/AgentBridge.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMGeometryProvider.h ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMGeometryProvider.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMMaterialLibrary.h ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMMaterialLibrary.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMSceneBuilder.h ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMSceneBuilder.cpp
)
set_target_properties(zigma_app PROPERTIES OUTPUT_NAME ZigmaApp)

set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/qml/ThemeManager.qml PROPERTIES QT_QML_SINGLETON_TYPE TRUE)

qt_add_qml_module(zigma_app
    URI Zigma
    VERSION 1.0
    QML_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/main.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/BIMView3D.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/ChatPanel.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/PropertyPanel.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/CostPanel.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/DeltaPanel.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/SchedulePanel.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/StatusBar.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/ScenePicker.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/AssetBrowser.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/ThemeManager.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/LoadingOverlay.qml
        ${CMAKE_CURRENT_SOURCE_DIR}/qml/SplashScreen.qml
)

target_include_directories(zigma_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_link_libraries(zigma_app PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Qml
    Qt6::Quick
    Qt6::Quick3D
)

# Media path
if(APPLE)
    set(ZIGMA_MEDIA_DEFAULT "$ENV{HOME}/ZigmaMedia")
elseif(WIN32)
    set(ZIGMA_MEDIA_DEFAULT "C:/ZigmaMedia")
endif()
set(ZIGMA_MEDIA_PATH "${ZIGMA_MEDIA_DEFAULT}" CACHE PATH "ZigmaMedia path")
target_compile_definitions(zigma_app PRIVATE ZIGMA_MEDIA_PATH="${ZIGMA_MEDIA_PATH}")

# Tests
enable_testing()
find_package(Qt6 REQUIRED COMPONENTS Test)

qt_add_executable(test_agent_bridge
    ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_agent_bridge.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/AgentBridge.h ${CMAKE_CURRENT_SOURCE_DIR}/src/AgentBridge.cpp)
target_link_libraries(test_agent_bridge PRIVATE Qt6::Core Qt6::Test Qt6::Gui Qt6::Qml Qt6::Quick)
add_test(NAME AgentBridgeTests COMMAND test_agent_bridge)

qt_add_executable(test_bim_components
    ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_bim_components.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMGeometryProvider.h ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMGeometryProvider.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMMaterialLibrary.h ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMMaterialLibrary.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMSceneBuilder.h ${CMAKE_CURRENT_SOURCE_DIR}/src/BIMSceneBuilder.cpp)
target_link_libraries(test_bim_components PRIVATE Qt6::Core Qt6::Test Qt6::Gui Qt6::Qml Qt6::Quick Qt6::Quick3D)
add_test(NAME BIMComponentTests COMMAND test_bim_components)

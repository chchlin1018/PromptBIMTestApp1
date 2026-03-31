# bim_core — Standalone BIM C++ core library (no Qt dependency)

add_library(bim_core STATIC
    BIMEntity.cpp
    BIMSceneGraph.cpp
    AgentBridge.cpp
    GeometryEngine.cpp
    PropertyManager.cpp
    CostCalculator.cpp
)

target_include_directories(bim_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(bim_core PUBLIC nlohmann_json::nlohmann_json)
target_compile_features(bim_core PUBLIC cxx_std_17)

if(MSVC)
    target_compile_options(bim_core PRIVATE /W4 /WX- /utf-8)
else()
    target_compile_options(bim_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# PromptBIM C++ Core Library

add_library(promptbim_core STATIC
    src/compliance_engine.cpp
    src/cost_engine.cpp
)

target_include_directories(promptbim_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# nlohmann/json for structured data
find_package(nlohmann_json CONFIG QUIET)
if(NOT nlohmann_json_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        nlohmann_json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG v3.11.3
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(nlohmann_json)
endif()
target_link_libraries(promptbim_core PUBLIC nlohmann_json::nlohmann_json)

target_compile_features(promptbim_core PUBLIC cxx_std_20)

# Platform-specific settings
if(MSVC)
    target_compile_options(promptbim_core PRIVATE /W4 /WX- /utf-8)
else()
    target_compile_options(promptbim_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# === BIM Core Library (standalone, no Qt) ===
add_subdirectory(core)
# Alias to avoid name collision with pybind11 module
add_library(bim_core_lib ALIAS bim_core)

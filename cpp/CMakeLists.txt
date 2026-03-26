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
if(nlohmann_json_FOUND)
    target_link_libraries(promptbim_core PUBLIC nlohmann_json::nlohmann_json)
endif()

target_compile_features(promptbim_core PUBLIC cxx_std_20)

# Platform-specific settings
if(MSVC)
    target_compile_options(promptbim_core PRIVATE /W4 /WX- /utf-8)
else()
    target_compile_options(promptbim_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

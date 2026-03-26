cmake_minimum_required(VERSION 3.21)
project(promptbim VERSION 2.5.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------
option(PROMPTBIM_BUILD_TESTS    "Build GoogleTest suite"      ON)
option(PROMPTBIM_BUILD_PYTHON   "Build pybind11 bindings"     ON)
option(PROMPTBIM_USE_VCPKG      "Use vcpkg for dependencies"  OFF)

# ---------------------------------------------------------------------------
# Dependencies — FetchContent (CI-friendly, no vcpkg required locally)
# ---------------------------------------------------------------------------
include(FetchContent)

# nlohmann/json
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG        v3.11.3
    GIT_SHALLOW    TRUE
)

if(PROMPTBIM_BUILD_TESTS)
    # GoogleTest
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG        v1.14.0
        GIT_SHALLOW    TRUE
    )
    # Don't install gtest alongside promptbim
    set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
endif()

FetchContent_MakeAvailable(nlohmann_json)
if(PROMPTBIM_BUILD_TESTS)
    FetchContent_MakeAvailable(googletest)
endif()

# ---------------------------------------------------------------------------
# Core library
# ---------------------------------------------------------------------------
add_library(promptbim_core STATIC
    src/compliance/compliance_engine.cpp
    src/cost/cost_engine.cpp
)

target_include_directories(promptbim_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(promptbim_core PUBLIC nlohmann_json::nlohmann_json)

# Shared library with C ABI (for Swift / FFI)
add_library(promptbim SHARED
    src/compliance/compliance_engine.cpp
    src/cost/cost_engine.cpp
)
target_include_directories(promptbim PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(promptbim PUBLIC nlohmann_json::nlohmann_json)
set_target_properties(promptbim PROPERTIES
    VERSION   ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
)

# ---------------------------------------------------------------------------
# pybind11 bindings
# ---------------------------------------------------------------------------
if(PROMPTBIM_BUILD_PYTHON)
    find_package(pybind11 CONFIG QUIET)
    if(pybind11_FOUND)
        pybind11_add_module(_native bindings/python/bindings.cpp)
        target_link_libraries(_native PRIVATE promptbim_core)
        target_include_directories(_native PRIVATE include)
    else()
        message(STATUS "pybind11 not found — skipping Python bindings")
    endif()
endif()

# ---------------------------------------------------------------------------
# GoogleTest suite
# ---------------------------------------------------------------------------
if(PROMPTBIM_BUILD_TESTS)
    enable_testing()
    add_executable(promptbim_tests
        tests/test_compliance_engine.cpp
        tests/test_cost_engine.cpp
        tests/test_version.cpp
    )
    target_link_libraries(promptbim_tests
        PRIVATE promptbim_core
                GTest::gtest_main
    )
    target_include_directories(promptbim_tests PRIVATE include)
    include(GoogleTest)
    gtest_discover_tests(promptbim_tests)
endif()

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
install(TARGETS promptbim
    LIBRARY  DESTINATION lib
    ARCHIVE  DESTINATION lib
    RUNTIME  DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include)

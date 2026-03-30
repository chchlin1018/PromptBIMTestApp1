# PromptBIM C++ Core — Root CMakeLists.txt
# Cross-platform: Windows (MSVC/VS2025) + macOS (Clang)

cmake_minimum_required(VERSION 3.25)
project(PromptBIMCppCore
    VERSION 3.0.0
    DESCRIPTION "PromptBIM C++ Core — Compliance Engine + Cost Engine"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# === vcpkg integration ===
if(DEFINED ENV{VCPKG_ROOT})
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
        CACHE STRING "vcpkg toolchain")
endif()

# === Options ===
option(BUILD_TESTS "Build C++ unit tests (GoogleTest)" ON)
option(BUILD_PYTHON_BINDINGS "Build pybind11 Python bindings" ON)

# === C++ Core Library ===
add_subdirectory(cpp)

# === Tests ===
if(BUILD_TESTS)
    enable_testing()
    find_package(GTest CONFIG QUIET)
    if(NOT GTest_FOUND)
        include(FetchContent)
        FetchContent_Declare(
            googletest
            GIT_REPOSITORY https://github.com/google/googletest.git
            GIT_TAG v1.14.0
        )
        set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
        FetchContent_MakeAvailable(googletest)
    endif()
    add_subdirectory(cpp/tests)
endif()

# === Python Bindings ===
if(BUILD_PYTHON_BINDINGS)
    find_package(pybind11 CONFIG QUIET)
    if(pybind11_FOUND)
        add_subdirectory(cpp/bindings)
    else()
        message(WARNING "pybind11 not found — Python bindings will not be built.")
    endif()
endif()

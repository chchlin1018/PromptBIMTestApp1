cmake_minimum_required(VERSION 3.21)
project(promptbim VERSION 2.11.0 LANGUAGES CXX)

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
# Python executable — prefer conda env python3.11 over system python
# ---------------------------------------------------------------------------
if(PROMPTBIM_BUILD_PYTHON AND NOT Python3_EXECUTABLE)
    # Try conda env first
    find_program(_CONDA_PYTHON python3.11
        PATHS "$ENV{CONDA_PREFIX}/bin" NO_DEFAULT_PATH)
    if(_CONDA_PYTHON)
        set(Python3_EXECUTABLE "${_CONDA_PYTHON}" CACHE FILEPATH
            "Preferred Python interpreter (conda env)" FORCE)
        message(STATUS "Using conda Python: ${_CONDA_PYTHON}")
    else()
        find_program(_SYS_PYTHON python3.11)
        if(_SYS_PYTHON)
            set(Python3_EXECUTABLE "${_SYS_PYTHON}" CACHE FILEPATH
                "Preferred Python interpreter" FORCE)
        endif()
    endif()
endif()

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
# Compiler hardening flags
# ---------------------------------------------------------------------------
add_compile_options(
    -fstack-protector-strong
    -D_FORTIFY_SOURCE=2
    -Wall -Wextra -Wpedantic
)

# Symbol visibility — only export explicitly marked symbols
set(CMAKE_C_VISIBILITY_PRESET hidden)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# Sanitizer support for development builds
option(PROMPTBIM_ENABLE_SANITIZERS "Enable ASan/UBSan" OFF)
if(PROMPTBIM_ENABLE_SANITIZERS)
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
endif()

# ---------------------------------------------------------------------------
# Source file list
# ---------------------------------------------------------------------------
set(PROMPTBIM_SOURCES
    src/geometry/geometry.cpp
    src/compliance/compliance_engine.cpp
    src/cost/cost_engine.cpp
    src/mep/mep_engine.cpp
    src/simulation/simulation_engine.cpp
    src/bim/ifc_generator.cpp
    src/bim/usd_generator.cpp
    src/gis/gis_engine.cpp
)

# ---------------------------------------------------------------------------
# Core library (static — for tests and pybind11)
# ---------------------------------------------------------------------------
add_library(promptbim_core STATIC ${PROMPTBIM_SOURCES})

target_include_directories(promptbim_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(promptbim_core PUBLIC nlohmann_json::nlohmann_json)

# Shared library with C ABI (for Swift / FFI)
add_library(promptbim SHARED ${PROMPTBIM_SOURCES})
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
        tests/test_mep_engine.cpp
        tests/test_simulation_engine.cpp
        tests/test_geometry.cpp
        tests/test_utf8.cpp
        tests/test_ifc_generator.cpp
        tests/test_bim_engine.cpp
        tests/test_gis_engine.cpp
        tests/test_thread_safety.cpp
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

# PromptBIM C++ Tests — GoogleTest

add_executable(promptbim_tests
    test_compliance.cpp
    test_cost.cpp
)

target_link_libraries(promptbim_tests PRIVATE
    promptbim_core
    GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests(promptbim_tests)

# === BIM Core Tests ===
add_executable(bim_core_tests
    test_entity.cpp
    test_scenegraph.cpp
    test_agent_actions.cpp
    test_binding.cpp
    test_tsmc_demo.cpp
)

target_link_libraries(bim_core_tests PRIVATE
    bim_core_static
    GTest::gtest_main
)

target_include_directories(bim_core_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core
)

gtest_discover_tests(bim_core_tests)

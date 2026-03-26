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

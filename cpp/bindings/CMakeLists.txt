# PromptBIM C++ — pybind11 Python Bindings

pybind11_add_module(promptbim_cpp pybind_module.cpp)

target_link_libraries(promptbim_cpp PRIVATE promptbim_core)

# Install to Python site-packages
install(TARGETS promptbim_cpp
    LIBRARY DESTINATION ${Python3_SITEARCH}
)

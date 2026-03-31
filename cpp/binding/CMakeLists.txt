# bim_core pybind11 binding
pybind11_add_module(bim_core bim_core_module.cpp)
target_link_libraries(bim_core PRIVATE bim_core_static)
target_include_directories(bim_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../core)

# Also build the existing promptbim_cpp binding
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/pybind_module.cpp)
    pybind11_add_module(promptbim_cpp pybind_module.cpp)
    target_link_libraries(promptbim_cpp PRIVATE promptbim_core)
endif()

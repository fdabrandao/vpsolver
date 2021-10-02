cmake_minimum_required(VERSION 3.1...3.19)

project(
    VPSolver
    VERSION 3.0
    LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)

add_library(vpsolver-lib OBJECT
    src/instance.cpp src/instance.hpp 
    src/graph.cpp src/graph.hpp
    src/arcflow.cpp src/arcflow.hpp
    src/common.cpp src/common.hpp)

add_executable(vbp2afg src/vbp2afg.cpp $<TARGET_OBJECTS:vpsolver-lib>)
add_executable(afg2mps src/afg2mps.cpp $<TARGET_OBJECTS:vpsolver-lib>)
add_executable(afg2lp src/afg2lp.cpp $<TARGET_OBJECTS:vpsolver-lib>)
add_executable(vbpsol src/vbpsol.cpp src/arcflowsol.cpp src/arcflowsol.hpp $<TARGET_OBJECTS:vpsolver-lib>)

# CPack
set(CPACK_GENERATOR ZIP)
set(CPACK_PACKAGE_FILE_NAME vpsolver)
include(CPack)

# CTest
include(CTest)
enable_testing()
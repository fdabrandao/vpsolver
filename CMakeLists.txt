cmake_minimum_required(VERSION 3.3...3.19)

project(
    VPSolver
    VERSION 3.0
    LANGUAGES CXX)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})
set(CMAKE_CXX_STANDARD 11)

# Visual Studio compiler with static runtime libraries
if(MSVC AND MT)
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MT")
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MTd")
  set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} /MT")
  set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} /MTd")
endif()

add_library(vpsolver-lib OBJECT
    src/instance.cpp src/instance.hpp 
    src/graph.cpp src/graph.hpp
    src/arcflow.cpp src/arcflow.hpp
    src/arcflowsol.cpp src/arcflowsol.hpp
    src/common.cpp src/common.hpp)

# VPSolver executable
find_package(GUROBI)
if(GUROBI_CXX_LIBRARY AND GUROBI_LIBRARY AND GUROBI_INCLUDE_DIRS)
    add_executable(vpsolver src/vpsolver.cpp $<TARGET_OBJECTS:vpsolver-lib>)
    target_include_directories(vpsolver PRIVATE ${GUROBI_INCLUDE_DIRS})
    target_link_libraries(vpsolver ${GUROBI_CXX_LIBRARY} ${GUROBI_LIBRARY})
    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/vpsolver)
endif()

# Auxiliary executables
add_executable(vbp2afg src/vbp2afg.cpp $<TARGET_OBJECTS:vpsolver-lib>)
add_executable(afg2mps src/afg2mps.cpp $<TARGET_OBJECTS:vpsolver-lib>)
add_executable(afg2lp src/afg2lp.cpp $<TARGET_OBJECTS:vpsolver-lib>)
add_executable(vbpsol src/vbpsol.cpp $<TARGET_OBJECTS:vpsolver-lib>)
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/vbp2afg
    ${CMAKE_CURRENT_BINARY_DIR}/afg2mps
    ${CMAKE_CURRENT_BINARY_DIR}/afg2lp
    ${CMAKE_CURRENT_BINARY_DIR}/vbpsol
    DESTINATION bin)
install(DIRECTORY
    ${CMAKE_CURRENT_SOURCE_DIR}/scripts/
    DESTINATION scripts)

# CPack
set(CPACK_GENERATOR ZIP)
set(CPACK_PACKAGE_FILE_NAME vpsolver)
include(CPack)

# CTest
include(CTest)
enable_testing()
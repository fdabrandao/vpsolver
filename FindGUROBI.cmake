find_path(
  GUROBI_INCLUDE_DIRS
  NAMES gurobi_c.h
  HINTS ${GUROBI_DIR} $ENV{GUROBI_HOME}
  PATH_SUFFIXES include)

find_library(
  GUROBI_LIBRARY
  NAMES gurobi gurobi81 gurobi90 gurobi95
  HINTS ${GUROBI_DIR} $ENV{GUROBI_HOME}
  PATH_SUFFIXES lib)

get_property(languages GLOBAL PROPERTY ENABLED_LANGUAGES)
if("CXX" IN_LIST languages)
  if(MSVC)
    # determine Visual Studio year
    if(MSVC_TOOLSET_VERSION EQUAL 142)
      set(MSVC_YEAR "2019")
    elseif(MSVC_TOOLSET_VERSION EQUAL 141)
      set(MSVC_YEAR "2017")
    elseif(MSVC_TOOLSET_VERSION EQUAL 140)
      set(MSVC_YEAR "2015")
    endif()

    if(MT)
      set(M_FLAG "mt")
    else()
      set(M_FLAG "md")
    endif()

    find_library(
      GUROBI_CXX_LIBRARY
      NAMES gurobi_c++${M_FLAG}${MSVC_YEAR}
      HINTS ${GUROBI_DIR} $ENV{GUROBI_HOME}
      PATH_SUFFIXES lib)
    find_library(
      GUROBI_CXX_DEBUG_LIBRARY
      NAMES gurobi_c++${M_FLAG}d${MSVC_YEAR}
      HINTS ${GUROBI_DIR} $ENV{GUROBI_HOME}
      PATH_SUFFIXES lib)
  else()
    find_library(
      GUROBI_CXX_LIBRARY
      NAMES gurobi_c++
      HINTS ${GUROBI_DIR} $ENV{GUROBI_HOME}
      PATH_SUFFIXES lib)
    set(GUROBI_CXX_DEBUG_LIBRARY ${GUROBI_CXX_LIBRARY})
  endif()
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(GUROBI DEFAULT_MSG GUROBI_LIBRARY
                                  GUROBI_INCLUDE_DIRS)

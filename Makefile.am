AUTOMAKE_OPTIONS = foreign
AM_CXXFLAGS = -std=c++11 -Wall -O2
AM_LDFLAGS  =

bin_SCRIPTS = scripts/vpsolver_coinor.sh scripts/vpsolver_cplex.sh scripts/vpsolver_glpk.sh scripts/vpsolver_gurobi.sh scripts/vpsolver_lpsolve.sh scripts/vpsolver_scip.sh
EXTRA_DIST = scripts/vpsolver_coinor.sh scripts/vpsolver_cplex.sh scripts/vpsolver_glpk.sh scripts/vpsolver_gurobi.sh scripts/vpsolver_lpsolve.sh scripts/vpsolver_scip.sh

if GUROBI_HOME_SET
bin_PROGRAMS = $(top_builddir)/bin/vbp2afg $(top_builddir)/bin/afg2mps $(top_builddir)/bin/afg2lp   $(top_builddir)/bin/vbpsol $(top_builddir)/bin/vpsolver
else
bin_PROGRAMS = $(top_builddir)/bin/vbp2afg $(top_builddir)/bin/afg2mps $(top_builddir)/bin/afg2lp $(top_builddir)/bin/vbpsol
endif

__top_builddir__bin_vbp2afg_SOURCES = src/vbp2afg.cpp src/instance.cpp src/instance.hpp src/graph.cpp src/graph.hpp src/arcflow.cpp src/arcflow.hpp src/common.cpp src/common.hpp

__top_builddir__bin_afg2mps_SOURCES = src/afg2mps.cpp src/instance.cpp src/instance.hpp src/graph.cpp src/graph.hpp src/arcflow.cpp src/arcflow.hpp src/common.cpp src/common.hpp

__top_builddir__bin_afg2lp_SOURCES = src/afg2lp.cpp src/instance.cpp src/instance.hpp src/graph.cpp src/graph.hpp src/arcflow.cpp src/arcflow.hpp src/common.cpp src/common.hpp

__top_builddir__bin_vbpsol_SOURCES = src/vbpsol.cpp src/instance.cpp src/instance.hpp src/graph.cpp src/graph.hpp src/arcflow.cpp src/arcflow.hpp src/arcflowsol.cpp src/arcflowsol.hpp src/common.cpp src/common.hpp

if GUROBI_HOME_SET
__top_builddir__bin_vpsolver_SOURCES = src/vpsolver.cpp src/instance.cpp src/instance.hpp src/graph.cpp src/graph.hpp src/arcflow.cpp src/arcflowsol.cpp src/arcflowsol.hpp src/common.cpp src/common.hpp
__top_builddir__bin_vpsolver_CPPFLAGS = -I$(GUROBI_HOME)/include/
__top_builddir__bin_vpsolver_LDFLAGS = -L$(GUROBI_HOME)/lib/
if GUROBI_LIBS_SET
__top_builddir__bin_vpsolver_LDADD = -lpthread $(GUROBI_LIBS)
else
__top_builddir__bin_vpsolver_LDADD = -lpthread -lgurobi_c++ -lgurobi65
endif
endif

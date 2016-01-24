SRC = src
BIN = bin
CC=g++
CFLAGS= -std=c++11 -Wall -O2

GUROBI_DIR = /opt/gurobi650/linux64
INC    = $(GUROBI_DIR)/include/
CLIB   = -L$(GUROBI_DIR)/lib/ -lpthread -lgurobi65
CPPLIB = -L$(GUROBI_DIR)/lib/ -lpthread -lgurobi_c++ -lgurobi65
GUROBI_OPTS = -I$(INC) $(CPPLIB)

GLPK_OPTS = -lglpk

all: $(BIN)/vpsolver $(BIN)/vbp2afg $(BIN)/afg2mps $(BIN)/afg2lp $(BIN)/solve_gurobi $(BIN)/solve_glpk $(BIN)/vbpsol

$(BIN)/vpsolver: $(SRC)/vpsolver.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/arcflowsol.cpp $(SRC)/common.cpp
	$(CC) -o $(BIN)/vpsolver $(CFLAGS) $(SRC)/vpsolver.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/arcflowsol.cpp $(SRC)/common.cpp $(GUROBI_OPTS)

$(BIN)/vbp2afg: $(SRC)/vbp2afg.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/common.cpp
	$(CC) -o $(BIN)/vbp2afg $(CFLAGS) $(SRC)/vbp2afg.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/common.cpp

$(BIN)/afg2mps: $(SRC)/afg2mps.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/common.cpp
	$(CC) -o $(BIN)/afg2mps $(CFLAGS) $(SRC)/afg2mps.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/common.cpp

$(BIN)/afg2lp: $(SRC)/afg2lp.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/common.cpp
	$(CC) -o $(BIN)/afg2lp $(CFLAGS) $(SRC)/afg2lp.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/common.cpp

$(BIN)/solve_gurobi: $(SRC)/solve_gurobi.cpp
	$(CC) -o $(BIN)/solve_gurobi $(CFLAGS) $(SRC)/solve_gurobi.cpp $(GUROBI_OPTS)

$(BIN)/solve_glpk: $(SRC)/solve_glpk.cpp
	$(CC) -o $(BIN)/solve_glpk $(CFLAGS) $(SRC)/solve_glpk.cpp $(GLPK_OPTS)

$(BIN)/vbpsol: $(SRC)/vbpsol.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/arcflowsol.cpp $(SRC)/common.cpp
	$(CC) -o $(BIN)/vbpsol $(CFLAGS) $(SRC)/vbpsol.cpp $(SRC)/instance.cpp $(SRC)/graph.cpp $(SRC)/arcflow.cpp $(SRC)/arcflowsol.cpp $(SRC)/common.cpp

clean:
	rm -rf $(BIN)/*

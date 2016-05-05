# autoreconf -i (to update)
# Initialize autoconf.
AC_INIT([VPSolver], [3.1.0], [fdabrandao@dcc.fc.up.pt],
        [vpsolver], [http://vpsolver.dcc.fc.up.pt/])
# Force autoconf to be at least this version number:
AC_PREREQ([2.68])
# Safety check - list a source file that wouldn't be in other directories:
AC_CONFIG_SRCDIR([src/vpsolver.cpp])
# Put configuration results here, so we can easily #include them:
AC_CONFIG_HEADERS([src/config.hpp])
# Put autotools auxiliary files in subdirectories to reduce clutter:
AC_CONFIG_AUX_DIR([build-tools])

# Enable "automake" to simplify creating makefiles:
AM_INIT_AUTOMAKE([subdir-objects -Wall -Werror])
AC_CONFIG_FILES([Makefile])

# Checks for programs, e.g., AC_PROG_CC
AC_PROG_CXX

# Checks conditional arguments
AC_SUBST([GUROBI_HOME])
AM_CONDITIONAL([GUROBI_HOME_SET], [test ! -z "$GUROBI_HOME"])
AC_SUBST([GUROBI_LIBS])
AM_CONDITIONAL([GUROBI_LIBS_SET], [test ! -z "$GUROBI_LIBS"])

# Do final output.
AC_OUTPUT

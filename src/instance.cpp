/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
**/
#include <cstring>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <algorithm>
#include "common.hpp"
#include "instance.hpp"

#define NORM_PRECISION 10000

/* Class Item */

bool Item::operator<(const Item &o) const {
    throw_assert(ndims == o.ndims);
    if (abs(key-o.key) >= 1e-5) {
        return key < o.key;
    }
    for (int i = 0; i < ndims; i++) {
        if (w[i] != o.w[i]) {
            return w[i] < o.w[i];
        }
    }
    return demand < o.demand;
}

int Item::operator[](int i) const {
    throw_assert(i < ndims);
    return w[i];
}

int &Item::operator[](int i) {
    throw_assert(i < ndims);
    return w[i];
}

/* Class Instance */

void Instance::init() {
    relax_domains = false;
    binary = false;
    method = -3;
    vtype = 'I';
    ndims = 0;
    m = 0;
}

Instance::Instance() {
    init();
}

Instance::Instance(FILE *fin, ftype type) {
    init();
    read(fin, type);
}

Instance::Instance(const char *fname) {
    init();
    read(fname);
}

std::vector<Item> Instance::sorted_items() {
    std::vector<Item> sitems(items);
    std::stable_sort(all(sitems));
    std::reverse(all(sitems));
    return sitems;
}

void Instance::print() const {
    printf("Instance:\n");
    int p = 0;
    for (int i = 0; i < m; i++) {
        printf("i=%d (nopts: %d, demand: %d)\n", i+1, nopts[i], demands[i]);
        for (int q = 0; q < nopts[i]; q++) {
            printf("  opt=%d: (", q+1);
            for (int j = 0; j < ndims; j++) {
                if (j) {
                    printf(", ");
                }
                printf("%d", items[p][j]);
            }
            printf(")\n");
            p++;
        }
    }
}

void Instance::read(const char *fname) {
    FILE *fin = fopen(fname, "r");
    if (fin == NULL) {
        perror("fopen");
    }
    throw_assert(fin != NULL);
    if (check_ext(fname, ".vbp")) {
        read(fin, VBP);
    } else if (check_ext(fname, ".mvp")) {
        read(fin, MVP);
    } else {
        throw_error("Invalid file extension");
    }
    fclose(fin);
}

void Instance::read(FILE *fin, ftype type) {
    throw_assert(fscanf(fin, " #INSTANCE_BEGIN#") == 0);
    throw_assert(fscanf(fin, " $INSTANCE {") == 0);
    throw_assert(fscanf(fin, "%d", &ndims) == 1);
    throw_assert(ndims >= 1);

    if (type == MVP) {
        throw_assert(fscanf(fin, "%d", &nbtypes) == 1);
        throw_assert(nbtypes >= 1);
    } else {
        nbtypes = 1;
    }

    Ws.resize(nbtypes);
    Cs.resize(nbtypes);
    Qs.resize(nbtypes);
    for (int t = 0; t < nbtypes; t++) {
        Ws[t].resize(ndims);
        for (int d = 0; d < ndims; d++) {
            throw_assert(fscanf(fin, "%d", &Ws[t][d]) == 1);
            throw_assert(Ws[t][d] >= 0);
        }
        if (type == MVP) {
            throw_assert(fscanf(fin, "%d", &Cs[t]) == 1);
            throw_assert(fscanf(fin, "%d", &Qs[t]) == 1);
        } else {
            Cs[t] = 1;
            Qs[t] = -1;
        }
    }

    items.clear();
    nopts.clear();
    ctypes.clear();
    demands.clear();
    int it_count = 0;
    throw_assert(fscanf(fin, "%d", &m) == 1);
    for (int it_type = 0; it_type < m; it_type++) {
        int ti, bi;
        if (type == MVP) {
            throw_assert(fscanf(fin, "%d", &ti) == 1);
            throw_assert(ti >= 0);
            throw_assert(fscanf(fin, "%d", &bi) == 1);
            throw_assert(bi >= 0);
            demands.push_back(bi);
        } else {
            ti = 1;
            bi = -1;
        }
        nopts.push_back(ti);
        ctypes.push_back('*');

        int nfits = 0;
        for (int opt = 0; opt < ti; opt++) {
            items.push_back(Item(ndims));
            Item &item = items.back();
            if (ti > 1) {
                item.opt = opt;
            } else {
                item.opt = -1;
            }

            for (int d = 0; d < ndims; d++) {
                throw_assert(fscanf(fin, "%d", &item[d]) == 1);
                throw_assert(item[d] >= 0);
                if (item[d] != 0) {
                    item.nonzero.push_back(d);
                }
            }
            throw_assert(!item.nonzero.empty());

            if (type == VBP) {
                throw_assert(fscanf(fin, "%d", &bi) == 1);
                throw_assert(bi >= 0);
                demands.push_back(bi);
            }
            item.demand = bi;

            int S = 0;
            std::vector<int> maxW(ndims, 0);
            for (int d = 0; d < ndims; d++) {
                for (int t = 0; t < nbtypes; t++) {
                    maxW[d] = std::max(maxW[d], Ws[t][d]);
                }
            }
            for (int d = 0; d < ndims; d++) {
                if (maxW[d] > 0) {
                    S += round(
                        item[d]/static_cast<double>(maxW[d])*NORM_PRECISION);
                }
            }
            if (item.demand > 0) {
                bool fits = false;
                for (int t = 0; t < nbtypes; t++) {
                    fits = true;
                    for (int d = 0; d < ndims; d++) {
                        if (item[d] > Ws[t][d]) {
                            fits = false;
                            break;
                        }
                    }
                    if (fits) {
                        break;
                    }
                }
                nfits += fits;
            }
            item.key = S;
            item.type = it_type;
            item.id = it_count++;
        }
        if (bi > 0) {
            throw_assert(nfits >= 1);
        }
    }
    throw_assert(fscanf(fin, " } ;") <= 0);

    char buf[MAX_LEN];
    while (fscanf(fin, " $%[^{ \n]", buf) == 1) {
        if (!strcmp(buf, "VTYPE")) {
            throw_assert(fscanf(fin, " { %[^}, \n] } ;", buf) == 1);
            vtype = buf[0];
            throw_assert(vtype == 'C' || vtype == 'I');
        } else if (!strcmp(buf, "CTYPE")) {
            throw_assert(fscanf(fin, " {") == 0);
            ctypes.clear();
            for (int i = 0; i < m; i++) {
                if (i) throw_assert(fscanf(fin, " ,") == 0);
                throw_assert(fscanf(fin, " %[^}, \n]", buf) == 1);
                if (!strcmp(buf, ">")) {
                    ctypes.push_back('>');
                } else if (!strcmp(buf, "=")) {
                    ctypes.push_back('=');
                } else {
                    throw_assert(!strcmp(buf, "*"));
                    ctypes.push_back('*');
                }
            }
            throw_assert(fscanf(fin, " } ;") == 0);
        } else if (!strcmp(buf, "METHOD")) {
            throw_assert(fscanf(fin, " { %d } ;", &method) == 1);
            throw_assert(method >= MIN_METHOD && method <= MAX_METHOD);
        } else if (!strcmp(buf, "RELAX")) {
            int trelax = 0;
            throw_assert(fscanf(fin, " { %d } ;", &trelax) == 1);
            throw_assert(trelax == 0 || trelax == 1);
            relax_domains = trelax;
        } else if (!strcmp(buf, "BINARY")) {
            int tbinary = 0;
            throw_assert(fscanf(fin, " { %d } ;", &tbinary) == 1);
            throw_assert(tbinary == 0 || tbinary == 1);
            binary = tbinary;
        } else {
            printf("Invalid option '%s'!\n", buf);
            exit(1);
        }
    }
    throw_assert(fscanf(fin, " #INSTANCE_END#") <= 0);

    for (int i = 0; i < m; i++) {
        if (ctypes[i] == '*') {
            ctypes[i] = (demands[i] <= 1) ? '=' : '>';
        }
    }

    n = 0;
    for (int i = 0; i < m; i++) {
        n += demands[i];
    }

    nsizes = items.size();
}

void Instance::write(FILE *fout) const {
    fprintf(fout, "#INSTANCE_BEGIN#\n");
    fprintf(fout, "$INSTANCE{\n");
    fprintf(fout, "%d\n", ndims);

    fprintf(fout, "%d\n", nbtypes);

    for (int t = 0; t < nbtypes; t++) {
        for (int i = 0; i < ndims; i++) {
            fprintf(fout, " %d", Ws[t][i]);
        }
        fprintf(fout, " %d", Cs[t]);
        fprintf(fout, " %d\n", Qs[t]);
    }

    fprintf(fout, "%d\n", m);
    int p = 0;
    std::vector<int> rid(items.size());
    for (int it = 0; it < static_cast<int>(items.size()); it++) {
        rid[items[it].id] = it;
    }
    for (int i = 0; i < m; i++) {
        fprintf(fout, "%d %d\n", nopts[i], demands[i]);
        for (int q = 0; q < nopts[i]; q++) {
            for (int j = 0; j < ndims; j++) {
                fprintf(fout, " %d", items[rid[p]][j]);
            }
            fprintf(fout, "\n");
            p++;
        }
    }
    fprintf(fout, "};\n");

    fprintf(fout, "$VTYPE{%c};\n", vtype);

    fprintf(fout, "$CTYPE{");
    for (int i = 0; i < m; i++) {
        if (i) fprintf(fout, ",");
        fprintf(fout, "%c", ctypes[i]);
    }
    fprintf(fout, "};\n");

    fprintf(fout, "$METHOD{%d};\n", method);

    fprintf(fout, "$RELAX{%d};\n", relax_domains);

    fprintf(fout, "$BINARY{%d};\n", binary);

    fprintf(fout, "#INSTANCE_END#\n");
}

"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2017, Filipe Brandao
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
"""
from __future__ import print_function
from __future__ import division
from builtins import str, map, object, range, zip, sorted

import svgwrite
import colorsys
from random import random


SPACE_SIZE = 3
CSS_STYLES = """
    .background { fill: white; }
    .line {stroke: darkgrey; stroke-width: 0.5;}
    .rect {stroke: black; stroke-width:0.05; fill:lightgrey; fill-opacity:50%;}
    .sheet {stroke:black; stroke-width:0.5; fill:none;}
    .label {font-size: 3px; font-family: monospace; fill:black;}
    .label2 {font-size: 4px; font-family: monospace; fill:black;}
    .header {font-size: 5px; fill:black;}
"""


class HsvColorGenerator(object):
    """
    Mostly-random Color Generator
    http://variable-scope.com/posts/creating-a-mostly-random-color-generator
    """

    def __init__(self, hue=None, saturation=None, value=None):
        self.h_func = self._channel_picker(hue, scale=360)
        self.s_func = self._channel_picker(saturation)
        self.v_func = self._channel_picker(value)

    def __call__(self):
        """Returns a random color based on configured functions."""
        hsv = self.h_func(), self.s_func(), self.v_func()
        return tuple(
            [int(round(value * 255)) for value in colorsys.hsv_to_rgb(*hsv)])

    def _channel_picker(self, value, scale=1):
        """Returns a function to create (restricted) random values."""
        if value is None:
            return random
        scaler = self._scale_input(scale)
        if isinstance(value, tuple):
            start, stop = map(scaler, value)
            return lambda: random() * (stop - start) + start
        else:
            value = scaler(value)
            return lambda: value

    def _scale_input(self, scale_max):
        """Creates a function that compresses an range to [0-1]."""
        scale_max = float(scale_max)
        return lambda num: num / scale_max


def draw_solution(sheet_types, solution, dimension, demand, fprefix):
    """Generate .svg files with the solution."""

    def get_dims(name, scale):
        w, h = dimension[name]
        return w*scale, h*scale

    def get_name(name):
        return name[:name.find("[")]

    def get_number(name):
        return int("".join(c for c in "0123456789" if c in get_name(name)))

    maxW = max(
        get_dims(sheet, 1)[0] for sheet in sheet_types if sheet in solution
    )
    maxH = max(
        get_dims(sheet, 1)[1] for sheet in sheet_types if sheet in solution
    )

    SCALE = 500.0/maxW
    maxW *= SCALE
    maxH *= SCALE

    generator = HsvColorGenerator(
        hue=(0/3.0*255, 3/3.0*255), value=(0.7, 0.9), saturation=(0.4, 0.6)
    )

    colors = [generator() for i in range(100)]
    colors = [
        "#{:x}{:x}{:x}".format(r_g_b[0], r_g_b[1], r_g_b[2])
        for r_g_b in colors
    ]

    line_colors = ["red", "blue", "green", "orange", "yellow"]

    def draw_sheet(fname, W, H, patt):
        svgwidth, svgheight = W+2*SPACE_SIZE, H+2*SPACE_SIZE
        svg_scale = 800.0/svgwidth
        dwg = svgwrite.Drawing(
            fname, size=(svgwidth*svg_scale, svgheight*svg_scale)
        )
        dwg.viewbox(0, 0, svgwidth, svgheight)
        dwg.defs.add(dwg.style(CSS_STYLES))
        dwg.add(dwg.rect(size=("100%", "100%"), class_="background"))

        def group(classname):
            return dwg.add(dwg.g(class_=classname))

        # setup element groups
        lines = group("line")
        rects = group("rect")
        sheets = group("sheet")
        labels = group("label")

        sheets.add(dwg.rect(insert=(SPACE_SIZE, SPACE_SIZE), size=(W, H)))

        def draw_stage(stage, patt, x1, y1, x2, y2):
            x, y = x1, y1
            for it in patt:
                w, h = get_dims(it, SCALE)
                if it not in solution:
                    if it.startswith("I"):
                        name = get_name(it)
                        if demand[name] > 0:
                            demand[name] -= 1
                            ind = get_number(it)
                            rects.add(
                                dwg.rect(
                                    insert=(x+0.25, y+0.25),
                                    size=(w-0.5, h-0.5),
                                    fill=colors[ind % len(colors)]
                                )
                            )
                            labels.add(dwg.text(it, insert=(x+0.3, y+2.5)))
                        else:
                            continue
                elif solution[it] != []:
                    draw_stage(stage+1, solution[it].pop(), x, y, x+w, y+h)
                else:
                    continue
                if stage % 2 != 0:
                    y += h
                    lines.add(dwg.line(
                        start=(x1+0.25, y), end=(x2-0.25, y),
                        stroke=line_colors[stage % len(line_colors)]
                    ))
                else:
                    x += w
                    lines.add(dwg.line(
                        start=(x, y1+0.25), end=(x, y2-0.25),
                        stroke=line_colors[stage % len(line_colors)]
                    ))

        draw_stage(1, patt, SPACE_SIZE, SPACE_SIZE, SPACE_SIZE+W, SPACE_SIZE+H)

        dwg.save()

    cnt = 0
    for typ in sheet_types:
        if typ in solution:
            W, H = get_dims(typ, SCALE)
            for patt in solution[typ]:
                cnt += 1
                fname = "{}_{}.svg".format(fprefix, cnt)
                draw_sheet(fname, W, H, patt)

    for name in demand:
        if demand[name] != 0:
            print(name, demand[name])
        assert demand[name] == 0

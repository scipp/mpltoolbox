# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .tool import Tool
from .utils import parse_kwargs
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
import uuid
from typing import Tuple


class Line:
    def __init__(
        self,
        x: float,
        y: float,
        number: int,
        ax: Axes,
        n=2,
        hide_vertices: bool = False,
        **kwargs,
    ):
        self._max_clicks = n
        self._ax = ax
        kwargs = parse_kwargs(kwargs, number)
        if set(["ls", "linestyle"]).isdisjoint(set(kwargs.keys())):
            kwargs["ls"] = "solid"
        if "marker" not in kwargs:
            kwargs["marker"] = "o"
        (self._line,) = self._ax.plot(x, y, **kwargs)
        if hide_vertices:
            self.mec = "None"
            self.mfc = "None"
        self._line.parent = self
        self.id = uuid.uuid1().hex

    def __repr__(self):
        return f"Line: x={self.x}, y={self.y}, color={self.color}"

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self.x)

    def move_vertex(self, event: Event, ind: int):
        new_data = self.xy
        if ind is None:
            ind = -1
        new_data[0][ind] = event.xdata
        new_data[1][ind] = event.ydata
        self.xy = new_data

    def after_persist_vertex(self, event: Event):
        # Duplicate the last vertex
        new_data = self.xy
        self.xy = (
            np.append(new_data[0], new_data[0][-1]),
            np.append(new_data[1], new_data[1][-1]),
        )

    @property
    def x(self) -> np.ndarray:
        return self._line.get_xdata()

    @x.setter
    def x(self, x: np.ndarray):
        self._line.set_xdata(x)

    @property
    def y(self) -> np.ndarray:
        return self._line.get_ydata()

    @y.setter
    def y(self, y: np.ndarray):
        self._line.set_ydata(y)

    @property
    def xy(self) -> Tuple[np.ndarray]:
        return self._line.get_data()

    @xy.setter
    def xy(self, xy: Tuple[np.ndarray]):
        self._line.set_data(xy)

    @property
    def color(self) -> str:
        return self._line.get_color()

    @color.setter
    def color(self, c: str):
        self._line.set_color(c)

    @property
    def markerfacecolor(self) -> str:
        return self._line.get_markerfacecolor()

    @markerfacecolor.setter
    def markerfacecolor(self, color: str):
        self._line.set_markerfacecolor(color)

    @property
    def markeredgecolor(self) -> str:
        return self._line.get_markeredgecolor()

    @markeredgecolor.setter
    def markeredgecolor(self, color: str):
        self._line.set_markeredgecolor(color)

    @property
    def mfc(self) -> str:
        return self.markerfacecolor

    @mfc.setter
    def mfc(self, color: str):
        self.markerfacecolor = color

    @property
    def mec(self) -> str:
        return self.markeredgecolor

    @mec.setter
    def mec(self, color: str):
        self.markeredgecolor = color

    @property
    def marker(self) -> str:
        return self._line.get_marker()

    @marker.setter
    def marker(self, m: str):
        self._line.set_marker(m)

    @property
    def linestyle(self) -> str:
        return self._line.get_linestyle()

    @linestyle.setter
    def linestyle(self, style: str):
        self._line.set_linestyle(style)

    @property
    def ls(self) -> str:
        return self.linestyle

    @ls.setter
    def ls(self, style: str):
        self.linestyle = style

    @property
    def linewidth(self) -> float:
        return self._line.get_linewidth()

    @linewidth.setter
    def linewidth(self, width: float):
        self._line.set_linewidth(width)

    @property
    def lw(self) -> float:
        return self.linewidth

    @lw.setter
    def lw(self, width: float):
        self.linewidth = width

    def remove(self):
        self._line.remove()

    def set_picker(self, pick: float):
        self._line.set_picker(pick)

    def is_moveable(self, artist: Artist):
        return True

    def is_draggable(self, artist: Artist):
        return True

    def is_removable(self, artist: Artist):
        return True


Lines = partial(Tool, spawner=Line)
Lines.__doc__ = """
Lines: Add lines to the supplied axes.

Controls:
  - Left-click to make new lines
  - Left-click and hold on line vertex to move vertex
  - Right-click and hold to drag/move the entire line
  - Middle-click to delete line

:param ax: The Matplotlib axes to which the Lines tool will be attached.
:param n: The number of vertices for each line. Default is 2.
:param autostart: Automatically activate the tool upon creation if `True`.
:param hide_vertices: Hide vertices if `True`.
:param on_create: Callback that fires when a line is created.
:param on_change: Callback that fires when a line is modified.
:param on_remove: Callback that fires when a line is removed.
:param on_vertex_press: Callback that fires when a vertex is left-clicked.
:param on_vertex_move: Callback that fires when a vertex is moved.
:param on_vertex_release: Callback that fires when a vertex is released.
:param on_drag_press: Callback that fires when a line is right-clicked.
:param on_drag_move: Callback that fires when a line is dragged.
:param on_drag_release: Callback that fires when a line is released.
:param kwargs: Matplotlib line parameters used for customization.
    Each parameter can be a single item (it will apply to all lines),
    a list of items (one entry per line), or a callable (which will be
    called every time a new line is created).
"""

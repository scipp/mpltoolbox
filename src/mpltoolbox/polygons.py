# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .tool import Tool
from .utils import parse_kwargs
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from typing import Tuple
import uuid


class Polygon:
    def __init__(
        self,
        x: float,
        y: float,
        number: int,
        ax: Axes,
        hide_vertices: bool = False,
        **kwargs,
    ):
        self._max_clicks = 0
        self._ax = ax
        line_kwargs = parse_kwargs(kwargs, number)
        fill_kwargs = {}
        for arg in ("ec", "edgecolor", "fc", "facecolor", "alpha"):
            if arg in line_kwargs:
                fill_kwargs[arg] = line_kwargs.pop(arg)
        if set(["mfc", "markerfacecolor"]).isdisjoint(set(line_kwargs.keys())):
            line_kwargs["mfc"] = "None"
        if set(["ls", "linestyle"]).isdisjoint(set(line_kwargs.keys())):
            line_kwargs["ls"] = "solid"
        if "marker" not in line_kwargs:
            line_kwargs["marker"] = "o"
        if "alpha" not in fill_kwargs:
            fill_kwargs["alpha"] = 0.05
        if set(["fc", "facecolor"]).isdisjoint(set(fill_kwargs.keys())):
            fill_kwargs["fc"] = None

        (self._vertices,) = self._ax.plot(x, y, **line_kwargs)
        if fill_kwargs["fc"] is None:
            fill_kwargs["fc"] = self._vertices.get_color()
        (self._fill,) = self._ax.fill(x, y, **fill_kwargs)
        if hide_vertices:
            self.mec = "None"
            self.mfc = "None"
        self._fill.parent = self
        self._vertices.parent = self
        self.id = uuid.uuid1().hex
        self._distance_from_first_point = 0.05
        self._first_point_position_data = (x, y)
        self._first_point_position_axes = self._data_to_axes_transform(x, y)

    def __repr__(self):
        return (
            f"Polygon: x={self.x}, y={self.y}, "
            f"edgecolor={self.edgecolor}, facecolor={self.facecolor}"
        )

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self.x)

    def after_persist_vertex(self, event: Event):
        new_data = self.xy
        self.xy = (
            np.append(new_data[0], new_data[0][-1]),
            np.append(new_data[1], new_data[1][-1]),
        )

    def _data_to_axes_transform(self, x: float, y: float) -> Tuple[float]:
        trans = self._ax.transData.transform((x, y))
        return self._ax.transAxes.inverted().transform(trans)

    def _get_distance_from_first_point(self, x: float, y: float) -> float:
        xdisplay, ydisplay = self._data_to_axes_transform(x, y)
        dist = np.sqrt(
            (xdisplay - self._first_point_position_axes[0]) ** 2
            + (ydisplay - self._first_point_position_axes[1]) ** 2
        )
        return dist

    def move_vertex(self, event: Event, ind: int):
        x = event.xdata
        y = event.ydata
        if self._get_distance_from_first_point(x, y) < self._distance_from_first_point:
            x = self._first_point_position_data[0]
            y = self._first_point_position_data[1]
            self._max_clicks = len(self)
        else:
            self._max_clicks = 0
        new_data = self.xy
        if ind is None:
            ind = -1
        elif ind in (0, len(new_data[0])):
            ind = [0, -1]
        new_data[0][ind] = x
        new_data[1][ind] = y
        self.xy = new_data
        self._update_fill()

    def _update_fill(self):
        self._fill.set_xy(np.array(self._vertices.get_data()).T)

    @property
    def x(self) -> np.ndarray:
        return self._vertices.get_xdata()

    @x.setter
    def x(self, x: np.ndarray):
        self._vertices.set_xdata(x)
        self._update_fill()

    @property
    def y(self) -> np.ndarray:
        return self._vertices.get_ydata()

    @y.setter
    def y(self, y: np.ndarray):
        self._vertices.set_ydata(y)
        self._update_fill()

    @property
    def xy(self) -> Tuple[np.ndarray]:
        return self._vertices.get_data()

    @xy.setter
    def xy(self, xy: Tuple[np.ndarray]):
        self._vertices.set_data(xy)
        self._update_fill()

    @property
    def edgecolor(self) -> str:
        return self._vertices.get_color()

    @edgecolor.setter
    def edgecolor(self, c: str):
        self._vertices.set_color(c)

    @property
    def facecolor(self) -> str:
        return self._fill.get_facecolor()

    @facecolor.setter
    def facecolor(self, c: str):
        self._fill.set_facecolor(c)

    @property
    def markerfacecolor(self) -> str:
        return self._vertices.get_markerfacecolor()

    @markerfacecolor.setter
    def markerfacecolor(self, color: str):
        self._vertices.set_markerfacecolor(color)

    @property
    def markeredgecolor(self) -> str:
        return self._vertices.get_markeredgecolor()

    @markeredgecolor.setter
    def markeredgecolor(self, color: str):
        self._vertices.set_markeredgecolor(color)

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
        return self._vertices.get_marker()

    @marker.setter
    def marker(self, m: str):
        self._vertices.set_marker(m)

    @property
    def linestyle(self) -> str:
        return self._vertices.get_linestyle()

    @linestyle.setter
    def linestyle(self, style: str):
        self._vertices.set_linestyle(style)

    @property
    def ls(self) -> str:
        return self.linestyle

    @ls.setter
    def ls(self, style: str):
        self.linestyle = style

    @property
    def linewidth(self) -> float:
        return self._vertices.get_linewidth()

    @linewidth.setter
    def linewidth(self, width: float):
        self._vertices.set_linewidth(width)

    @property
    def lw(self) -> float:
        return self.linewidth

    @lw.setter
    def lw(self, width: float):
        self.linewidth = width

    def remove(self):
        self._fill.remove()
        self._vertices.remove()

    def set_picker(self, pick: float):
        self._fill.set_picker(pick)
        self._vertices.set_picker(pick)

    def is_moveable(self, artist: Artist):
        return artist is self._vertices

    def is_draggable(self, artist: Artist):
        return artist is self._fill

    def is_removable(self, artist: Artist):
        return artist is self._fill


Polygons = partial(Tool, spawner=Polygon)
Polygons.__doc__ = """
Polygons: Add closed polygons to the supplied axes.

Controls:
  - Left-click to make new polygons
  - Left-click and hold on polygon vertex to move vertex
  - Right-click and hold to drag/move the entire polygon
  - Middle-click to delete polygon

:param ax: The Matplotlib axes to which the Polygons tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param hide_vertices: Hide vertices if `True`.
:param on_create: Callback that fires when a polygon is created.
:param on_change: Callback that fires when a polygon is modified.
:param on_remove: Callback that fires when a polygon is removed.
:param on_vertex_press: Callback that fires when a vertex is left-clicked.
:param on_vertex_move: Callback that fires when a vertex is moved.
:param on_vertex_release: Callback that fires when a vertex is released.
:param on_drag_press: Callback that fires when a polygon is right-clicked.
:param on_drag_move: Callback that fires when a polygon is dragged.
:param on_drag_release: Callback that fires when a polygon is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all polygons),
    a list of items (one entry per polygon), or a callable (which will be
    called every time a new polygon is created).
"""

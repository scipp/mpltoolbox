# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .lines import Line
from .tool import Tool
from functools import partial
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event


class Point(Line):
    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)
        self._max_clicks = 1

    def __repr__(self):
        return f"Point: x={self.x}, y={self.y}, color={self.color}"

    def __str__(self):
        return repr(self)

    def __len__(self):
        return 1

    @property
    def x(self) -> float:
        return self._line.get_xdata()[0]

    @x.setter
    def x(self, x: float):
        self._line.set_xdata([x])

    @property
    def y(self) -> float:
        return self._line.get_ydata()[0]

    @y.setter
    def y(self, y: float):
        self._line.set_ydata([y])

    @property
    def xy(self) -> float:
        data = self._line.get_data()
        return (data[0][0], data[1][0])

    @xy.setter
    def xy(self, xy: float):
        self._line.set_data([xy[0]], [xy[1]])

    def move_vertex(self, event: Event, ind: int):
        self.x = event.xdata
        self.y = event.ydata

    def after_persist_vertex(self, event: Event):
        return


Points = partial(Tool, spawner=Point)
Points.__doc__ = """
Points: Add points to the supplied axes.

Controls:
  - Left-click to make new points
  - Left-click and hold on point to move point
  - Middle-click to delete point

:param ax: The Matplotlib axes to which the Points tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param on_create: Callback that fires when a point is created.
:param on_change: Callback that fires when a point is modified.
:param on_remove: Callback that fires when a point is removed.
:param on_vertex_press: Callback that fires when a point is left-clicked.
:param on_vertex_move: Callback that fires when a point is moved.
:param on_vertex_release: Callback that fires when a point is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all points),
    a list of items (one entry per point), or a callable (which will be
    called every time a new point is created).
"""

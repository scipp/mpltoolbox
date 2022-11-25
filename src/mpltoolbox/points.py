# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .event_handler import EventHandler
from .utils import parse_kwargs
from functools import partial
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event
from typing import Tuple
import uuid


class Point:

    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        self._max_clicks = 1
        self._ax = ax
        kwargs = parse_kwargs(kwargs, number)
        if set(['ls', 'linestyle']).isdisjoint(set(kwargs.keys())):
            kwargs['ls'] = 'solid'
        if 'marker' not in kwargs:
            kwargs['marker'] = 'o'
        self._point, = self._ax.plot(x, y, **kwargs)
        self._point.parent = self
        self.id = uuid.uuid1().hex

    def __repr__(self):
        return f'Point: x={self.x}, y={self.y}, color={self.color}'

    def __str__(self):
        return repr(self)

    def __len__(self):
        return 1

    @property
    def x(self) -> float:
        return self._point.get_xdata()[0]

    @x.setter
    def x(self, x: float):
        self._point.set_xdata(x)

    @property
    def y(self) -> float:
        return self._point.get_ydata()[0]

    @y.setter
    def y(self, y: float):
        self._point.set_ydata(y)

    @property
    def xy(self) -> float:
        return self._point.get_data()[0]

    @xy.setter
    def xy(self, xy: float):
        self._point.set_data(xy)

    @property
    def color(self) -> str:
        return self._point.get_color()

    @color.setter
    def color(self, c):
        self._point.set_color(c)

    @property
    def markerfacecolor(self) -> str:
        return self._point.get_markerfacecolor()

    @markerfacecolor.setter
    def markerfacecolor(self, color):
        self._point.set_markerfacecolor(color)

    @property
    def markeredgecolor(self) -> str:
        return self._point.get_markeredgecolor()

    @markeredgecolor.setter
    def markerfacecolor(self, color):
        self._point.set_markeredgecolor(color)

    @property
    def mfc(self) -> str:
        return self.markerfacecolor

    @mfc.setter
    def mfc(self, color):
        self.markerfacecolor = color

    @property
    def mec(self) -> str:
        return self.markeredgecolor

    @mec.setter
    def mec(self, color):
        self.markeredgecolor = color

    @property
    def marker(self) -> str:
        return self._point.get_marker()

    @marker.setter
    def marker(self, m):
        self._point.set_marker(m)

    def remove(self):
        self._point.remove()

    @property
    def artist(self) -> str:
        return self._point

    def set_picker(self, pick):
        self._point.set_picker(pick)

    def is_moveable(self, artist):
        return True

    def is_draggable(self, artist):
        return True

    def is_removable(self, artist):
        return True

    def move_vertex(self, event: Event, ind: int):
        self.x = event.xdata
        self.y = event.ydata

    def after_persist_vertex(self, event):
        return


Points = partial(EventHandler, spawner=Point)
"""
Add points to the supplied axes.

Controls:
  - Left-click to make new points
  - Left-click and hold on point to move point
  - Middle-click to delete point

:param ax: The Matplotlib axes to which the Points tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param on_create: Callback that fires when a point is created.
:param on_remove: Callback that fires when a point is removed.
:param on_vertex_press: Callback that fires when a point is left-clicked.
:param on_vertex_move: Callback that fires when a point is moved.
:param on_vertex_release: Callback that fires when a point is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all points),
    a list of items (one entry per point), or a callable (which will be
    called every time a new point is created).
"""

# class Points(Lines):
#     """
#     Add points to the supplied axes.

#     Controls:
#       - Left-click to make new points
#       - Left-click and hold on point to move point
#       - Middle-click to delete point

#     :param ax: The Matplotlib axes to which the Points tool will be attached.
#     :param autostart: Automatically activate the tool upon creation if `True`.
#     :param on_create: Callback that fires when a point is created.
#     :param on_remove: Callback that fires when a point is removed.
#     :param on_vertex_press: Callback that fires when a point is left-clicked.
#     :param on_vertex_move: Callback that fires when a point is moved.
#     :param on_vertex_release: Callback that fires when a point is released.
#     :param kwargs: Matplotlib parameters used for customization.
#         Each parameter can be a single item (it will apply to all points),
#         a list of items (one entry per point), or a callable (which will be
#         called every time a new point is created).
#     """

#     def __init__(self, ax: Axes, **kwargs):
#         super().__init__(ax, n=1, **kwargs)
#         self._maker = Point

#     def _new_line_pos(self, x: float, y: float) -> Tuple[float]:
#         return [x], [y]

#     # def _after_line_creation(self, event):
#     #     self._finalize_line(event)

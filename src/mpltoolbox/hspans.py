# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .patch import Patch
from .tool import Tool
from functools import partial
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event
from typing import Tuple


class Hspan(Patch):
    def __init__(
        self, x: float, y: float, number: int, ax: Axes, hide_median=False, **kwargs
    ):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)
        self._vertices.set_transform(self._patch.get_transform())
        self._median = self._ax.axhline(y, ls="dashed", color=self.edgecolor)
        if hide_median:
            self._median.set_visible(False)

    def __repr__(self):
        return (
            f"VSpan: bottom={self.bottom}, top={self.top}, "
            f"edgecolor={self.edgecolor}, facecolor={self.facecolor}"
        )

    def _update_vertices(self):
        super()._update_vertices()
        corners = self._patch.get_xy()
        mid = 0.5 * (corners[0, 1] + corners[1, 1])
        self._median.set_ydata([mid, mid])

    def _make_patch(self, x, y, **kwargs):
        self._patch = self._ax.axhspan(y, y, **kwargs)

    def _make_vertices(self) -> Tuple[float]:
        return ([0.5, 0.5], [self.bottom, self.top])

    def move_vertex(self, event: Event, ind: int):
        y = event.ydata
        if ind == 0:
            self.bottom = y
        else:
            self.top = y

    def remove(self):
        super().remove()
        self._median.remove()

    @property
    def bottom(self) -> float:
        return self._patch.get_xy()[0, 1]

    @bottom.setter
    def bottom(self, y: float):
        corners = self._patch.get_xy()
        for i in [0, 3]:
            corners[i, 1] = y
        if len(corners) > 3:
            corners[4, 1] = y
        else:
            corners += [corners[0, 0], y]
        self._patch.set_xy(corners)
        self._update_vertices()

    @property
    def top(self) -> float:
        return self._patch.get_xy()[1, 1]

    @top.setter
    def top(self, y: float):
        corners = self._patch.get_xy()
        for i in [1, 2]:
            corners[i, 1] = y
        self._patch.set_xy(corners)
        self._update_vertices()

    @property
    def height(self) -> float:
        corners = self._patch.get_xy()
        return corners[1, 1] - corners[0, 1]

    @property
    def xy(self) -> Tuple[float]:
        corners = self._patch.get_xy().copy()
        return (corners[:, 0], corners[:, 1])

    @xy.setter
    def xy(self, xy: Tuple[float]):
        corners = self._patch.get_xy()
        corners[:, 1] = xy[1]
        self._patch.set_xy(corners)
        self._update_vertices()


Hspans = partial(Tool, spawner=Hspan)
Hspans.__doc__ = """
Hspans: Add horizontal spans to the supplied axes.

Controls:
  - Left-click and hold to make new spans
  - Right-click and hold to drag/move span
  - Middle-click to delete span

:param ax: The Matplotlib axes to which the Hspans tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param hide_vertices: Hide vertices if `True`.
:param hide_median: Hide median line if `True`.
:param on_create: Callback that fires when a span is created.
:param on_change: Callback that fires when a span is modified.
:param on_remove: Callback that fires when a span is removed.
:param on_vertex_press: Callback that fires when a vertex is left-clicked.
:param on_vertex_move: Callback that fires when a vertex is moved.
:param on_vertex_release: Callback that fires when a vertex is released.
:param on_drag_press: Callback that fires when a span is right-clicked.
:param on_drag_move: Callback that fires when a span is dragged.
:param on_drag_release: Callback that fires when a span is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all spans),
    a list of items (one entry per span), or a callable (which will be
    called every time a new span is created).
"""

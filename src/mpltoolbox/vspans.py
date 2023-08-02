# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .patch import Patch
from .tool import Tool
from functools import partial
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event
from typing import Tuple


class Vspan(Patch):
    def __init__(
        self,
        x: float,
        y: float,
        number: int,
        ax: Axes,
        hide_median: bool = False,
        **kwargs,
    ):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)
        self._vertices.set_transform(self._patch.get_transform())
        self._median = self._ax.axvline(x, ls="dashed", color=self.edgecolor)
        if hide_median:
            self._median.set_visible(False)

    def __repr__(self):
        return (
            f"VSpan: left={self.left}, right={self.right}, "
            f"edgecolor={self.edgecolor}, facecolor={self.facecolor}"
        )

    def _update_vertices(self):
        super()._update_vertices()
        corners = self._patch.get_xy()
        mid = 0.5 * (corners[0, 0] + corners[2, 0])
        self._median.set_xdata([mid, mid])

    def _make_patch(self, x: float, y: float, **kwargs):
        self._patch = self._ax.axvspan(x, x, **kwargs)

    def _make_vertices(self) -> Tuple[float]:
        return ([self.left, self.right], [0.5, 0.5])

    def move_vertex(self, event: Event, ind: int):
        x = event.xdata
        if ind == 0:
            self.left = x
        else:
            self.right = x

    def remove(self):
        super().remove()
        self._median.remove()

    @property
    def left(self) -> float:
        return self._patch.get_xy()[0, 0]

    @left.setter
    def left(self, x: float):
        corners = self._patch.get_xy()
        for i in [0, 1]:
            corners[i, 0] = x
        if len(corners) > 3:
            corners[4, 0] = x
        else:
            corners += [x, corners[0, 1]]
        self._patch.set_xy(corners)
        self._update_vertices()

    @property
    def right(self) -> float:
        return self._patch.get_xy()[2, 0]

    @right.setter
    def right(self, x: float):
        corners = self._patch.get_xy()
        for i in [2, 3]:
            corners[i, 0] = x
        self._patch.set_xy(corners)
        self._update_vertices()

    @property
    def width(self) -> float:
        corners = self._patch.get_xy()
        return corners[2, 0] - corners[0, 0]

    @property
    def xy(self) -> Tuple[float]:
        corners = self._patch.get_xy().copy()
        return (corners[:, 0], corners[:, 1])

    @xy.setter
    def xy(self, xy: Tuple[float]):
        corners = self._patch.get_xy()
        corners[:, 0] = xy[0]
        self._patch.set_xy(corners)
        self._update_vertices()


Vspans = partial(Tool, spawner=Vspan)
Vspans.__doc__ = """
Vspans: Add vertical spans to the supplied axes.

Controls:
  - Left-click and hold to make new spans
  - Right-click and hold to drag/move span
  - Middle-click to delete span

:param ax: The Matplotlib axes to which the Vspans tool will be attached.
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

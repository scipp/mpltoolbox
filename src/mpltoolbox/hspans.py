# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

from functools import partial

from matplotlib.backend_bases import Event
from matplotlib.pyplot import Axes

from .patch import Patch
from .tool import Tool


class Hspan(Patch):
    def __init__(
        self, x: float, y: float, number: int, ax: Axes, hide_median=False, **kwargs
    ):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)
        self._median = self._ax.axhline(y, ls="dashed", color=self.edgecolor)
        self._vertices.set_transform(self._median.get_transform())
        if hide_median:
            self._median.set_visible(False)

    def __repr__(self):
        return (
            f"VSpan: bottom={self.bottom}, top={self.top}, "
            f"edgecolor={self.edgecolor}, facecolor={self.facecolor}"
        )

    def _update_vertices(self):
        super()._update_vertices()
        mid = 0.5 * (self.bottom + self.top)
        self._median.set_ydata([mid, mid])

    def _make_patch(self, x, y, **kwargs):
        self._patch = self._ax.axhspan(y, y, **kwargs)

    def _make_vertices(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return ([0.5, 0.5], [self.bottom, self.top])

    def move_vertex(self, event: Event, ind: int, **ignored):
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
        xy = self._patch.get_xy()
        if len(xy) > 2:
            return xy[0, 1]
        return xy[1]

    @bottom.setter
    def bottom(self, y: float):
        xy = self._patch.get_xy()
        if len(xy) > 2:
            for i in [0, 3]:
                xy[i, 1] = y
            if len(xy) > 3:
                xy[4, 1] = y
            else:
                xy += [xy[0, 0], y]
            self._patch.set_xy(xy)
        else:
            self._patch.set(height=xy[1] - y + self.height, xy=(0, y))
        self._update_vertices()

    @property
    def top(self) -> float:
        xy = self._patch.get_xy()
        if len(xy) > 2:
            return xy[1, 1]
        return xy[1] + self.height

    @top.setter
    def top(self, y: float):
        xy = self._patch.get_xy()
        if len(xy) > 2:
            for i in [1, 2]:
                xy[i, 1] = y
            self._patch.set_xy(xy)
        else:
            self._patch.set(height=y - xy[1])
        self._update_vertices()

    @property
    def height(self) -> float:
        if hasattr(self._patch, "get_height"):
            return self._patch.get_height()
        corners = self._patch.get_xy()
        return corners[1, 1] - corners[0, 1]

    @property
    def xy(self) -> tuple[float, float]:
        return (0, self.bottom)

    @xy.setter
    def xy(self, value: tuple[float, float]):
        _xy = self._patch.get_xy()
        if len(_xy) > 2:
            _xy[:, 1] += value[1] - _xy[0, 1]
        else:
            _xy = (0, value[1])
        self._patch.set_xy(_xy)
        self._update_vertices()

    def set(self, **kwargs):
        super().set(**kwargs)
        self._median.set(**kwargs)


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

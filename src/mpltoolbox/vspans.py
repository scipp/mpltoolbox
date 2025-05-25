# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

from functools import partial

from matplotlib.backend_bases import Event
from matplotlib.pyplot import Axes

from .patch import Patch
from .tool import Tool


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
        self._median = self._ax.axvline(x, ls="dashed", color=self.edgecolor)
        self._vertices.set_transform(self._median.get_transform())
        if hide_median:
            self._median.set_visible(False)

    def __repr__(self):
        return (
            f"VSpan: left={self.left}, right={self.right}, "
            f"edgecolor={self.edgecolor}, facecolor={self.facecolor}"
        )

    def _update_vertices(self):
        super()._update_vertices()
        mid = 0.5 * (self.left + self.right)
        self._median.set_xdata([mid, mid])

    def _make_patch(self, x: float, y: float, **kwargs):
        self._patch = self._ax.axvspan(x, x, **kwargs)

    def _make_vertices(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return ([self.left, self.right], [0.5, 0.5])

    def move_vertex(self, event: Event, ind: int, **ignored):
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
        xy = self._patch.get_xy()
        if len(xy) > 2:
            return xy[0, 0]
        return xy[0]

    @left.setter
    def left(self, x: float):
        xy = self._patch.get_xy()
        if len(xy) > 2:
            for i in [0, 1]:
                xy[i, 0] = x
            if len(xy) > 3:
                xy[4, 0] = x
            else:
                xy += [x, xy[0, 1]]
            self._patch.set_xy(xy)
        else:
            self._patch.set(width=xy[0] - x + self.width, xy=(x, 0))
        self._update_vertices()

    @property
    def right(self) -> float:
        xy = self._patch.get_xy()
        if len(xy) > 2:
            return xy[2, 0]
        return xy[0] + self.width

    @right.setter
    def right(self, x: float):
        xy = self._patch.get_xy()
        if len(xy) > 2:
            for i in [2, 3]:
                xy[i, 0] = x
            self._patch.set_xy(xy)
        else:
            self._patch.set_width(x - xy[0])
        self._update_vertices()

    @property
    def width(self) -> float:
        if hasattr(self._patch, "get_width"):
            return self._patch.get_width()
        corners = self._patch.get_xy()
        return corners[2, 0] - corners[0, 0]

    @property
    def xy(self) -> tuple[float, float]:
        return (self.left, 0)

    @xy.setter
    def xy(self, value: tuple[float, float]):
        _xy = self._patch.get_xy()
        if len(_xy) > 2:
            _xy[:, 0] += value[0] - _xy[0, 0]
        else:
            _xy = (value[0], 0)
        self._patch.set_xy(_xy)
        self._update_vertices()

    def set(self, **kwargs):
        super().set(**kwargs)
        self._median.set(**kwargs)


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

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .patch import Patch
from .tool import Tool
from functools import partial
from matplotlib import patches as mp
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event
import numpy as np
from typing import Tuple


class Rectangle(Patch):
    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)

    def __repr__(self):
        return (
            f"Rectangle: xy={self.xy}, width={self.width}, height={self.height}, "
            f"edgecolor={self.edgecolor}, facecolor={self.facecolor}"
        )

    def _make_patch(self, x: float, y: float, **kwargs):
        self._patch = mp.Rectangle((x, y), 0, 0, **kwargs)
        self._ax.add_patch(self._patch)

    def _make_vertices(self) -> Tuple[np.ndarray]:
        xy = self.xy
        w = self.width
        h = self.height
        xc = np.array([xy[0], xy[0] + w, xy[0] + w, xy[0], xy[0]])
        yc = np.array([xy[1], xy[1], xy[1] + h, xy[1] + h, xy[1]])
        x_mid = 0.5 * (xc[1:] + xc[:-1])
        y_mid = 0.5 * (yc[1:] + yc[:-1])
        x = np.empty(xc.size + x_mid.size - 1, dtype=float)
        y = np.empty(yc.size + y_mid.size - 1, dtype=float)
        x[0:-1:2] = xc[:-1]
        x[1::2] = x_mid
        y[0:-1:2] = yc[:-1]
        y[1::2] = y_mid
        return (x, y)

    def move_vertex(self, event: Event, ind: int):
        props = super().get_new_patch_props(event=event, ind=ind)
        props["xy"] = props.pop("corner")
        self.update(**props)

    @property
    def xy(self) -> Tuple[float]:
        return self._patch.get_xy()

    @xy.setter
    def xy(self, xy: Tuple[float]):
        self._patch.set_xy(xy)
        self._update_vertices()


Rectangles = partial(Tool, spawner=Rectangle)
Rectangles.__doc__ = """
Rectangles: Add rectangles to the supplied axes.

Controls:
  - Left-click and hold to make new rectangles
  - Right-click and hold to drag/move rectangle
  - Middle-click to delete rectangle

:param ax: The Matplotlib axes to which the Rectangles tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param hide_vertices: Hide vertices if `True`.
:param on_create: Callback that fires when a rectangle is created.
:param on_change: Callback that fires when a rectangle is modified.
:param on_remove: Callback that fires when a rectangle is removed.
:param on_vertex_press: Callback that fires when a vertex is left-clicked.
:param on_vertex_move: Callback that fires when a vertex is moved.
:param on_vertex_release: Callback that fires when a vertex is released.
:param on_drag_press: Callback that fires when a rectangle is right-clicked.
:param on_drag_move: Callback that fires when a rectangle is dragged.
:param on_drag_release: Callback that fires when a rectangle is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all rectangles),
    a list of items (one entry per rectangle), or a callable (which will be
    called every time a new rectangle is created).
"""

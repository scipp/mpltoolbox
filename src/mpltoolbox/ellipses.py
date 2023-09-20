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


class Ellipse(Patch):
    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)

    def __repr__(self):
        return (
            f"Ellipse: center={self.center}, width={self.width}, "
            f"height={self.height}, "
            f"edgecolor={self.edgecolor}, facecolor={self.facecolor}"
        )

    def _make_patch(self, x: float, y: float, **kwargs):
        self._patch = mp.Ellipse((x, y), 0, 0, **kwargs)
        self._ax.add_patch(self._patch)

    def _make_vertices(self) -> Tuple[np.ndarray]:
        center = self.center
        width = self.width
        height = self.height
        lft = center[0] - 0.5 * width
        cen = center[0]
        rgt = center[0] + 0.5 * width
        btm = center[1] - 0.5 * height
        mid = center[1]
        top = center[1] + 0.5 * height
        return (
            np.array([lft, cen, rgt, rgt, rgt, cen, lft, lft]),
            np.array([btm, btm, btm, mid, top, top, top, mid]),
        )

    def move_vertex(self, event: Event, ind: int):
        props = super().get_new_patch_props(event=event, ind=ind)
        center = list(self.center)
        if "width" in props:
            center[0] = props["corner"][0] + 0.5 * props["width"]
        if "height" in props:
            center[1] = props["corner"][1] + 0.5 * props["height"]
        props["center"] = center
        del props["corner"]
        self.update(**props)

    @property
    def center(self) -> Tuple[float]:
        return self._patch.get_center()

    @center.setter
    def center(self, center: Tuple[float]):
        self._patch.set_center(center)
        self._update_vertices()

    @property
    def xy(self) -> Tuple[float]:
        return self.center

    @xy.setter
    def xy(self, xy: Tuple[float]):
        self.center = xy


Ellipses = partial(Tool, spawner=Ellipse)
Ellipses.__doc__ = """
Ellipses: Add ellipses to the supplied axes.

Controls:
  - Left-click and hold to make new ellipses
  - Right-click and hold to drag/move ellipse
  - Middle-click to delete ellipse

:param ax: The Matplotlib axes to which the Ellipses tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param hide_vertices: Hide vertices if `True`.
:param on_create: Callback that fires when an ellipse is created.
:param on_change: Callback that fires when an ellipse is modified.
:param on_remove: Callback that fires when an ellipse is removed.
:param on_vertex_press: Callback that fires when a vertex is left-clicked.
:param on_vertex_move: Callback that fires when a vertex is moved.
:param on_vertex_release: Callback that fires when a vertex is released.
:param on_drag_press: Callback that fires when a ellipse is right-clicked.
:param on_drag_move: Callback that fires when a ellipse is dragged.
:param on_drag_release: Callback that fires when a ellipse is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all ellipses),
    a list of items (one entry per ellipse), or a callable (which will be
    called every time a new ellipse is created).
"""

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

# from .event_handler import EventHandler
from .patch import Patch
from .tool import Tool
from .utils import parse_kwargs
from functools import partial
from matplotlib import patches as mp
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event
from matplotlib.colors import to_rgb
import numpy as np
from typing import Tuple, List
import uuid

# def _vertices_from_rectangle(rectangle: mp.Patch) -> Tuple[List[float]]:
#     center = ellipse.center
#     width = ellipse.get_width()
#     height = ellipse.get_height()
#     return ([center[0] - 0.5 * width, center[0], center[0] + 0.5 * width, center[0]],
#             [center[1], center[1] - 0.5 * height, center[1], center[1] + 0.5 * height])


class Rectangle(Patch):

    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)

    def _make_patch(self, x, y, **kwargs):
        self._patch = mp.Rectangle((x, y), 0, 0, **kwargs)

    def __repr__(self):
        return (f'Rectangle: xy={self.xy}, width={self.width}, height={self.height}, '
                f'edgecolor={self.edgecolor}, facecolor={self.facecolor}')

    def _make_vertices(self):
        corners = self._patch.get_corners()
        xc = np.concatenate([corners[:, 0], [corners[0, 0]]])
        yc = np.concatenate([corners[:, 1], [corners[0, 1]]])
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
        self.update(**props)

    # def after_persist_vertex(self, event):
    #     return


Rectangles = partial(Tool, spawner=Rectangle)
"""
Add rectangles to the supplied axes.

Controls:
  - Left-click and hold to make new rectangles
  - Right-click and hold to drag/move rectangle
  - Middle-click to delete rectangle

:param ax: The Matplotlib axes to which the Rectangles tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param on_create: Callback that fires when a rectangle is created.
:param on_remove: Callback that fires when a rectangle is removed.
:param on_drag_press: Callback that fires when a rectangle is right-clicked.
:param on_drag_move: Callback that fires when a rectangle is dragged.
:param on_drag_release: Callback that fires when a rectangle is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all rectangles),
    a list of items (one entry per rectangle), or a callable (which will be
    called every time a new rectangle is created).
"""

# class Rectangles(EventHandler):
#     """
#     Add rectangles to the supplied axes.

#     Controls:
#       - Left-click and hold to make new rectangles
#       - Right-click and hold to drag/move rectangle
#       - Middle-click to delete rectangle

#     :param ax: The Matplotlib axes to which the Rectangles tool will be attached.
#     :param autostart: Automatically activate the tool upon creation if `True`.
#     :param on_create: Callback that fires when a rectangle is created.
#     :param on_remove: Callback that fires when a rectangle is removed.
#     :param on_drag_press: Callback that fires when a rectangle is right-clicked.
#     :param on_drag_move: Callback that fires when a rectangle is dragged.
#     :param on_drag_release: Callback that fires when a rectangle is released.
#     :param kwargs: Matplotlib parameters used for customization.
#         Each parameter can be a single item (it will apply to all rectangles),
#         a list of items (one entry per rectangle), or a callable (which will be
#         called every time a new rectangle is created).
#     """

#     def __init__(self, ax: Axes, **kwargs):

#         super().__init__(ax=ax, **kwargs)
#         self._spawner = Rectangle
#         self._max_clicks = 2

#     # def _resize_patch(self, event: Event):
#     #     if event.inaxes != self._ax:
#     #         return
#     #     patch = self.patches[-1]
#     #     x, y = patch.xy
#     #     patch.update(width=event.xdata - x, height=event.ydata - y)
#     #     self._draw()

#     def _move_vertex(self, event: Event, ind: int, motif):
#         if event.inaxes != self._ax:
#             return
#         x, y = motif._vertices.get_data()
#         if ind is None:
#             ind = 2
#         x[ind] = event.xdata
#         y[ind] = event.ydata
#         opp = (ind + 2) % 4
#         if ind == 0:
#             width = x[opp] - x[ind]
#             height = y[opp] - y[ind]
#         elif ind == 1:
#             width = x[ind] - x[opp]
#             height = y[opp] - y[ind]
#         elif ind == 2:
#             width = x[ind] - x[opp]
#             height = y[ind] - y[opp]
#         elif ind == 3:
#             width = x[opp] - x[ind]
#             height = y[ind] - y[opp]
#         xy = (min(x[ind], x[opp]) if width > 0 else max(x[ind], x[opp]),
#               min(y[ind], y[opp]) if height > 0 else max(y[ind], y[opp]))
#         motif.update(xy=xy, width=width, height=height)
#         # self._draw()

#     # def _grab_patch(self, event: Event):
#     #     super()._grab_patch(event)
#     #     self._grab_artist_origin = self._grab_artist.xy

#     # def _update_motif_position(self, dx: float, dy: float):
#     #     rect = self._grabbed_motif
#     #     rect.xy = (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy)

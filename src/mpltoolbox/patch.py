# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

# from .event_handler import EventHandler
# from .patches import Patches
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


class Patch:

    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        self._max_clicks = 2
        self._ax = ax
        kwargs = parse_kwargs(kwargs, number)
        defaut_color = f'C{number}'
        if set(['ec', 'edgecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['ec'] = defaut_color
        if set(['fc', 'facecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['fc'] = to_rgb(defaut_color) + (0.05, )
        self._make_patch(x=x, y=y, **kwargs)
        self._vertices, = self._ax.plot(*self._make_vertices(),
                                        'o',
                                        ls='None',
                                        mec=self.edgecolor,
                                        mfc='None')
        self._vertices.parent = self
        self._patch.parent = self
        # self._ax.add_patch(self._patch)
        self.id = uuid.uuid1().hex

    def __str__(self):
        return repr(self)

    def _update_vertices(self):
        # if self._vertices is not None:
        self._vertices.set_data(*self._make_vertices())

    @property
    def width(self) -> float:
        return self._patch.get_width()

    @width.setter
    def width(self, width: float):
        self._patch.set_width(width)
        self._update_vertices()

    @property
    def height(self) -> float:
        return self._patch.get_height()

    @height.setter
    def height(self, height: float):
        self._patch.set_height(height)
        self._update_vertices()

    @property
    def edgecolor(self) -> str:
        return self._patch.get_edgecolor()

    @edgecolor.setter
    def edgecolor(self, color):
        self._patch.set_edgecolor(color)
        self._vertices.set_edgecolor(color)

    @property
    def facecolor(self) -> str:
        return self._patch.get_facecolor()

    @facecolor.setter
    def facecolor(self, color):
        self._patch.set_facecolor(color)

    def remove(self):
        self._patch.remove()
        self._vertices.remove()

    # def add_vertices(self):
    #     corners = self._patch.get_corners()
    #     self._vertices, = self._ax.plot(corners[:, 0],
    #                                     corners[:, 1],
    #                                     'o',
    #                                     ls='None',
    #                                     mec=self.edgecolor,
    #                                     mfc='None',
    #                                     picker=5.0)
    #     self._vertices.parent = self

    def update(self, **kwargs):
        self._patch.update(kwargs)
        self._update_vertices()

    # def _update_from_new_vertices(self, vertices):
    #     xy = vertices[0]
    #     width = vertices[2, 0] - vertices[0, 0]
    #     height = vertices[4, 1] - vertices[0, 1]
    #     self.update(xy=xy, width=width, height=height)

    @property
    def vertices(self):
        return self._vertices.get_data()

    def set_picker(self, pick):
        self._patch.set_picker(pick)
        self._vertices.set_picker(pick)

    def is_moveable(self, artist):
        return artist is self._vertices

    def is_draggable(self, artist):
        return artist is self._patch

    def is_removable(self, artist):
        return artist is self._patch

    def get_new_patch_props(self, event: Event, ind: int):
        x = event.xdata
        y = event.ydata
        verts = self.vertices
        if ind is None:
            ind = 4
        opp = (ind + 4) % 8
        xopp = verts[0][opp]
        yopp = verts[1][opp]
        width = None
        height = None
        corner = [verts[0][0], verts[1][0]]
        if ind == 0:
            width = xopp - x
            height = yopp - y
            corner = [x, y]
        elif ind == 1:
            height = yopp - y
            corner[1] = y
        elif ind == 2:
            width = x - xopp
            height = yopp - y
            corner[1] = y
        elif ind == 3:
            width = x - xopp
        elif ind == 4:
            width = x - xopp
            height = y - yopp
        elif ind == 5:
            height = y - yopp
        elif ind == 6:
            width = xopp - x
            height = y - yopp
            corner[0] = x
        elif ind == 7:
            width = xopp - x
            corner[0] = x
        # xy = (min(x[ind], x[opp]) if width > 0 else max(x[ind], x[opp]),
        #       min(y[ind], y[opp]) if height > 0 else max(y[ind], y[opp]))
        out = {'corner': corner}
        if width is not None:
            out['width'] = width
        if height is not None:
            out['height'] = height
        return out

    def after_persist_vertex(self, event):
        return


# Rectangles = partial(Tool, spawner=Rectangle)
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

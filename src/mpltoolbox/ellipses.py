# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

# from .patches import Patches
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


class Ellipse(Patch):

    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        super().__init__(x=x, y=y, number=number, ax=ax, **kwargs)

    def __repr__(self):
        return (f'Ellipse: center={self.center}, width={self.width}, '
                f'height={self.height}, '
                f'edgecolor={self.edgecolor}, facecolor={self.facecolor}')

    def _make_patch(self, x, y, **kwargs):
        self._patch = mp.Ellipse((x, y), 0, 0, **kwargs)

    def _make_vertices(self):
        # ellipse = self._patch
        center = self.center
        width = self.width
        height = self.height
        l = center[0] - 0.5 * width
        c = center[0]
        r = center[0] + 0.5 * width
        b = center[1] - 0.5 * height
        m = center[1]
        t = center[1] + 0.5 * height
        return (np.array([l, c, r, r, r, c, l, l]), np.array([b, b, b, m, t, t, t, m]))

    def move_vertex(self, event: Event, ind: int):
        props = super().get_new_patch_props(event=event, ind=ind)
        center = list(self.center)
        if 'width' in props:
            center[0] = props['corner'][0] + 0.5 * props['width']
        if 'height' in props:
            center[1] = props['corner'][1] + 0.5 * props['height']
        props['center'] = center
        del props['corner']
        self.update(**props)

    @property
    def center(self) -> float:
        return self._patch.get_center()

    @center.setter
    def center(self, center: float):
        self._patch.set_center(center)
        self._update_vertices()

    @property
    def xy(self) -> float:
        return self.center

    @xy.setter
    def xy(self, xy: float):
        self.center = xy


Ellipses = partial(Tool, spawner=Ellipse)
"""
Add ellipses to the supplied axes.

Controls:
  - Left-click and hold to make new ellipses
  - Right-click and hold to drag/move ellipse
  - Middle-click to delete ellipse

:param ax: The Matplotlib axes to which the Ellipses tool will be attached.
:param autostart: Automatically activate the tool upon creation if `True`.
:param on_create: Callback that fires when a ellipse is created.
:param on_remove: Callback that fires when a ellipse is removed.
:param on_drag_press: Callback that fires when a ellipse is right-clicked.
:param on_drag_move: Callback that fires when a ellipse is dragged.
:param on_drag_release: Callback that fires when a ellipse is released.
:param kwargs: Matplotlib parameters used for customization.
    Each parameter can be a single item (it will apply to all ellipses),
    a list of items (one entry per ellipse), or a callable (which will be
    called every time a new ellipse is created).
"""

# def _vertices_from_ellipse(ellipse: mp.Patch) -> Tuple[List[float]]:
#     center = ellipse.center
#     width = ellipse.get_width()
#     height = ellipse.get_height()
#     return ([center[0] - 0.5 * width, center[0], center[0] + 0.5 * width, center[0]],
#             [center[1], center[1] - 0.5 * height, center[1], center[1] + 0.5 * height])

# class Ellipse:

#     def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
#         self._max_clicks = 2
#         self._ax = ax
#         kwargs = parse_kwargs(kwargs, number)
#         defaut_color = f'C{number}'
#         if set(['ec', 'edgecolor']).isdisjoint(set(kwargs.keys())):
#             kwargs['ec'] = defaut_color
#         if set(['fc', 'facecolor']).isdisjoint(set(kwargs.keys())):
#             kwargs['fc'] = to_rgb(defaut_color) + (0.05, )
#         self._ellipse = mp.Ellipse((x, y), 0, 0, **kwargs)
#         # self._vertices = None
#         self._vertices, = self._ax.plot(*self._make_vertices(),
#                                         'o',
#                                         ls='None',
#                                         mec=self.edgecolor,
#                                         mfc='None')
#         self._vertices.parent = self
#         self._ellipse.parent = self
#         self._ax.add_patch(self._ellipse)
#         self.id = uuid.uuid1().hex

#     def __repr__(self):
#         return (f'Ellipse: center={self.center}, width={self.width}, '
#                 f'height={self.height}, '
#                 f'edgecolor={self.edgecolor}, facecolor={self.facecolor}')

#     def __str__(self):
#         return repr(self)

#     def _make_vertices(self):
#         center = ellipse.center
#         width = ellipse.get_width()
#         height = ellipse.get_height()
#         l = center[0] - 0.5 * width
#         c = center[0]
#         r = center[0] + 0.5 * width
#         b = center[1] - 0.5 * height
#         m = center[1]
#         t = center[1] + 0.5 * height
#         return (np.array([l, c, r, r, r, c, l, l]), np.array([b, b, b, m, t, t, t, m]))

#     def _update_vertices(self):
#         self._vertices.set_data(*self._make_vertices())

#     @property
#     def center(self) -> float:
#         return self._ellipse.center

#     @center.setter
#     def center(self, xy: float):
#         self._ellipse.center = xy
#         self._update_vertices()

#     @property
#     def xy(self) -> float:
#         return self.center

#     @xy.setter
#     def xy(self, xy: float):
#         self.center = xy

#     @property
#     def width(self) -> float:
#         return self._ellipse.get_width()

#     @width.setter
#     def width(self, width: float):
#         self._ellipse.set_width(width)
#         self._update_vertices()

#     @property
#     def height(self) -> float:
#         return self._ellipse.get_height()

#     @height.setter
#     def height(self, height: float):
#         self._ellipse.set_height(height)
#         self._update_vertices()

#     @property
#     def edgecolor(self) -> str:
#         return self._ellipse.get_edgecolor()

#     @edgecolor.setter
#     def edgecolor(self, color):
#         self._ellipse.set_edgecolor(color)
#         self._vertices.set_edgecolor(color)

#     @property
#     def facecolor(self) -> str:
#         return self._ellipse.get_facecolor()

#     @facecolor.setter
#     def facecolor(self, color):
#         self._ellipse.set_facecolor(color)

#     def remove(self):
#         self._ellipse.remove()
#         self._vertices.remove()

#     # def add_vertices(self):
#     #     # corners = self._ellipse.get_corners()
#     #     self._vertices, = self._ax.plot(*_vertices_from_ellipse(self._ellipse),
#     #                                     'o',
#     #                                     ls='None',
#     #                                     mec=self.edgecolor,
#     #                                     mfc='None',
#     #                                     picker=5.0)
#     #     self._vertices.parent = self

#     def update(self, **kwargs):
#         self._ellipse.update(kwargs)
#         self._update_vertices()

#     @property
#     def vertices(self):
#         return self._vertices.get_data()

#     def set_picker(self, pick):
#         self._ellipse.set_picker(pick)
#         self._vertices.set_picker(pick)

#     def is_moveable(self, artist):
#         return artist is self._vertices

#     def is_draggable(self, artist):
#         return artist is self._ellipse

#     def is_removable(self, artist):
#         return artist is self._ellipse

#     def move_vertex(self, event: Event, ind: int):
#         x = event.xdata
#         y = event.ydata
#         verts = self.vertices

#         # x, y = self._vertices.get_data()
#         if ind is None:
#             ind = 4
#         opp = (ind + 4) % 8
#         xopp = verts[0][opp]
#         yopp = verts[1][opp]
#         width = None
#         height = None
#         center = self.center

#         # patch = self._moving_vertex_artist.parent
#         x[ind] = event.xdata
#         y[ind] = event.ydata
#         opp = (ind + 2) % 4

#         even_ind = (ind % 2) == 0
#         if even_ind:
#             if ind == 0:
#                 width = x[opp] - x[ind]
#             else:
#                 width = x[ind] - x[opp]
#             height = self.height
#             center = (0.5 * (x[ind] + x[opp]), self.center[1])
#         else:
#             if ind == 1:
#                 height = y[opp] - y[ind]
#             else:
#                 height = y[ind] - y[opp]
#             width = self.width
#             center = (self.center[0], 0.5 * (y[ind] + y[opp]))
#         self.update(center=center, width=width, height=height)

#     def after_persist_vertex(self, event):
#         return

# def __init__(self, ax: Axes, **kwargs):

#     super().__init__(ax=ax, **kwargs)
#     self._spawner = Ellipse
#     self._new_ellipse_center = None

# def _make_new_patch(self, x: float, y: float):
#     super()._make_new_patch(x, y)
#     self._new_ellipse_center = (x, y)

# def _resize_patch(self, event: Event):
#     if event.inaxes != self._ax:
#         return
#     x, y = self._new_ellipse_center
#     dx = event.xdata - x
#     dy = event.ydata - y
#     self.patches[-1].update(width=dx,
#                             height=dy,
#                             center=(x + 0.5 * dx, y + 0.5 * dy))
#     self._draw()

# # def _add_vertices(self):
# #     patch = self.patches[-1]
# #     vertices = _vertices_from_ellipse(center=patch.center,
# #                                       width=patch.get_width(),
# #                                       height=patch.get_height())

# #     line, = self._ax.plot(vertices[0],
# #                           vertices[1],
# #                           'o',
# #                           mec=patch.get_edgecolor(),
# #                           mfc='None',
# #                           picker=5.0)
# #     patch._vertices = line
# #     line._patch = patch

# def _move_vertex(self, event: Event, ind: int, line: Artist):
#     if event.inaxes != self._ax:
#         return
#     x, y = line.get_data()
#     patch = self._moving_vertex_artist.parent
#     x[ind] = event.xdata
#     y[ind] = event.ydata
#     opp = (ind + 2) % 4
#     even_ind = (ind % 2) == 0
#     if even_ind:
#         if ind == 0:
#             width = x[opp] - x[ind]
#         else:
#             width = x[ind] - x[opp]
#         height = patch.height
#         center = (0.5 * (x[ind] + x[opp]), patch.center[1])
#     else:
#         if ind == 1:
#             height = y[opp] - y[ind]
#         else:
#             height = y[ind] - y[opp]
#         width = patch.width
#         center = (patch.center[0], 0.5 * (y[ind] + y[opp]))
#     patch.update(center=center, width=width, height=height)
#     # line.set_data(_vertices_from_ellipse(center=center, width=width, height=height))
#     # line._patch.update({'center': center, 'width': width, 'height': height})
#     self._draw()

# def _grab_patch(self, event: Event):
#     super()._grab_patch(event)
#     self._grab_artist_origin = self._grab_artist.center

# def _update_artist_position(self, dx: float, dy: float):
#     ell = self._grab_artist.parent
#     ell.center = (self._grab_artist_origin[0] + dx,
#                   self._grab_artist_origin[1] + dy)
#     # ell._vertices.set_data(
#     #     _vertices_from_ellipse(center=ell.center,
#     #                            width=ell.get_width(),
#     #                            height=ell.get_height()))

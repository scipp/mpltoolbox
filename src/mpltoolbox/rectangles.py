# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .event_handler import EventHandler
from .patches import Patches
from .utils import parse_kwargs
from matplotlib import patches as mp
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event
from matplotlib.colors import to_rgb
from typing import Tuple, List
import uuid


class Rectangle:

    def __init__(self, x: float, y: float, number: int, ax: Axes, **kwargs):
        self._ax = ax
        kwargs = parse_kwargs(kwargs, number)
        defaut_color = f'C{number}'
        if set(['ec', 'edgecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['ec'] = defaut_color
        if set(['fc', 'facecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['fc'] = to_rgb(defaut_color) + (0.05, )
        self._rectangle = mp.Rectangle((x, y), 0, 0, **kwargs)
        # self._vertices = None
        corners = self._rectangle.get_corners()
        self._vertices, = self._ax.plot(corners[:, 0],
                                        corners[:, 1],
                                        'o',
                                        ls='None',
                                        mec=self.edgecolor,
                                        mfc='None')
        self._vertices.parent = self
        self._rectangle.parent = self
        self._ax.add_patch(self._rectangle)
        self.id = uuid.uuid1().hex

    def __repr__(self):
        return (f'Rectangle: xy={self.xy}, width={self.width}, height={self.height}, '
                f'edgecolor={self.edgecolor}, facecolor={self.facecolor}')

    def __str__(self):
        return repr(self)

    def _update_vertices(self):
        if self._vertices is not None:
            self._vertices.set_data(self._rectangle.get_corners().T)

    @property
    def xy(self) -> float:
        return self._rectangle.get_xy()

    @xy.setter
    def xy(self, xy: float):
        self._rectangle.set_xy(xy)
        self._update_vertices()

    @property
    def width(self) -> float:
        return self._rectangle.get_width()

    @width.setter
    def width(self, width: float):
        self._rectangle.set_width(width)
        self._update_vertices()

    @property
    def height(self) -> float:
        return self._rectangle.get_height()

    @height.setter
    def height(self, height: float):
        self._rectangle.set_height(height)
        self._update_vertices()

    @property
    def edgecolor(self) -> str:
        return self._rectangle.get_edgecolor()

    @edgecolor.setter
    def edgecolor(self, color):
        self._rectangle.set_edgecolor(color)
        self._vertices.set_edgecolor(color)

    @property
    def facecolor(self) -> str:
        return self._rectangle.get_facecolor()

    @facecolor.setter
    def facecolor(self, color):
        self._rectangle.set_facecolor(color)

    def remove(self):
        self._rectangle.remove()
        self._vertices.remove()

    # def add_vertices(self):
    #     corners = self._rectangle.get_corners()
    #     self._vertices, = self._ax.plot(corners[:, 0],
    #                                     corners[:, 1],
    #                                     'o',
    #                                     ls='None',
    #                                     mec=self.edgecolor,
    #                                     mfc='None',
    #                                     picker=5.0)
    #     self._vertices.parent = self

    def update(self, **kwargs):
        self._rectangle.update(kwargs)
        self._update_vertices()

    @property
    def vertices(self):
        return self._vertices.get_data()

    def set_picker(self, pick):
        self._rectangle.set_picker(pick)
        self._vertices.set_picker(pick)


class Rectangles(EventHandler):
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

    def __init__(self, ax: Axes, **kwargs):

        super().__init__(ax=ax, **kwargs)
        self._maker = Rectangle
        self._max_clicks = 2

    def _resize_patch(self, event: Event):
        if event.inaxes != self._ax:
            return
        patch = self.patches[-1]
        x, y = patch.xy
        patch.update(width=event.xdata - x, height=event.ydata - y)
        self._draw()

    def _move_vertex(self, event: Event, ind: int, artist: Artist):
        if event.inaxes != self._ax:
            return
        x, y = artist._vertices.get_data()
        if ind is None:
            ind = 2
        x[ind] = event.xdata
        y[ind] = event.ydata
        opp = (ind + 2) % 4
        if ind == 0:
            width = x[opp] - x[ind]
            height = y[opp] - y[ind]
        elif ind == 1:
            width = x[ind] - x[opp]
            height = y[opp] - y[ind]
        elif ind == 2:
            width = x[ind] - x[opp]
            height = y[ind] - y[opp]
        elif ind == 3:
            width = x[opp] - x[ind]
            height = y[ind] - y[opp]
        xy = (min(x[ind], x[opp]) if width > 0 else max(x[ind], x[opp]),
              min(y[ind], y[opp]) if height > 0 else max(y[ind], y[opp]))
        artist.update(xy=xy, width=width, height=height)
        self._draw()

    def _grab_patch(self, event: Event):
        super()._grab_patch(event)
        self._grab_artist_origin = self._grab_artist.xy

    def _update_artist_position(self, dx: float, dy: float):
        rect = self._grab_artist.parent
        rect.xy = (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy)

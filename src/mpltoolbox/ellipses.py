# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .patches import Patches
from matplotlib import patches as mp
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event
from typing import Tuple, List
import uuid


def _vertices_from_ellipse(ellipse: mp.Patch) -> Tuple[List[float]]:
    center = ellipse.center
    width = ellipse.get_width()
    height = ellipse.get_height()
    return ([center[0] - 0.5 * width, center[0], center[0] + 0.5 * width, center[0]],
            [center[1], center[1] - 0.5 * height, center[1], center[1] + 0.5 * height])


class Ellipse:

    def __init__(self, x: float, y: float, width: float, height: float, ax: Axes,
                 **kwargs):
        self._ax = ax
        self._ellipse = mp.Ellipse((x, y), width, height, **kwargs)
        self._vertices = None
        self._ellipse.parent = self
        self._ax.add_patch(self._ellipse)
        self.id = uuid.uuid1().hex

    def __repr__(self):
        return (f'Ellipse: center={self.center}, width={self.width}, '
                f'height={self.height}, '
                f'edgecolor={self.edgecolor}, facecolor={self.facecolor}')

    def __str__(self):
        return repr(self)

    def _update_vertices(self):
        if self._vertices is not None:
            self._vertices.set_data(*_vertices_from_ellipse(self._ellipse))

    @property
    def center(self) -> float:
        return self._ellipse.center

    @center.setter
    def center(self, xy: float):
        self._ellipse.center = xy
        self._update_vertices()

    @property
    def width(self) -> float:
        return self._ellipse.get_width()

    @width.setter
    def width(self, width: float):
        self._ellipse.set_width(width)
        self._update_vertices()

    @property
    def height(self) -> float:
        return self._ellipse.get_height()

    @height.setter
    def height(self, height: float):
        self._ellipse.set_height(height)
        self._update_vertices()

    @property
    def edgecolor(self) -> str:
        return self._ellipse.get_edgecolor()

    @edgecolor.setter
    def edgecolor(self, color):
        self._ellipse.set_edgecolor(color)
        self._vertices.set_edgecolor(color)

    @property
    def facecolor(self) -> str:
        return self._ellipse.get_facecolor()

    @facecolor.setter
    def facecolor(self, color):
        self._ellipse.set_facecolor(color)

    def remove(self):
        self._ellipse.remove()
        self._vertices.remove()

    def add_vertices(self):
        # corners = self._ellipse.get_corners()
        self._vertices, = self._ax.plot(*_vertices_from_ellipse(self._ellipse),
                                        'o',
                                        ls='None',
                                        mec=self.edgecolor,
                                        mfc='None',
                                        picker=5.0)
        self._vertices.parent = self

    def update(self, **kwargs):
        self._ellipse.update(kwargs)
        self._update_vertices()

    @property
    def vertices(self):
        return self._vertices.get_data()


class Ellipses(Patches):
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

    def __init__(self, ax: Axes, **kwargs):

        super().__init__(ax=ax, **kwargs)
        self._spawner = Ellipse
        self._new_ellipse_center = None

    def _make_new_patch(self, x: float, y: float):
        super()._make_new_patch(x, y)
        self._new_ellipse_center = (x, y)

    def _resize_patch(self, event: Event):
        if event.inaxes != self._ax:
            return
        x, y = self._new_ellipse_center
        dx = event.xdata - x
        dy = event.ydata - y
        self.patches[-1].update(width=dx,
                                height=dy,
                                center=(x + 0.5 * dx, y + 0.5 * dy))
        self._draw()

    # def _add_vertices(self):
    #     patch = self.patches[-1]
    #     vertices = _vertices_from_ellipse(center=patch.center,
    #                                       width=patch.get_width(),
    #                                       height=patch.get_height())

    #     line, = self._ax.plot(vertices[0],
    #                           vertices[1],
    #                           'o',
    #                           mec=patch.get_edgecolor(),
    #                           mfc='None',
    #                           picker=5.0)
    #     patch._vertices = line
    #     line._patch = patch

    def _move_vertex(self, event: Event, ind: int, line: Artist):
        if event.inaxes != self._ax:
            return
        x, y = line.get_data()
        patch = self._moving_vertex_artist.parent
        x[ind] = event.xdata
        y[ind] = event.ydata
        opp = (ind + 2) % 4
        even_ind = (ind % 2) == 0
        if even_ind:
            if ind == 0:
                width = x[opp] - x[ind]
            else:
                width = x[ind] - x[opp]
            height = patch.height
            center = (0.5 * (x[ind] + x[opp]), patch.center[1])
        else:
            if ind == 1:
                height = y[opp] - y[ind]
            else:
                height = y[ind] - y[opp]
            width = patch.width
            center = (patch.center[0], 0.5 * (y[ind] + y[opp]))
        patch.update(center=center, width=width, height=height)
        # line.set_data(_vertices_from_ellipse(center=center, width=width, height=height))
        # line._patch.update({'center': center, 'width': width, 'height': height})
        self._draw()

    def _grab_patch(self, event: Event):
        super()._grab_patch(event)
        self._grab_artist_origin = self._grab_artist.center

    def _update_artist_position(self, dx: float, dy: float):
        ell = self._grab_artist.parent
        ell.center = (self._grab_artist_origin[0] + dx,
                      self._grab_artist_origin[1] + dy)
        # ell._vertices.set_data(
        #     _vertices_from_ellipse(center=ell.center,
        #                            width=ell.get_width(),
        #                            height=ell.get_height()))

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .patches import Patches
from matplotlib.patches import Rectangle
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event


class Rectangles(Patches):
    """
    Add rectangles to the supplied axes.

    Controls:
      - Left-click and hold to make new rectangles
      - Right-click and hold to drag/move rectangle
      - Middle-click to delete rectangle

    :param ax: The Matplotlib axes to which the Lines tool will be attached.
    :param color: The rectangle colors. Can be a string (all lines will have the same
        color), a list of strings (one entry per rectangle), or a callable (this will be
        called every time a new rectangle is created and should return a color).
    :param autostart: Automatically activate the tool upon creation if `True`.
    :param on_create: Callback that fires when a rectangle is created.
    :param on_remove: Callback that fires when a rectangle is removed.
    :param on_drag_press: Callback that fires when a rectangle is right-clicked.
    :param on_drag_move: Callback that fires when a rectangle is dragged.
    :param on_drag_release: Callback that fires when a rectangle is released.
    """

    def __init__(self, ax: Axes, **kwargs):

        super().__init__(ax=ax, patch=Rectangle, **kwargs)

    def _resize_patch(self, event: Event):
        if event.inaxes != self._ax:
            return
        x, y = self.patches[-1].xy
        self.patches[-1].update({
            'width': event.xdata - x,
            'height': event.ydata - y,
        })
        self._draw()

    def _grab_patch(self, event: Event):
        super()._grab_patch(event)
        self._grab_artist_origin = self._grab_artist.xy

    def _update_artist_position(self, dx: float, dy: float):
        self._grab_artist.xy = (self._grab_artist_origin[0] + dx,
                                self._grab_artist_origin[1] + dy)

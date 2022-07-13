# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .patches import Patches
from matplotlib.patches import Ellipse
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event


class Ellipses(Patches):
    """
    Add ellipses to the supplied axes.

    Controls:
      - Left-click and hold to make new ellipses
      - Right-click and hold to drag/move ellipse
      - Middle-click to delete ellipse

    :param ax: The Matplotlib axes to which the Lines tool will be attached.
    :param color: The ellipse colors. Can be a string (all lines will have the same
        color), a list of strings (one entry per ellipse), or a callable (this will be
        called every time a new ellipse is created and should return a color).
    :param autostart: Automatically activate the tool upon creation if `True`.
    :param on_create: Callback that fires when a ellipse is created.
    :param on_remove: Callback that fires when a ellipse is removed.
    :param on_drag_press: Callback that fires when a ellipse is right-clicked.
    :param on_drag_move: Callback that fires when a ellipse is dragged.
    :param on_drag_release: Callback that fires when a ellipse is released.
    """

    def __init__(self, ax: Axes, **kwargs):

        super().__init__(ax=ax, patch=Ellipse, **kwargs)
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
        self.patches[-1].update({
            'width': dx,
            'height': dy,
            'center': (x + 0.5 * dx, y + 0.5 * dy)
        })
        self._draw()

    def _grab_patch(self, event: Event):
        super()._grab_patch(event)
        self._grab_artist_origin = self._grab_artist.center

    def _update_artist_position(self, dx: float, dy: float):
        self._grab_artist.center = (self._grab_artist_origin[0] + dx,
                                    self._grab_artist_origin[1] + dy)

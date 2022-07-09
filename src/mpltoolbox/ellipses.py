# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .patches import Patches
from matplotlib.patches import Ellipse


class Ellipses(Patches):

    def __init__(self, ax, **kwargs):

        super().__init__(ax=ax, patch=Ellipse, **kwargs)
        self._new_ellipse_center = None

    def _make_new_patch(self, x, y):
        super()._make_new_patch(x, y)
        self._new_ellipse_center = (x, y)

    def _resize_patch(self, event):
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

    def _grab_patch(self, event):
        super()._grab_patch(event)
        self._grab_artist_origin = self._grab_artist.center

    def _update_artist_position(self, dx, dy):
        self._grab_artist.center = (self._grab_artist_origin[0] + dx,
                                    self._grab_artist_origin[1] + dy)

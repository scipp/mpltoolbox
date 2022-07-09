# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .patches import Patches
from matplotlib.patches import Rectangle


class Rectangles(Patches):

    def __init__(self, ax, **kwargs):

        super().__init__(ax=ax, patch=Rectangle, **kwargs)

    def _resize_patch(self, event):
        if event.inaxes != self._ax:
            return
        x, y = self.patches[-1].xy
        self.patches[-1].update({
            'width': event.xdata - x,
            'height': event.ydata - y,
        })
        self._draw()

    def _grab_patch(self, event):
        super()._grab_patch(event)
        self._grab_artist_origin = self._grab_artist.xy

    def _update_artist_position(self, dx, dy):
        self._grab_artist.xy = (self._grab_artist_origin[0] + dx,
                                self._grab_artist_origin[1] + dy)

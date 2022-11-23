# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .spans import Spans
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event


class HSpan:

    def __init__(self, x: float, y: float, ax: Axes, **kwargs):
        self._ax = ax
        self._span = self._ax.axhspan(y, y, **kwargs)
        self._vertices = None
        self._span.parent = self

    @property
    def bottom(self) -> float:
        return self._span.get_xy()[0, 1]

    @bottom.setter
    def bottom(self, y: float):
        corners = self._span.get_xy()
        for i in [0, 3]:
            corners[i, 1] = y
        if len(corners) > 3:
            corners[4, 1] = y
        else:
            corners += [corners[0, 0], y]
        self._span.set_xy(corners)
        if self._vertices is not None:
            self._vertices.set_ydata([corners[0, 1], corners[1, 1]])

    @property
    def top(self) -> float:
        return self._span.get_xy()[1, 1]

    @top.setter
    def top(self, y: float):
        corners = self._span.get_xy()
        for i in [1, 2]:
            corners[i, 1] = y
        self._span.set_xy(corners)
        if self._vertices is not None:
            self._vertices.set_ydata([corners[0, 1], corners[1, 1]])

    @property
    def color(self) -> str:
        return self._span.get_edgecolor()

    def remove(self):
        self._span.remove()
        self._vertices.remove()

    def add_vertices(self):
        self._vertices, = self._ax.plot([0.5, 0.5], [self.bottom, self.top],
                                        'o',
                                        ls='None',
                                        mec=self.color,
                                        mfc='None',
                                        picker=5.0,
                                        transform=self._span.get_transform())
        self._vertices.parent = self


class Hspans(Spans):
    """
    Add horizontal spans to the supplied axes.

    Controls:
      - Left-click and hold to make new spans
      - Right-click and hold to drag/move span
      - Middle-click to delete span

    :param ax: The Matplotlib axes to which the Hspans tool will be attached.
    :param autostart: Automatically activate the tool upon creation if `True`.
    :param on_create: Callback that fires when a span is created.
    :param on_remove: Callback that fires when a span is removed.
    :param on_drag_press: Callback that fires when a span is right-clicked.
    :param on_drag_move: Callback that fires when a span is dragged.
    :param on_drag_release: Callback that fires when a span is released.
    :param kwargs: Matplotlib parameters used for customization.
        Each parameter can be a single item (it will apply to all spans),
        a list of items (one entry per span), or a callable (which will be
        called every time a new span is created).
    """

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax=ax, **kwargs)
        self._span = HSpan

    def _resize_span(self, event: Event):
        if event.inaxes != self._ax:
            return
        self.spans[-1].top = event.ydata
        self._draw()

    def _move_vertex(self, event: Event, ind: int, line: Artist):
        if event.inaxes != self._ax:
            return
        span = self._moving_vertex_artist.parent
        y = event.ydata
        if ind == 0:
            span.bottom = y
        else:
            span.top = y
        self._draw()

    def _grab_span(self, event: Event):
        super()._grab_span(event)
        self._grab_artist_origin = [
            self._grab_artist.parent.bottom, self._grab_artist.parent.top
        ]

    def _update_artist_position(self, dx: float, dy: float):
        span = self._grab_artist.parent
        span.bottom = self._grab_artist_origin[0] + dy
        span.top = self._grab_artist_origin[1] + dy

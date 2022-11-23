# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .spans import Spans
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event


class VSpan:

    def __init__(self, x: float, y: float, ax: Axes, **kwargs):
        self._ax = ax
        self._span = self._ax.axvspan(x, x, **kwargs)
        self._vertices = None
        self._span.parent = self

    @property
    def left(self) -> float:
        return self._span.get_xy()[0, 0]

    @left.setter
    def left(self, x: float):
        corners = self._span.get_xy()
        for i in [0, 1]:
            corners[i, 0] = x
        if len(corners) > 3:
            corners[4, 0] = x
        else:
            corners += [x, corners[0, 1]]
        self._span.set_xy(corners)
        if self._vertices is not None:
            self._vertices.set_xdata([corners[0, 0], corners[2, 0]])

    @property
    def right(self) -> float:
        return self._span.get_xy()[2, 0]

    @right.setter
    def right(self, x: float):
        corners = self._span.get_xy()
        for i in [2, 3]:
            corners[i, 0] = x
        self._span.set_xy(corners)
        if self._vertices is not None:
            self._vertices.set_xdata([corners[0, 0], corners[2, 0]])

    @property
    def color(self) -> str:
        return self._span.get_edgecolor()

    def remove(self):
        self._span.remove()
        self._vertices.remove()

    def add_vertices(self):
        self._vertices, = self._ax.plot([self.left, self.right], [0.5, 0.5],
                                        'o',
                                        ls='None',
                                        mec=self.color,
                                        mfc='None',
                                        picker=5.0,
                                        transform=self._span.get_transform())
        self._vertices.parent = self


class Vspans(Spans):
    """
    Add vertical spans to the supplied axes.

    Controls:
      - Left-click and hold to make new spans
      - Right-click and hold to drag/move span
      - Middle-click to delete span

    :param ax: The Matplotlib axes to which the Vspans tool will be attached.
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
        self._span = VSpan

    def _resize_span(self, event: Event):
        if event.inaxes != self._ax:
            return
        self.spans[-1].right = event.xdata
        self._draw()

    def _move_vertex(self, event: Event, ind: int, line: Artist):
        if event.inaxes != self._ax:
            return
        span = self._moving_vertex_artist.parent
        x = event.xdata
        if ind == 0:
            span.left = x
        else:
            span.right = x
        self._draw()

    def _grab_span(self, event: Event):
        super()._grab_span(event)
        self._grab_artist_origin = [
            self._grab_artist.parent.left, self._grab_artist.parent.right
        ]

    def _update_artist_position(self, dx: float, dy: float):
        span = self._grab_artist.parent
        span.left = self._grab_artist_origin[0] + dx
        span.right = self._grab_artist_origin[1] + dx

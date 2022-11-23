# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .lines import Lines
from matplotlib.pyplot import Axes
from typing import Tuple


class Points(Lines):
    """
    Add points to the supplied axes.

    Controls:
      - Left-click to make new points
      - Left-click and hold on point to move point
      - Middle-click to delete point

    :param ax: The Matplotlib axes to which the Points tool will be attached.
    :param autostart: Automatically activate the tool upon creation if `True`.
    :param on_create: Callback that fires when a point is created.
    :param on_remove: Callback that fires when a point is removed.
    :param on_vertex_press: Callback that fires when a point is left-clicked.
    :param on_vertex_move: Callback that fires when a point is moved.
    :param on_vertex_release: Callback that fires when a point is released.
    :param kwargs: Matplotlib parameters used for customization.
        Each parameter can be a single item (it will apply to all points),
        a list of items (one entry per point), or a callable (which will be
        called every time a new point is created).
    """

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax, n=1, **kwargs)

    def _new_line_pos(self, x: float, y: float) -> Tuple[float]:
        return [x], [y]

    def _after_line_creation(self, event):
        self._finalize_line(event)

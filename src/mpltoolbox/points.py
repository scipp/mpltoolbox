# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .lines import Lines
from matplotlib.pyplot import Axes
from typing import Tuple


class Points(Lines):

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax, n=1, **kwargs)

    def _new_line_pos(self, x: float, y: float) -> Tuple[float]:
        return [x], [y]

    def _after_line_creation(self, event):
        self._finalize_line(event)

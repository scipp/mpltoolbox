# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .lines import Lines
from matplotlib.pyplot import Axes


class Points(Lines):

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax, n=1, **kwargs)

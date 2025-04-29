# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

from dataclasses import dataclass

from matplotlib.pyplot import Axes


@dataclass
class DummyEvent:
    """
    A dummy event class for simulating clicks on figures.
    """

    xdata: float
    ydata: float
    inaxes: Axes
    button: int
    modifiers: list[str] | None

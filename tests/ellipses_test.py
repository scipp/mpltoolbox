# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np

import mpltoolbox as tbx


def test_ellipses_creation():
    _, ax = plt.subplots()
    ells = tbx.Ellipses(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80]
    y = [40, 70]
    ells.click(x=x[0], y=y[0])  # first corner
    ells.click(x=x[1], y=y[1])  # second corner
    assert len(ax.patches) == 1
    p = ax.patches[0]
    xy = p.get_center()
    assert xy[0], 0.5 * (x[0] + x[1])
    assert xy[1], 0.5 * (y[0] + y[1])
    assert p.get_width() == x[1] - x[0]
    assert p.get_height() == y[1] - y[0]

    x = [30, 40]
    y = [10, 90]
    ells.click(x=x[0], y=y[0])  # first corner
    ells.click(x=x[1], y=y[1])  # second corner
    assert len(ax.patches) == 2
    p = ax.patches[1]
    xy = p.get_center()
    assert np.allclose(xy[0], 0.5 * (x[0] + x[1]))
    assert np.allclose(xy[1], 0.5 * (y[0] + y[1]))
    assert p.get_width() == x[1] - x[0]
    assert p.get_height() == y[1] - y[0]


def test_ellipses_calls_on_create():
    _, ax = plt.subplots()

    my_event_list = []

    def on_create(event):
        my_event_list.append(event)

    ells = tbx.Ellipses(ax=ax, on_create=on_create)
    x = [20, 80]
    y = [40, 70]
    ells.click(x=x[0], y=y[0])
    assert len(my_event_list) == 0  # only first corner, not a full rectangle
    ells.click(x=x[1], y=y[1])
    assert len(my_event_list) == 1
    x = [31, 41]
    y = [11, 91]
    ells.click(x=x[0], y=y[0])
    ells.click(x=x[1], y=y[1])
    assert len(my_event_list) == 2


def test_ellipses_remove():
    _, ax = plt.subplots()
    ells = tbx.Ellipses(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80]
    y = [40, 70]
    ells.click(x=x[0], y=y[0])
    ells.click(x=x[1], y=y[1])
    assert len(ax.patches) == 1

    x = [30, 40]
    y = [10, 90]
    ells.click(x=x[0], y=y[0])
    ells.click(x=x[1], y=y[1])
    assert len(ax.patches) == 2

    ells.remove(0)
    assert len(ax.patches) == 1
    ells.remove(0)
    assert len(ax.patches) == 0


def test_ellipses_calls_on_remove():
    _, ax = plt.subplots()

    my_event_list = []

    def on_remove(artist):
        my_event_list.append(f'Artist {artist} was removed')

    ells = tbx.Ellipses(ax=ax, on_remove=on_remove)
    x = [20, 80]
    y = [40, 70]
    ells.click(x=x[0], y=y[0])
    ells.click(x=x[1], y=y[1])
    assert len(ax.patches) == 1
    assert len(my_event_list) == 0

    ells.remove(0)
    assert len(ax.patches) == 0
    assert len(my_event_list) == 1

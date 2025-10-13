# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np

import mpltoolbox as tbx


def test_polygons_creation():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    assert len(ax.patches) == 0

    # Closing the polygon by repeating the first point
    x = [20, 80, 50, 20]
    y = [40, 70, 90, 40]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    p = ax.patches[0]
    verts = p.get_xy()
    assert len(verts) == 4  # closed polygon has one extra vertex
    assert np.allclose(verts[:, 0], x)
    assert np.allclose(verts[:, 1], y)

    x = [30, 40, 60, 70, 30]
    y = [10, 90, 80, 20, 10]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 2
    p = ax.patches[1]
    verts = p.get_xy()
    assert len(verts) == 5  # closed polygon has one extra vertex
    assert np.allclose(verts[:, 0], x)
    assert np.allclose(verts[:, 1], y)


def test_polygons_calls_on_create():
    _, ax = plt.subplots()

    my_event_list = []

    def on_create(event):
        my_event_list.append(event)

    polys = tbx.Polygons(ax=ax, on_create=on_create)
    x = [20, 80, 50, 20]
    y = [40, 70, 90, 40]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(my_event_list) == 1  # full polygon created
    x = [30, 40, 60, 70, 30]
    y = [10, 90, 80, 20, 10]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(my_event_list) == 2


def test_polygons_remove():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80, 50, 20]
    y = [40, 70, 90, 40]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1

    x = [30, 40, 60, 70, 30]
    y = [10, 90, 80, 20, 10]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 2

    polys.remove(0)
    assert len(ax.patches) == 1
    p = ax.patches[0]
    verts = p.get_xy()
    assert len(verts) == 5  # closed polygon has one extra vertex
    assert np.allclose(verts[:, 0], x)
    assert np.allclose(verts[:, 1], y)


def test_polygons_calls_on_remove():
    _, ax = plt.subplots()
    my_event_list = []

    def on_remove(event):
        my_event_list.append(event)

    polys = tbx.Polygons(ax=ax, on_remove=on_remove)
    x = [20, 80, 50, 20]
    y = [40, 70, 90, 40]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    assert len(my_event_list) == 0

    polys.remove(0)
    assert len(ax.patches) == 0
    assert len(my_event_list) == 1

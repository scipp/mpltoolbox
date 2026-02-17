# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_hex

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


def test_polygons_stop():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    x = [30, 90, 60, 30]
    y = [20, 20, 50, 20]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    polys.stop()
    for xi, yi in zip(np.array(x) + 1, np.array(y) + 1, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1


def test_polygons_start():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    x = [30, 90, 60, 30]
    y = [20, 20, 50, 20]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    polys.stop()
    polys.start()
    for xi, yi in zip(np.array(x) + 1, np.array(y) + 1, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 2


def test_polygons_freeze():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    x = [30, 90, 60, 30]
    y = [20, 20, 50, 20]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    polys.freeze()
    for xi, yi in zip(np.array(x) + 1, np.array(y) + 1, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    polys.start()
    for xi, yi in zip(np.array(x) + 1, np.array(y) + 1, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 2


def test_polygons_clear():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    x = [30, 90, 60, 30]
    y = [20, 20, 50, 20]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    assert to_hex(ax.lines[0].get_color()) == to_hex("C0")
    for xi, yi in zip(np.array(x) + 1, np.array(y) + 1, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 2
    assert to_hex(ax.lines[1].get_color()) == to_hex("C1")
    polys.clear()
    assert len(ax.patches) == 0
    for xi, yi in zip(np.array(x) + 2, np.array(y) + 2, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    assert to_hex(ax.lines[0].get_color()) == to_hex("C2")


def test_polygons_reset():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    x = [30, 90, 60, 30]
    y = [20, 20, 50, 20]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    for xi, yi in zip(np.array(x) + 3, np.array(y) + 3, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 2
    assert to_hex(ax.lines[0].get_color()) == to_hex("C0")
    assert to_hex(ax.lines[1].get_color()) == to_hex("C1")
    polys.reset()
    assert len(ax.patches) == 0
    for xi, yi in zip(np.array(x) + 5, np.array(y) + 5, strict=True):
        polys.click(x=xi, y=yi)
    assert to_hex(ax.lines[0].get_color()) == to_hex("C0")


def test_polygons_shutdown():
    _, ax = plt.subplots()
    polys = tbx.Polygons(ax=ax)
    x = [30, 90, 60, 30]
    y = [20, 20, 50, 20]
    for xi, yi in zip(x, y, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 1
    polys.shutdown()
    assert len(ax.patches) == 0
    for xi, yi in zip(np.array(x) + 1, np.array(y) + 1, strict=True):
        polys.click(x=xi, y=yi)
    assert len(ax.patches) == 0

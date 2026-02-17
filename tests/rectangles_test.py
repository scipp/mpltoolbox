# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

import mpltoolbox as tbx


def test_rectangles_creation():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80]
    y = [40, 70]
    rects.click(x=x[0], y=y[0])  # first corner
    rects.click(x=x[1], y=y[1])  # second corner
    assert len(ax.patches) == 1
    p = ax.patches[0]
    xy = p.get_xy()
    assert xy[0] == x[0]
    assert xy[1] == y[0]
    assert p.get_width() == x[1] - x[0]
    assert p.get_height() == y[1] - y[0]

    x = [30, 40]
    y = [10, 90]
    rects.click(x=x[0], y=y[0])  # first corner
    rects.click(x=x[1], y=y[1])  # second corner
    assert len(ax.patches) == 2
    p = ax.patches[1]
    xy = p.get_xy()
    assert xy[0] == x[0]
    assert xy[1] == y[0]
    assert p.get_width() == x[1] - x[0]
    assert p.get_height() == y[1] - y[0]


def test_rectangles_calls_on_create():
    _, ax = plt.subplots()

    my_event_list = []

    def on_create(event):
        my_event_list.append(event)

    rects = tbx.Rectangles(ax=ax, on_create=on_create)
    x = [20, 80]
    y = [40, 70]
    rects.click(x=x[0], y=y[0])
    assert len(my_event_list) == 0  # only first corner, not a full rectangle
    rects.click(x=x[1], y=y[1])
    assert len(my_event_list) == 1
    x = [31, 41]
    y = [11, 91]
    rects.click(x=x[0], y=y[0])
    rects.click(x=x[1], y=y[1])
    assert len(my_event_list) == 2


def test_rectangles_remove():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80]
    y = [40, 70]
    rects.click(x=x[0], y=y[0])
    rects.click(x=x[1], y=y[1])
    assert len(ax.patches) == 1

    x = [30, 40]
    y = [10, 90]
    rects.click(x=x[0], y=y[0])
    rects.click(x=x[1], y=y[1])
    assert len(ax.patches) == 2

    rects.remove(0)
    assert len(ax.patches) == 1
    rects.remove(0)
    assert len(ax.patches) == 0


def test_rectangles_calls_on_remove():
    _, ax = plt.subplots()

    my_event_list = []

    def on_remove(artist):
        my_event_list.append(f'Artist {artist} was removed')

    rects = tbx.Rectangles(ax=ax, on_remove=on_remove)
    x = [20, 80]
    y = [40, 70]
    rects.click(x=x[0], y=y[0])
    rects.click(x=x[1], y=y[1])
    assert len(ax.patches) == 1
    assert len(my_event_list) == 0

    rects.remove(0)
    assert len(ax.patches) == 0
    assert len(my_event_list) == 1


def test_rectangles_stop():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=80, y=70)
    assert len(ax.patches) == 1
    rects.stop()
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 1


def test_rectangles_start():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=80, y=70)
    assert len(ax.patches) == 1
    rects.stop()
    rects.start()
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 2


def test_rectangles_freeze():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=80, y=70)
    assert len(ax.patches) == 1
    rects.freeze()
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 1
    rects.start()
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 2


def test_rectangles_clear():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=80, y=70)
    assert len(ax.patches) == 1
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")
    rects.click(x=25, y=55)
    rects.click(x=35, y=75)
    assert len(ax.patches) == 2
    assert to_hex(ax.patches[1].get_edgecolor()) == to_hex("C1")
    rects.clear()
    assert len(ax.patches) == 0
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 1
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C2")


def test_rectangles_reset():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=25, y=55)
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 2
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")
    assert to_hex(ax.patches[1].get_edgecolor()) == to_hex("C1")
    rects.reset()
    assert len(ax.patches) == 0
    rects.click(x=21, y=40)
    rects.click(x=41, y=60)
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")


def test_rectangles_shutdown():
    _, ax = plt.subplots()
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=25, y=55)
    assert len(ax.patches) == 1
    rects.shutdown()
    assert len(ax.patches) == 0
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 0

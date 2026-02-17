# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

import mpltoolbox as tbx


def test_points_creation():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    assert len(ax.lines) == 0

    x = [20.5, 77.1]
    y = [44.3, 70.0]
    points.click(x=x[0], y=y[0])
    assert len(ax.lines) == 1
    data = ax.lines[0].get_xydata()
    assert data.shape == (1, 2)
    assert data[0, 0] == x[0]
    assert data[0, 1] == y[0]

    points.click(x=x[1], y=y[1])
    assert len(ax.lines) == 2
    data = ax.lines[1].get_xydata()
    assert data[0, 0] == x[1]
    assert data[0, 1] == y[1]


def test_points_calls_on_create():
    _, ax = plt.subplots()

    my_event_list = []

    def on_create(event):
        my_event_list.append(event)

    points = tbx.Points(ax=ax, on_create=on_create)
    x = [20, 80]
    y = [40, 70]
    points.click(x=x[0], y=y[0])
    assert len(my_event_list) == 1
    points.click(x=x[1], y=y[1])
    assert len(my_event_list) == 2


def test_points_remove():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    assert len(ax.lines) == 0

    x = [20, 80]
    y = [40, 70]
    points.click(x=x[0], y=y[0])
    assert len(ax.lines) == 1

    points.click(x=x[1], y=y[1])
    assert len(ax.lines) == 2

    points.remove(0)
    assert len(ax.lines) == 1
    points.remove(0)
    assert len(ax.lines) == 0


def test_points_calls_on_remove():
    _, ax = plt.subplots()

    my_event_list = []

    def on_remove(artist):
        my_event_list.append(f'Artist {artist} was removed')

    points = tbx.Points(ax=ax, on_remove=on_remove)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    assert len(my_event_list) == 0
    points.remove(0)
    assert len(ax.lines) == 0
    assert len(my_event_list) == 1


def test_points_stop():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    points.stop()
    points.click(x=30, y=60)
    assert len(ax.lines) == 1


def test_points_start():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    points.stop()
    points.start()
    points.click(x=30, y=60)
    assert len(ax.lines) == 2


def test_points_freeze():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    points.freeze()
    points.click(x=30, y=60)
    assert len(ax.lines) == 1
    points.start()
    points.click(x=30, y=60)
    assert len(ax.lines) == 2


def test_points_clear():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    assert to_hex(ax.lines[0].get_color()) == to_hex("C0")
    points.click(x=25, y=55)
    assert len(ax.lines) == 2
    assert to_hex(ax.lines[1].get_color()) == to_hex("C1")
    points.clear()
    assert len(ax.lines) == 0
    points.click(x=30, y=60)
    assert len(ax.lines) == 1
    assert to_hex(ax.lines[0].get_color()) == to_hex("C2")


def test_points_reset():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    points.click(x=25, y=55)
    assert len(ax.lines) == 2
    assert to_hex(ax.lines[0].get_color()) == to_hex("C0")
    assert to_hex(ax.lines[1].get_color()) == to_hex("C1")
    points.reset()
    assert len(ax.lines) == 0
    points.click(x=21, y=40)
    assert to_hex(ax.lines[0].get_color()) == to_hex("C0")


def test_points_shutdown():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    points.shutdown()
    assert len(ax.lines) == 0
    points.click(x=30, y=60)
    assert len(ax.lines) == 0

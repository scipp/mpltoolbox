# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

import mpltoolbox as tbx


def test_vspans_creation():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80]
    vspans.click(x=x[0], y=0)  # first vertical line
    vspans.click(x=x[1], y=0)  # second vertical line
    assert len(ax.patches) == 1
    p = ax.patches[0]
    xy = p.get_xy()
    # In older versions of MPL, xy was a 2D array with all vertices of the patch
    if not isinstance(xy, tuple):
        width = xy[:, 0].max() - xy[:, 0].min()
        xy = xy[0]
    else:
        width = p.get_width()
    assert xy[0] == x[0]
    assert width == x[1] - x[0]

    x = [30, 40]
    vspans.click(x=x[0], y=0)  # first vertical line
    vspans.click(x=x[1], y=0)  # second vertical line
    assert len(ax.patches) == 2
    p = ax.patches[1]
    xy = p.get_xy()
    # In older versions of MPL, xy was a 2D array with all vertices of the patch
    if not isinstance(xy, tuple):
        width = xy[:, 0].max() - xy[:, 0].min()
        xy = xy[0]
    else:
        width = p.get_width()
    assert xy[0] == x[0]
    assert width == x[1] - x[0]


def test_vspans_calls_on_create():
    _, ax = plt.subplots()

    my_event_list = []

    def on_create(event):
        my_event_list.append(event)

    vspans = tbx.Vspans(ax=ax, on_create=on_create)
    x = [20, 80]
    vspans.click(x=x[0], y=0)
    assert len(my_event_list) == 0  # only first line, not a full span
    vspans.click(x=x[1], y=0)
    assert len(my_event_list) == 1
    x = [31, 41]
    vspans.click(x=x[0], y=0)
    vspans.click(x=x[1], y=0)
    assert len(my_event_list) == 2


def test_vspans_remove():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80]
    vspans.click(x=x[0], y=0)
    vspans.click(x=x[1], y=0)
    assert len(ax.patches) == 1

    x = [30, 40]
    vspans.click(x=x[0], y=0)
    vspans.click(x=x[1], y=0)
    assert len(ax.patches) == 2

    vspans.remove(0)
    assert len(ax.patches) == 1
    vspans.remove(0)
    assert len(ax.patches) == 0


def test_vspans_calls_on_remove():
    _, ax = plt.subplots()

    my_event_list = []

    def on_remove(artist):
        my_event_list.append(f'Artist {artist} was removed')

    vspans = tbx.Vspans(ax=ax, on_remove=on_remove)
    x = [20, 80]
    vspans.click(x=x[0], y=0)
    vspans.click(x=x[1], y=0)
    assert len(ax.patches) == 1
    assert len(my_event_list) == 0
    vspans.remove(0)
    assert len(ax.patches) == 0
    assert len(my_event_list) == 1


def test_vspans_stop():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    vspans.click(x=20, y=0)
    vspans.click(x=80, y=0)
    assert len(ax.patches) == 1
    vspans.stop()
    vspans.click(x=30, y=0)
    vspans.click(x=40, y=0)
    assert len(ax.patches) == 1


def test_vspans_start():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    vspans.click(x=20, y=0)
    vspans.click(x=80, y=0)
    assert len(ax.patches) == 1
    vspans.stop()
    vspans.start()
    vspans.click(x=30, y=0)
    vspans.click(x=40, y=0)
    assert len(ax.patches) == 2


def test_vspans_freeze():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    vspans.click(x=20, y=0)
    vspans.click(x=80, y=0)
    assert len(ax.patches) == 1
    vspans.freeze()
    vspans.click(x=30, y=0)
    vspans.click(x=40, y=0)
    assert len(ax.patches) == 1
    vspans.start()
    vspans.click(x=30, y=0)
    vspans.click(x=40, y=0)
    assert len(ax.patches) == 2


def test_vspans_clear():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    vspans.click(x=20, y=0)
    vspans.click(x=80, y=0)
    assert len(ax.patches) == 1
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")
    vspans.click(x=25, y=0)
    vspans.click(x=35, y=0)
    assert len(ax.patches) == 2
    assert to_hex(ax.patches[1].get_edgecolor()) == to_hex("C1")
    vspans.clear()
    assert len(ax.patches) == 0
    vspans.click(x=30, y=0)
    vspans.click(x=40, y=0)
    assert len(ax.patches) == 1
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C2")


def test_vspans_reset():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    vspans.click(x=20, y=0)
    vspans.click(x=25, y=0)
    vspans.click(x=30, y=0)
    vspans.click(x=40, y=0)
    assert len(ax.patches) == 2
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")
    assert to_hex(ax.patches[1].get_edgecolor()) == to_hex("C1")
    vspans.reset()
    assert len(ax.patches) == 0
    vspans.click(x=21, y=0)
    vspans.click(x=41, y=0)
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")


def test_vspans_shutdown():
    _, ax = plt.subplots()
    vspans = tbx.Vspans(ax=ax)
    vspans.click(x=20, y=0)
    vspans.click(x=25, y=0)
    assert len(ax.patches) == 1
    vspans.shutdown()
    assert len(ax.patches) == 0
    vspans.click(x=30, y=0)
    vspans.click(x=40, y=0)
    assert len(ax.patches) == 0

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

import mpltoolbox as tbx


def test_hspans_creation():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    assert len(ax.patches) == 0

    y = [20, 80]
    hspans.click(x=0, y=y[0])  # first horizontal line
    hspans.click(x=0, y=y[1])  # second horizontal line
    assert len(ax.patches) == 1
    p = ax.patches[0]
    xy = p.get_xy()
    # In older versions of MPL, xy was a 2D array with all vertices of the patch
    if not isinstance(xy, tuple):
        height = xy[:, 1].max() - xy[:, 1].min()
        xy = xy[0]
    else:
        height = p.get_height()
    assert xy[1] == y[0]
    assert height == y[1] - y[0]

    y = [30, 40]
    hspans.click(x=0, y=y[0])  # first horizontal line
    hspans.click(x=0, y=y[1])  # second horizontal line
    assert len(ax.patches) == 2
    p = ax.patches[1]
    xy = p.get_xy()
    # In older versions of MPL, xy was a 2D array with all vertices of the patch
    if not isinstance(xy, tuple):
        height = xy[:, 1].max() - xy[:, 1].min()
        xy = xy[0]
    else:
        height = p.get_height()
    assert xy[1] == y[0]
    assert height == y[1] - y[0]


def test_hspans_calls_on_create():
    _, ax = plt.subplots()

    my_event_list = []

    def on_create(event):
        my_event_list.append(event)

    hspans = tbx.Hspans(ax=ax, on_create=on_create)
    y = [20, 80]
    hspans.click(x=0, y=y[0])
    assert len(my_event_list) == 0  # only first line, not a full span
    hspans.click(x=0, y=y[1])
    assert len(my_event_list) == 1
    y = [31, 41]
    hspans.click(x=0, y=y[0])
    hspans.click(x=0, y=y[1])
    assert len(my_event_list) == 2


def test_hspans_remove():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    assert len(ax.patches) == 0

    y = [20, 80]
    hspans.click(x=0, y=y[0])
    hspans.click(x=0, y=y[1])
    assert len(ax.patches) == 1

    y = [30, 40]
    hspans.click(x=0, y=y[0])
    hspans.click(x=0, y=y[1])
    assert len(ax.patches) == 2

    hspans.remove(0)
    assert len(ax.patches) == 1
    hspans.remove(0)
    assert len(ax.patches) == 0


def test_hspans_calls_on_remove():
    _, ax = plt.subplots()

    my_event_list = []

    def on_remove(artist):
        my_event_list.append(f'Artist {artist} was removed')

    hspans = tbx.Hspans(ax=ax, on_remove=on_remove)
    y = [20, 80]
    hspans.click(x=0, y=y[0])
    hspans.click(x=0, y=y[1])
    assert len(ax.patches) == 1
    assert len(my_event_list) == 0

    hspans.remove(0)
    assert len(ax.patches) == 0
    assert len(my_event_list) == 1


def test_hspans_stop():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    hspans.click(x=0, y=50)
    hspans.click(x=0, y=70)
    assert len(ax.patches) == 1
    hspans.stop()
    hspans.click(x=0, y=60)
    hspans.click(x=0, y=80)
    assert len(ax.patches) == 1


def test_hspans_start():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    hspans.click(x=0, y=50)
    hspans.click(x=0, y=70)
    assert len(ax.patches) == 1
    hspans.stop()
    hspans.start()
    hspans.click(x=0, y=60)
    hspans.click(x=0, y=80)
    assert len(ax.patches) == 2


def test_hspans_freeze():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    hspans.click(x=0, y=50)
    hspans.click(x=0, y=70)
    assert len(ax.patches) == 1
    hspans.freeze()
    hspans.click(x=0, y=60)
    hspans.click(x=0, y=80)
    assert len(ax.patches) == 1
    hspans.start()
    hspans.click(x=0, y=60)
    hspans.click(x=0, y=80)
    assert len(ax.patches) == 2


def test_hspans_clear():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    hspans.click(x=0, y=50)
    hspans.click(x=0, y=70)
    assert len(ax.patches) == 1
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")
    hspans.click(x=0, y=55)
    hspans.click(x=0, y=75)
    assert len(ax.patches) == 2
    assert to_hex(ax.patches[1].get_edgecolor()) == to_hex("C1")
    hspans.clear()
    assert len(ax.patches) == 0
    hspans.click(x=0, y=60)
    hspans.click(x=0, y=80)
    assert len(ax.patches) == 1
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C2")


def test_hspans_reset():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    hspans.click(x=0, y=50)
    hspans.click(x=0, y=55)
    hspans.click(x=0, y=60)
    hspans.click(x=0, y=80)
    assert len(ax.patches) == 2
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")
    assert to_hex(ax.patches[1].get_edgecolor()) == to_hex("C1")
    hspans.reset()
    assert len(ax.patches) == 0
    hspans.click(x=0, y=40)
    hspans.click(x=0, y=60)
    assert to_hex(ax.patches[0].get_edgecolor()) == to_hex("C0")


def test_hspans_shutdown():
    _, ax = plt.subplots()
    hspans = tbx.Hspans(ax=ax)
    hspans.click(x=0, y=50)
    hspans.click(x=0, y=55)
    assert len(ax.patches) == 1
    hspans.shutdown()
    assert len(ax.patches) == 0
    hspans.click(x=0, y=60)
    hspans.click(x=0, y=80)
    assert len(ax.patches) == 0

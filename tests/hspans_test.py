# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt

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
    assert xy[1] == y[0]
    assert p.get_height() == y[1] - y[0]

    y = [30, 40]
    hspans.click(x=0, y=y[0])  # first horizontal line
    hspans.click(x=0, y=y[1])  # second horizontal line
    assert len(ax.patches) == 2
    p = ax.patches[1]
    xy = p.get_xy()
    assert xy[1] == y[0]
    assert p.get_height() == y[1] - y[0]


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

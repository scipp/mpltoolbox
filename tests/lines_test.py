# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np

import mpltoolbox as tbx


def test_lines_creation():
    _, ax = plt.subplots()
    lines = tbx.Lines(ax=ax, n=2)
    assert len(ax.lines) == 0

    x = [20, 80]
    y = [40, 70]
    lines.click(x=x[0], y=y[0])  # first line vertex
    lines.click(x=x[1], y=y[1])  # second line vertex
    assert len(ax.lines) == 1
    data = ax.lines[0].get_xydata()
    assert data.shape == (2, 2)
    assert np.allclose(data[:, 0], x)
    assert np.allclose(data[:, 1], y)

    x = [30, 40]
    y = [10, 90]
    lines.click(x=x[0], y=y[0])  # first line vertex
    lines.click(x=x[1], y=y[1])  # second line vertex
    assert len(ax.lines) == 2
    data = ax.lines[1].get_xydata()
    assert np.allclose(data[:, 0], x)
    assert np.allclose(data[:, 1], y)


def test_lines_creation_3_vertices():
    _, ax = plt.subplots()
    lines = tbx.Lines(ax=ax, n=3)
    assert len(ax.lines) == 0

    x = [20, 60, 80]
    y = [40, 70, 10]
    for xx, yy in zip(x, y, strict=True):
        lines.click(x=xx, y=yy)
    assert len(ax.lines) == 1
    data = ax.lines[0].get_xydata()
    assert data.shape == (3, 2)
    assert np.allclose(data[:, 0], x)
    assert np.allclose(data[:, 1], y)


def test_lines_calls_on_create():
    _, ax = plt.subplots()

    my_event_list = []

    def on_create(event):
        my_event_list.append(event)

    lines = tbx.Lines(ax=ax, n=2, on_create=on_create)
    x = [20, 80]
    y = [40, 70]
    lines.click(x=x[0], y=y[0])  # first line vertex
    assert len(my_event_list) == 0
    lines.click(x=x[1], y=y[1])  # second line vertex
    assert len(ax.lines) == 1
    assert len(my_event_list) == 1


def test_lines_remove():
    _, ax = plt.subplots()
    lines = tbx.Lines(ax=ax, n=2)
    assert len(ax.lines) == 0

    x = [20, 80]
    y = [40, 70]
    lines.click(x=x[0], y=y[0])  # first line vertex
    lines.click(x=x[1], y=y[1])  # second line vertex
    assert len(ax.lines) == 1

    x = [30, 40]
    y = [10, 90]
    lines.click(x=x[0], y=y[0])  # first line vertex
    lines.click(x=x[1], y=y[1])  # second line vertex
    assert len(ax.lines) == 2

    lines.remove(0)
    assert len(ax.lines) == 1
    lines.remove(0)
    assert len(ax.lines) == 0


def test_lines_calls_on_remove():
    _, ax = plt.subplots()

    my_event_list = []

    def on_remove(artist):
        my_event_list.append(f'Artist {artist} was removed')

    lines = tbx.Lines(ax=ax, n=2, on_remove=on_remove)
    x = [20, 80]
    y = [40, 70]
    lines.click(x=x[0], y=y[0])  # first line vertex
    lines.click(x=x[1], y=y[1])  # second line vertex
    assert len(ax.lines) == 1
    assert len(my_event_list) == 0
    lines.remove(0)
    assert len(ax.lines) == 0
    assert len(my_event_list) == 1

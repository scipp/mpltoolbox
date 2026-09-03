# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import pytest
from matplotlib.backend_bases import MouseButton
from matplotlib.colors import to_hex

import mpltoolbox as tbx


def test_points_creation():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    points = tbx.Points(ax=ax)
    assert len(ax.lines) == 0

    x = [20.5, 77.1]
    y = [44.3, 70.0]
    points.click(x=x[0], y=y[0])
    assert len(ax.lines) == 1
    data = ax.lines[0].get_xydata()
    assert data.shape == (1, 2)
    assert data[0, 0] == pytest.approx(x[0])
    assert data[0, 1] == pytest.approx(y[0])

    points.click(x=x[1], y=y[1])
    assert len(ax.lines) == 2
    data = ax.lines[1].get_xydata()
    assert data[0, 0] == pytest.approx(x[1])
    assert data[0, 1] == pytest.approx(y[1])


def test_points_calls_on_create():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))

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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))

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


def test_click_processes_canvas_press_pick_and_release_events():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    mouse_events = []
    pick_events = []
    ax.figure.canvas.mpl_connect('button_press_event', mouse_events.append)
    ax.figure.canvas.mpl_connect('motion_notify_event', mouse_events.append)
    ax.figure.canvas.mpl_connect('button_release_event', mouse_events.append)
    ax.figure.canvas.mpl_connect('pick_event', pick_events.append)

    points.click(x=20, y=50, button=MouseButton.MIDDLE)

    assert [event.name for event in mouse_events] == [
        'button_press_event',
        'button_release_event',
    ]
    assert len(pick_events) == 1
    press, release = mouse_events
    assert pick_events[0].mouseevent is press
    assert press.button is MouseButton.MIDDLE
    assert release.button is MouseButton.MIDDLE
    assert (release.x, release.y) == (press.x, press.y)
    assert release.xdata == pytest.approx(press.xdata)
    assert release.ydata == pytest.approx(press.ydata)


def test_click_outside_axes_does_not_create_point():
    _, ax = plt.subplots()
    points = tbx.Points(ax=ax)

    points.click(x=20, y=50)

    assert points.children == []


def test_points_middle_click_with_log_scale():
    _, ax = plt.subplots()
    ax.set(xlim=(1, 100), ylim=(-100, 200))
    ax.set_xscale('log')
    points = tbx.Points(ax=ax)
    points.click(x=10, y=1)
    assert len(points.children) == 1

    points.click(x=10, y=1, button=MouseButton.MIDDLE)

    assert len(points.children) == 0


def test_points_stop():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    points.stop()
    points.click(x=30, y=60)
    assert len(ax.lines) == 1


def test_points_start():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    points.stop()
    points.start()
    points.click(x=30, y=60)
    assert len(ax.lines) == 2


def test_points_freeze():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    points = tbx.Points(ax=ax)
    points.click(x=20, y=50)
    assert len(ax.lines) == 1
    points.shutdown()
    assert len(ax.lines) == 0
    points.click(x=30, y=60)
    assert len(ax.lines) == 0

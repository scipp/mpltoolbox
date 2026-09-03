# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import pytest
from matplotlib.backend_bases import MouseButton
from matplotlib.colors import to_hex

import mpltoolbox as tbx


def test_rectangles_creation():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    rects = tbx.Rectangles(ax=ax)
    assert len(ax.patches) == 0

    x = [20, 80]
    y = [40, 70]
    rects.click(x=x[0], y=y[0])  # first corner
    rects.click(x=x[1], y=y[1])  # second corner
    assert len(ax.patches) == 1
    p = ax.patches[0]
    xy = p.get_xy()
    assert xy == pytest.approx((x[0], y[0]))
    assert p.get_width() == pytest.approx(x[1] - x[0])
    assert p.get_height() == pytest.approx(y[1] - y[0])

    x = [30, 40]
    y = [10, 90]
    rects.click(x=x[0], y=y[0])  # first corner
    rects.click(x=x[1], y=y[1])  # second corner
    assert len(ax.patches) == 2
    p = ax.patches[1]
    xy = p.get_xy()
    assert xy == pytest.approx((x[0], y[0]))
    assert p.get_width() == pytest.approx(x[1] - x[0])
    assert p.get_height() == pytest.approx(y[1] - y[0])


def test_rectangles_calls_on_create():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))

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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))

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


def test_rectangles_middle_click_outside_rectangle_does_not_remove():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    removed = []
    rects = tbx.Rectangles(ax=ax, on_remove=removed.append)
    rects.click(x=1, y=1)
    rects.click(x=5, y=5)
    assert len(rects.children) == 1

    rects.click(x=3, y=-3, button=MouseButton.MIDDLE)

    assert len(rects.children) == 1
    assert len(ax.patches) == 1
    assert removed == []


def test_rectangles_middle_click_respects_enable_remove():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    rects = tbx.Rectangles(ax=ax, enable_remove=False)
    rects.click(x=1, y=1)
    rects.click(x=5, y=5)
    assert len(rects.children) == 1

    rects.click(x=3, y=3, button=MouseButton.MIDDLE)

    assert len(rects.children) == 1
    assert len(ax.patches) == 1


def test_rectangles_ctrl_left_click_removes_rectangle():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=1, y=1)
    rects.click(x=5, y=5)
    assert len(rects.children) == 1

    rects.click(x=3, y=3, modifiers=['ctrl'])

    assert len(rects.children) == 0
    assert len(ax.patches) == 0


def test_rectangles_right_click_presses_and_releases_rectangle():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    pressed = []
    released = []
    rects = tbx.Rectangles(
        ax=ax, on_drag_press=pressed.append, on_drag_release=released.append
    )
    rects.click(x=1, y=1)
    rects.click(x=5, y=5)
    rectangle = rects.children[0]

    rects.click(x=3, y=3, button=MouseButton.RIGHT)

    assert pressed == [rectangle]
    assert released == [rectangle]


def test_rectangles_left_click_presses_and_releases_vertex():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    pressed = []
    released = []
    rects = tbx.Rectangles(
        ax=ax, on_vertex_press=pressed.append, on_vertex_release=released.append
    )
    rects.click(x=1, y=1)
    rects.click(x=5, y=5)
    rectangle = rects.children[0]

    rects.click(x=1, y=1, button=MouseButton.LEFT)

    assert pressed == [rectangle]
    assert released == [rectangle]


def test_click_and_drag_moves_rectangle():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    pressed = []
    moved = []
    released = []
    rects = tbx.Rectangles(
        ax=ax,
        on_drag_press=pressed.append,
        on_drag_move=moved.append,
        on_drag_release=released.append,
    )
    rects.click(x=1, y=1)
    rects.click(x=5, y=5)
    rectangle = rects.children[0]
    events = []
    for name in (
        'button_press_event',
        'motion_notify_event',
        'button_release_event',
    ):
        ax.figure.canvas.mpl_connect(name, events.append)

    rects.click_and_drag(start=(3, 3), end=(5, 7), button=MouseButton.RIGHT)

    assert rectangle.xy == pytest.approx((3, 5))
    assert pressed == [rectangle]
    assert moved == [rectangle]
    assert released == [rectangle]
    assert [event.name for event in events] == [
        'button_press_event',
        'motion_notify_event',
        'button_release_event',
    ]
    press, motion, release = events
    assert (press.xdata, press.ydata) == pytest.approx((3, 3))
    assert (motion.xdata, motion.ydata) == pytest.approx((5, 7))
    assert (release.xdata, release.ydata) == pytest.approx((5, 7))
    assert press.button is MouseButton.RIGHT
    assert motion.button is MouseButton.RIGHT
    assert release.button is MouseButton.RIGHT
    if hasattr(motion, 'buttons'):
        assert motion.buttons == {MouseButton.RIGHT}


def test_click_and_drag_moves_rectangle_vertex():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=1, y=1)
    rects.click(x=5, y=5)
    rectangle = rects.children[0]

    rects.click_and_drag(start=(1, 1), end=(0, -1), button=MouseButton.LEFT)

    assert rectangle.xy == pytest.approx((0, -1))
    assert rectangle.width == pytest.approx(5)
    assert rectangle.height == pytest.approx(6)


def test_rectangles_stop():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=80, y=70)
    assert len(ax.patches) == 1
    rects.stop()
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    rects.click(x=50, y=60, button=MouseButton.MIDDLE)
    assert len(ax.patches) == 0


def test_rectangles_start():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=80, y=70)
    assert len(ax.patches) == 1
    rects.freeze()
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    rects.click(x=50, y=60, button=MouseButton.MIDDLE)
    assert len(ax.patches) == 1
    rects.start()
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 2


def test_rectangles_clear():
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
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
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    rects = tbx.Rectangles(ax=ax)
    rects.click(x=20, y=50)
    rects.click(x=25, y=55)
    assert len(ax.patches) == 1
    rects.shutdown()
    assert len(ax.patches) == 0
    rects.click(x=30, y=60)
    rects.click(x=40, y=80)
    assert len(ax.patches) == 0

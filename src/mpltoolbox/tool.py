# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from functools import partial
from typing import Any

from matplotlib.backend_bases import Event
from matplotlib.pyplot import Axes

from .event import DummyEvent


class Tool:
    """
    A tool for creating and manipulating artists on a matplotlib figure.
    This is the base class for all tools in mpltoolbox.

    :param ax: The axes to which the tool is attached.
    :param spawner: An object constructor that creates the artists.
    :param autostart: If `True`, the tool is activated immediately.
    :param on_create: A function to be called when a new artist is created.
    :param on_remove: A function to be called when an artist is removed.
    :param on_change: A function to be called when an artist is changed.
    :param on_vertex_press: A function to be called when a vertex is pressed.
    :param on_vertex_move: A function to be called when a vertex is moved.
    :param on_vertex_release: A function to be called when a vertex is released.
    :param on_drag_press: A function to be called when an artist is dragged.
    :param on_drag_move: A function to be called when an artist is moved.
    :param on_drag_release: A function to be called when an artist is released.
    :param enable_drag: If `True`, dragging the artists is enabled.
        If `'xonly'` or `'yonly'`, dragging is restricted to the x or y direction,
        respectively. If `False`, dragging is disabled.
    :param enable_remove: If `True`, removing the artists is enabled.
    :param enable_vertex_move: If `True`, moving the vertices of the artists is
        enabled. If `'xonly'` or `'yonly'`, moving is restricted to the x or y
        direction, respectively. If `False`, moving vertices is disabled.
    :param kwargs: Additional keyword arguments for the artist constructor.
    """

    def __init__(
        self,
        ax: Axes,
        spawner,
        *,
        autostart: bool = True,
        on_create: Callable | None = None,
        on_remove: Callable | None = None,
        on_change: Callable | None = None,
        on_vertex_press: Callable | None = None,
        on_vertex_move: Callable | None = None,
        on_vertex_release: Callable | None = None,
        on_drag_press: Callable | None = None,
        on_drag_move: Callable | None = None,
        on_drag_release: Callable | None = None,
        enable_drag: bool | str = True,
        enable_remove: bool | str = True,
        enable_vertex_move: bool | str = True,
        **kwargs,
    ):
        self._ax = ax
        self._fig = ax.get_figure()
        self._connections = {}

        self._enable_drag = enable_drag
        self._enable_remove = enable_remove
        self._enable_vertex_move = enable_vertex_move

        self._on_create = []
        self._on_remove = []
        self._on_change = []
        self._on_vertex_press = []
        self._on_vertex_move = []
        self._on_vertex_release = []
        self._on_drag_press = []
        self._on_drag_move = []
        self._on_drag_release = []

        self.on_create(on_create)
        self.on_remove(on_remove)
        self.on_change(on_change)
        self.on_vertex_press(on_vertex_press)
        self.on_vertex_move(on_vertex_move)
        self.on_vertex_release(on_vertex_release)
        self.on_drag_press(on_drag_press)
        self.on_drag_move(on_drag_move)
        self.on_drag_release(on_drag_release)

        self._kwargs = kwargs
        self._owner_counter = 0

        self._spawner = spawner
        self.children = []
        self._drag_patch = False
        self._grabbed_child = None
        self._grab_mouse_origin = None
        self._grabbed_artist_origin = None
        self._pick_lock = False
        self._nclicks = 0

        if autostart:
            self.start()

    def __del__(self):
        self.shutdown()

    def on_create(self, func: Callable):
        if func is not None:
            self._on_create.append(func)

    def call_on_create(self, event: Event):
        for func in self._on_create:
            func(event)

    def on_remove(self, func: Callable):
        if func is not None:
            self._on_remove.append(func)

    def call_on_remove(self, event: Event):
        for func in self._on_remove:
            func(event)

    def on_change(self, func: Callable):
        if func is not None:
            self._on_change.append(func)

    def call_on_change(self, event: Event):
        for func in self._on_change:
            func(event)

    def on_vertex_press(self, func: Callable):
        if func is not None:
            self._on_vertex_press.append(func)

    def call_on_vertex_press(self, event: Event):
        for func in self._on_vertex_press:
            func(event)

    def on_vertex_move(self, func: Callable):
        if func is not None:
            self._on_vertex_move.append(func)

    def call_on_vertex_move(self, event: Event):
        for func in self._on_vertex_move:
            func(event)

    def on_vertex_release(self, func: Callable):
        if func is not None:
            self._on_vertex_release.append(func)

    def call_on_vertex_release(self, event: Event):
        for func in self._on_vertex_release:
            func(event)

    def on_drag_press(self, func: Callable):
        if func is not None:
            self._on_drag_press.append(func)

    def call_on_drag_press(self, event: Event):
        for func in self._on_drag_press:
            func(event)

    def on_drag_move(self, func: Callable):
        if func is not None:
            self._on_drag_move.append(func)

    def call_on_drag_move(self, event: Event):
        for func in self._on_drag_move:
            func(event)

    def on_drag_release(self, func: Callable):
        if func is not None:
            self._on_drag_release.append(func)

    def call_on_drag_release(self, event: Event):
        for func in self._on_drag_release:
            func(event)

    def _parse_kwargs(self):
        parsed = {}
        for key, value in self._kwargs.items():
            if callable(value):
                parsed[key] = value()
            elif isinstance(value, list):
                parsed[key] = value[self._artist_counter % len(value)]
            else:
                parsed[key] = value
        return parsed

    def _draw(self):
        self._fig.canvas.draw_idle()

    def start(self):
        """
        Activate the tool.
        """
        self._connections["button_press_event"] = self._fig.canvas.mpl_connect(
            "button_press_event", self._on_button_press
        )
        if "pick_event" not in self._connections:
            self._connections["pick_event"] = self._fig.canvas.mpl_connect(
                "pick_event", self._on_pick
            )
        for child in self.children:
            child._vertices.set_visible(True)

    def stop(self):
        """
        Deactivate adding new children, but resizing and moving existing children is
        still possible.
        """
        self._disconnect(
            [key for key in self._connections.keys() if key != "pick_event"]
        )

    def freeze(self):
        """
        Deactivate the tool but keep the children. No new children can be added and
        existing children cannot be moved or resized.
        """
        self._disconnect(list(self._connections.keys()))
        for child in self.children:
            child._vertices.set_visible(False)

    def clear(self):
        """
        Remove all children from the axes.
        """
        for a in self.children:
            a.remove()
        self.children.clear()
        self._draw()

    def shutdown(self):
        """
        Deactivate the tool and remove all children from the axes.
        """
        self.stop()
        self._connections.clear()
        self.clear()

    def _get_active_tool(self) -> str:
        return self._fig.canvas.toolbar.mode

    def _locked_by_other_tool(self) -> bool:
        return getattr(self._ax, "_mpltoolbox_lock", False)

    def _disconnect(self, keys: list[str]):
        for key in keys:
            if key in self._connections:
                self._fig.canvas.mpl_disconnect(self._connections[key])
                del self._connections[key]

    def _connect(self, connections: dict):
        for key, func in connections.items():
            self._connections[key] = self._fig.canvas.mpl_connect(key, func)

    def _on_button_press(self, event: Event):
        if (
            event.button != 1
            or self._pick_lock
            or self._get_active_tool()
            or self._locked_by_other_tool()
            or event.modifiers
            or event.inaxes != self._ax
        ):
            return
        if "motion_notify_event" not in self._connections:
            self._nclicks = 0
            self._spawn_new_owner(x=event.xdata, y=event.ydata)
            self._connect({"motion_notify_event": self._on_motion_notify})
        self._nclicks += 1
        self._persist_vertex(event=event, owner=self.children[-1])

    def _spawn_new_owner(self, x: float, y: float):
        owner = self._spawner(
            x=x, y=y, number=self._owner_counter, ax=self._ax, **self._kwargs
        )
        self.children.append(owner)
        self._owner_counter += 1
        self._draw()

    def _on_motion_notify(self, event: Event):
        self._move_vertex(event=event, ind=None, owner=self.children[-1])

    def _move_vertex(
        self,
        event: Event,
        ind: int,
        owner: Any,
        move_x: bool = True,
        move_y: bool = True,
    ):
        if event.inaxes != self._ax:
            return
        owner.move_vertex(event=event, ind=ind, move_x=move_x, move_y=move_y)
        self._draw()

    def _persist_vertex(self, event: Event, owner):
        if self._nclicks == owner._max_clicks:
            self._disconnect(["motion_notify_event"])
            self._finalize_owner()
        else:
            owner.after_persist_vertex(event)
        self._draw()

    def _finalize_owner(self):
        child = self.children[-1]
        child.set_picker(5.0)
        if self.on_create is not None:
            self.call_on_create(child)

    def _on_pick(self, event: Event):
        mev = event.mouseevent
        if (
            self._get_active_tool()
            or event.artist.parent not in self.children
            or mev.inaxes != self._ax
        ):
            return
        art = event.artist
        if (mev.button == 1) and ("ctrl" not in mev.modifiers):
            if (not art.parent.is_moveable(art)) or (not self._enable_vertex_move):
                return
            self._pick_lock = True
            self._ax._mpltoolbox_lock = True
            self._grab_vertex(event)
        if mev.button == 3:
            if (not art.parent.is_draggable(art)) or (not self._enable_drag):
                return
            self._pick_lock = True
            self._grab_owner(event)
        if (mev.button == 2) or ((mev.button == 1) and ("ctrl" in mev.modifiers)):
            if (not art.parent.is_removable(art)) or (not self._enable_remove):
                return
            self._remove_owner(art.parent)

    def _remove_owner(self, owner):
        owner.remove()
        self.children.remove(owner)
        self._draw()
        if self.on_remove is not None:
            self.call_on_remove(owner)

    def _grab_vertex(self, event: Event):
        self._connect(
            {
                "motion_notify_event": self._on_vertex_motion,
                "button_release_event": partial(self._release_owner, kind="vertex"),
            }
        )
        self._moving_vertex_index = event.ind[0]
        self._moving_vertex_owner = event.artist.parent
        if self.on_vertex_press is not None:
            self.call_on_vertex_press(self._moving_vertex_owner)

    def _on_vertex_motion(self, event: Event):
        # We only lock vertex movement here because we do not want to restrict x/y
        # motion while the artist is being created, only when moving an existing vertex.
        move_x = self._enable_vertex_move in (True, "xonly")
        move_y = self._enable_vertex_move in (True, "yonly")
        self._move_vertex(
            event=event,
            ind=self._moving_vertex_index,
            owner=self._moving_vertex_owner,
            move_x=move_x,
            move_y=move_y,
        )
        if self.on_vertex_move is not None:
            self.call_on_vertex_move(self._moving_vertex_owner)
        if self.on_change is not None:
            self.call_on_change(self._moving_vertex_owner)

    def _grab_owner(self, event: Event):
        self._connect(
            {
                "motion_notify_event": self._move_owner,
                "button_release_event": partial(self._release_owner, kind="drag"),
            }
        )
        self._grabbed_owner = event.artist.parent
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grabbed_owner_origin = self._grabbed_owner.xy
        if self.on_drag_press is not None:
            self.call_on_drag_press(self._grabbed_owner)

    def _move_owner(self, event: Event):
        if event.inaxes != self._ax:
            return
        move_x = self._enable_drag in (True, "xonly")
        move_y = self._enable_drag in (True, "yonly")
        dx = (event.xdata - self._grab_mouse_origin[0]) if move_x else 0
        dy = (event.ydata - self._grab_mouse_origin[1]) if move_y else 0
        self._grabbed_owner.xy = (
            self._grabbed_owner_origin[0] + dx,
            self._grabbed_owner_origin[1] + dy,
        )
        self._draw()
        if self.on_drag_move is not None:
            self.call_on_drag_move(self._grabbed_owner)
        if self.on_change is not None:
            self.call_on_change(self._grabbed_owner)

    def _release_owner(self, event: Event, kind: str):
        self._disconnect(["motion_notify_event", "button_release_event"])
        self._pick_lock = False
        self._ax._mpltoolbox_lock = False
        if (kind == "vertex") and (self.on_vertex_release is not None):
            self.call_on_vertex_release(self._moving_vertex_owner)
        elif (kind == "drag") and (self.on_drag_release is not None):
            self.call_on_drag_release(self._grabbed_owner)

    def click(
        self,
        x: float | tuple[float, float],
        y: float | None = None,
        *,
        button: int = 1,
        modifiers: list[str] | None = None,
    ):
        """
        Simulate a click on the figure.

        :param x: If only a float is given: the x coordinate for the click event. If a
            tuple of length 2 is given, it contains both the x and y coordinates for
            the event.
        :param y: The y coordinate for the event. Can be `None` if `x` is a tuple of
            length 2.
        :param button: 1 is for left-click, 2 is for middle-click, 3 is for
            right-click.
        :param modifiers: A list of modifier keys that were pressed during the click.
        """
        if y is None:
            y = x[1]
            x = x[0]
        ev = DummyEvent(
            xdata=x, ydata=y, inaxes=self._ax, button=button, modifiers=modifiers
        )
        if "motion_notify_event" in self._connections:
            self._on_motion_notify(ev)
        self._on_button_press(ev)

    def remove(self, child):
        """
        Remove an artist from the figure.

        :param child: The item to be removed. Can be supplied as:

            - an integer, in which case the artist with the corresponding position in
                the list of children will be removed
            - an artist (using `tool.children` will give a list of all artists the tool
                is responsible for)
            - a string, which should be the `id` (uuid) of the artist to be removed
        """
        if isinstance(child, int):
            self._remove_owner(self.children[child])
        elif isinstance(child, str):
            for c in self.children:
                if c.id == child:
                    self._remove_owner(c)
        else:
            self._remove_owner(child)

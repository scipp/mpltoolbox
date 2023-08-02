# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .event import DummyEvent
from functools import partial
from matplotlib.pyplot import Axes
from matplotlib.backend_bases import Event
from typing import Callable, List, Tuple, Union


class Tool:
    def __init__(
        self,
        ax: Axes,
        spawner,
        *,
        autostart: bool = True,
        on_create: Callable = None,
        on_remove: Callable = None,
        on_change: Callable = None,
        on_vertex_press: Callable = None,
        on_vertex_move: Callable = None,
        on_vertex_release: Callable = None,
        on_drag_press: Callable = None,
        on_drag_move: Callable = None,
        on_drag_release: Callable = None,
        **kwargs
    ):
        self._ax = ax
        self._fig = ax.get_figure()
        self._connections = {}

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
        self._connections["pick_event"] = self._fig.canvas.mpl_connect(
            "pick_event", self._on_pick
        )

    def stop(self):
        """
        Dectivate the tool.
        """
        self._disconnect(list(self._connections.keys()))

    def shutdown(self):
        """
        Deactivate the tool and remove all children from the axes.
        """
        self.stop()
        for a in self.children:
            a.remove()
        self.children.clear()
        self._connections.clear()
        self._draw()

    def _get_active_tool(self) -> str:
        return self._fig.canvas.toolbar.mode

    def _disconnect(self, keys: List[str]):
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
            or event.modifiers
        ):
            return
        if event.inaxes != self._ax:
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

    def _move_vertex(self, event: Event, ind: int, owner):
        if event.inaxes != self._ax:
            return
        owner.move_vertex(event=event, ind=ind)
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
        if self._get_active_tool():
            return
        if mev.inaxes != self._ax:
            return
        art = event.artist
        if (mev.button == 1) and ("ctrl" not in mev.modifiers):
            if not art.parent.is_moveable(art):
                return
            self._pick_lock = True
            self._grab_vertex(event)
            if self.on_vertex_press is not None:
                self.call_on_vertex_press(self._moving_vertex_owner)
        if mev.button == 3:
            if not art.parent.is_draggable(art):
                return
            self._pick_lock = True
            self._grab_owner(event)
            if self.on_drag_press is not None:
                self.call_on_drag_press(self._grabbed_owner)
        if (mev.button == 2) or ((mev.button == 1) and ("ctrl" in mev.modifiers)):
            if not art.parent.is_removable(art):
                return
            self._remove_owner(art.parent)
            if self.on_remove is not None:
                self.call_on_remove(art.parent)

    def _remove_owner(self, owner):
        owner.remove()
        self.children.remove(owner)
        self._draw()

    def _grab_vertex(self, event: Event):
        self._connect(
            {
                "motion_notify_event": self._on_vertex_motion,
                "button_release_event": partial(self._release_owner, kind="vertex"),
            }
        )
        self._moving_vertex_index = event.ind[0]
        self._moving_vertex_owner = event.artist.parent

    def _on_vertex_motion(self, event: Event):
        self._move_vertex(
            event=event, ind=self._moving_vertex_index, owner=self._moving_vertex_owner
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

    def _move_owner(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
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
        if (kind == "vertex") and (self.on_vertex_release is not None):
            self.call_on_vertex_release(self._moving_vertex_owner)
        elif (kind == "drag") and (self.on_drag_release is not None):
            self.call_on_drag_release(self._grabbed_owner)

    def click(
        self,
        x: Union[float, Tuple[float]],
        y: float = None,
        *,
        button: int = 1,
        modifiers: List[str] = None
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

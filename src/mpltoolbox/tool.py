# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)
from matplotlib.pyplot import Artist, Axes
from typing import Callable, List


class Tool:

    def __init__(self,
                 ax: Axes,
                 *,
                 autostart: bool = True,
                 on_create: Callable = None,
                 on_remove: Callable = None,
                 on_vertex_press: Callable = None,
                 on_vertex_move: Callable = None,
                 on_vertex_release: Callable = None,
                 on_drag_press: Callable = None,
                 on_drag_move: Callable = None,
                 on_drag_release: Callable = None,
                 **kwargs):
        self._ax = ax
        self._fig = ax.get_figure()
        self._connections = {}

        self.on_create = on_create
        self.on_remove = on_remove
        self.on_vertex_press = on_vertex_press
        self.on_vertex_move = on_vertex_move
        self.on_vertex_release = on_vertex_release
        self.on_drag_press = on_drag_press
        self.on_drag_move = on_drag_move
        self.on_drag_release = on_drag_release

        self._kwargs = kwargs
        self._artist_counter = 0

        if autostart:
            self.start()

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
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

    def stop(self):
        """
        Dectivate the tool.
        """
        self._disconnect(list(self._connections.keys()))

    def shutdown(self, artists: List[Artist]):
        """
        Deactivate the tool and remove all artists from the axes.
        """
        self.stop()
        for a in artists:
            a.remove()
        del artists, self._connections
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

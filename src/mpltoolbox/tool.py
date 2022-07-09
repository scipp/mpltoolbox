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
                 on_drag_release: Callable = None):
        """
        A generic tool that stores user callbacks and provides
        start/stop/shutdown mechanism.
        """

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

        if autostart:
            self.start()

    def _draw(self):
        self._fig.canvas.draw_idle()

    def start(self):
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

    def stop(self):
        for c in self._connections.values():
            self._fig.canvas.mpl_disconnect(c)

    def shutdown(self, artists: List[Artist]):
        self.stop()
        for a in artists:
            a.remove()
        del artists, self._connections
        self._draw()

    def _get_active_tool(self) -> str:
        return self._fig.canvas.toolbar.get_state()['_current_action']
